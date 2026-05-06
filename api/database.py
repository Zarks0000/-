import os
import atexit
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from queue import Empty, Full, LifoQueue
from threading import Lock
from typing import Any, Iterable, Optional
from uuid import UUID
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

load_dotenv()
load_dotenv(Path(__file__).with_name(".env"), override=True)
load_dotenv(Path(__file__).with_name(".env.postgres"), override=False)


def _append_query_param(url: str, key: str, value: str) -> str:
    parsed = urlsplit(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if key not in query:
        query[key] = value
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def _database_url() -> str:
    url = (
        os.getenv("SUPABASE_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or ""
    ).strip()
    if url:
        if "supabase" in url.lower() and "sslmode=" not in url.lower():
            return _append_query_param(url, "sslmode", "require")
        return url

    host = (os.getenv("POSTGRES_HOST") or "127.0.0.1").strip()
    port = (os.getenv("POSTGRES_PORT") or "5432").strip()
    db = (os.getenv("POSTGRES_DB") or "").strip()
    user = (os.getenv("POSTGRES_USER") or "").strip()
    password = (os.getenv("POSTGRES_PASSWORD") or "").strip()
    if db and user:
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    raise RuntimeError(
        "Missing DATABASE_URL, or POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD in environment"
    )


def _env_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


_POOL_MIN_SIZE = max(0, _env_int("POSTGRES_POOL_MIN", 1))
_POOL_MAX_SIZE = max(1, _env_int("POSTGRES_POOL_MAX", 8))
_POOL_WAIT_SECONDS = max(1, _env_int("POSTGRES_POOL_WAIT_SECONDS", 5))
_CONNECT_TIMEOUT_SECONDS = max(1, _env_int("POSTGRES_CONNECT_TIMEOUT", 5))

_pool: LifoQueue = LifoQueue(maxsize=_POOL_MAX_SIZE)
_pool_lock = Lock()
_pool_size = 0


def _new_connection():
    return psycopg.connect(
        _database_url(),
        row_factory=dict_row,
        connect_timeout=_CONNECT_TIMEOUT_SECONDS,
    )


def _is_connection_open(conn) -> bool:
    return conn is not None and not conn.closed


def _increase_pool_size() -> bool:
    global _pool_size
    with _pool_lock:
        if _pool_size >= _POOL_MAX_SIZE:
            return False
        _pool_size += 1
        return True


def _decrease_pool_size() -> None:
    global _pool_size
    with _pool_lock:
        _pool_size = max(0, _pool_size - 1)


def _discard_connection(conn) -> None:
    try:
        if conn is not None and not conn.closed:
            conn.close()
    finally:
        _decrease_pool_size()


def _borrow_connection():
    while True:
        try:
            conn = _pool.get_nowait()
        except Empty:
            if _increase_pool_size():
                try:
                    return _new_connection()
                except Exception:
                    _decrease_pool_size()
                    raise

            try:
                conn = _pool.get(timeout=_POOL_WAIT_SECONDS)
            except Empty as exc:
                raise TimeoutError("Timed out waiting for a PostgreSQL connection") from exc

        if _is_connection_open(conn):
            return conn
        _discard_connection(conn)


def _return_connection(conn) -> None:
    if not _is_connection_open(conn):
        _discard_connection(conn)
        return

    try:
        _pool.put_nowait(conn)
    except Full:
        _discard_connection(conn)


@contextmanager
def get_conn():
    conn = _borrow_connection()
    keep_connection = True
    try:
        yield conn
    except Exception:
        try:
            conn.rollback()
        except Exception:
            keep_connection = False
        raise
    else:
        try:
            conn.commit()
        except Exception:
            keep_connection = False
            try:
                conn.rollback()
            except Exception:
                pass
            raise
    finally:
        if keep_connection:
            _return_connection(conn)
        else:
            _discard_connection(conn)


def close_pool() -> None:
    while True:
        try:
            conn = _pool.get_nowait()
        except Empty:
            break
        _discard_connection(conn)


atexit.register(close_pool)


for _ in range(min(_POOL_MIN_SIZE, _POOL_MAX_SIZE)):
    if not _increase_pool_size():
        break
    try:
        _pool.put_nowait(_new_connection())
    except Exception:
        _decrease_pool_size()
        break


def fetch_one(sql: str, params: Optional[Iterable[Any]] = None) -> Optional[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()


def fetch_all(sql: str, params: Optional[Iterable[Any]] = None) -> list[dict[str, Any]]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())


def execute(sql: str, params: Optional[Iterable[Any]] = None) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())


def jsonb(value: Any) -> Jsonb:
    return Jsonb(value)


def jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [jsonable(v) for v in value]
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def jsonable_row(row: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    return jsonable(row) if row is not None else None


def jsonable_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [jsonable(row) for row in rows]
