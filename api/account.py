import os
from datetime import datetime, date, timedelta
from threading import Lock
from typing import Any, Optional
from uuid import uuid4

import requests
import certifi
from flask_compat import APIRouter, Header
from pydantic import BaseModel, Field

from database import fetch_all, fetch_one, get_conn, jsonb

router = APIRouter()

_auth_schema_lock = Lock()
_auth_schema_ready = False


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


def _ensure_auth_schema() -> None:
    global _auth_schema_ready
    if _auth_schema_ready:
        return

    with _auth_schema_lock:
        if _auth_schema_ready:
            return
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS unionid VARCHAR(100)")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS session_key TEXT")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        token VARCHAR(100) PRIMARY KEY,
                        user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        openid VARCHAR(100) NOT NULL,
                        unionid VARCHAR(100),
                        session_key TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                    """
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_sessions_openid ON user_sessions(openid)"
                )
                cur.execute(
                    "CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at)"
                )
        _auth_schema_ready = True


def _get_openid_by_session_token(token: str) -> Optional[str]:
    _ensure_auth_schema()
    row = fetch_one(
        """
        SELECT openid
        FROM user_sessions
        WHERE token = %s AND expires_at > CURRENT_TIMESTAMP
        LIMIT 1
        """,
        (token,),
    )
    return row.get("openid") if row else None


def get_current_user_id(
    authorization: Optional[str], x_user_id: Optional[str] = None
) -> Optional[str]:
    token = _extract_bearer_token(authorization)
    if token:
        return _get_openid_by_session_token(token)
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()
    return None


def _user_from_row(row: dict[str, Any]) -> dict[str, Any]:
    user_id = row.get("openid") or row.get("user_id") or ""
    return {
        "db_id": row.get("id"),
        "user_id": user_id,
        "nickname": row.get("nickname") or f"骑士{user_id[-4:]}",
        "avatar": row.get("avatar") or "",
        "age": 0,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _env_bool(name: str, default: bool = True) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _wechat_verify_arg() -> bool | str:
    custom_ca = (os.getenv("WECHAT_API_CA_BUNDLE") or "").strip()
    if custom_ca:
        return custom_ca
    if not _env_bool("WECHAT_API_VERIFY_SSL", True):
        return False
    return certifi.where()


def _exchange_code_to_wechat_session(code: str) -> dict[str, str]:
    if os.getenv("WECHAT_AUTH_MOCK") == "1":
        return {
            "openid": f"dev_{code}",
            "session_key": f"mock_session_{code}",
            "unionid": "",
        }

    appid = (
        os.getenv("WECHAT_APPID")
        or os.getenv("WECHAT_MINI_PROGRAM_APPID")
        or os.getenv("WX_APPID")
        or ""
    ).strip()
    secret = (
        os.getenv("WECHAT_APP_SECRET")
        or os.getenv("WECHAT_SECRET")
        or os.getenv("WX_APP_SECRET")
        or ""
    ).strip()

    if not appid or not secret:
        raise ValueError("后端未配置 WECHAT_APPID / WECHAT_APP_SECRET，无法完成微信 code2Session 登录")

    try:
        response = requests.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": appid,
                "secret": secret,
                "js_code": code,
                "grant_type": "authorization_code",
            },
            timeout=8,
            verify=_wechat_verify_arg(),
        )
        response.raise_for_status()
    except requests.exceptions.SSLError as exc:
        raise ValueError(
            "微信 code2Session 证书校验失败：请重新发布云托管镜像以更新 CA 证书；"
            "若仍失败，可临时在云托管环境变量设置 WECHAT_API_VERIFY_SSL=0 后再发布。"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError("微信 code2Session 网络请求失败，请检查云托管网络和微信接口连通性") from exc

    data = response.json()

    errcode = data.get("errcode")
    if errcode:
        raise ValueError(f"微信 code2Session 失败：{errcode} {data.get('errmsg', '')}".strip())

    openid = (data.get("openid") or "").strip()
    session_key = (data.get("session_key") or "").strip()
    unionid = (data.get("unionid") or "").strip()
    if not openid or not session_key:
        raise ValueError("微信 code2Session 未返回 openid 或 session_key")

    return {
        "openid": openid,
        "session_key": session_key,
        "unionid": unionid,
    }


def _upsert_wechat_user(
    openid: str,
    session_key: str,
    unionid: Optional[str] = None,
    nickname: Optional[str] = None,
) -> dict[str, Any]:
    _ensure_auth_schema()
    clean_nickname = (nickname or "").strip() or f"骑士{openid[-4:]}"
    row = fetch_one(
        """
        INSERT INTO users (openid, nickname, avatar, unionid, session_key, last_login_at)
        VALUES (%s, %s, '', %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (openid) DO UPDATE
        SET nickname = CASE
                WHEN EXCLUDED.nickname <> '' THEN EXCLUDED.nickname
                ELSE users.nickname
            END,
            unionid = COALESCE(EXCLUDED.unionid, users.unionid),
            session_key = EXCLUDED.session_key,
            last_login_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id, openid, nickname, avatar, created_at, updated_at
        """,
        (openid, clean_nickname, unionid or None, session_key),
    )
    return _user_from_row(row)


def _create_user_session(
    user: dict[str, Any],
    openid: str,
    session_key: str,
    unionid: Optional[str] = None,
) -> str:
    _ensure_auth_schema()
    token = f"mt_{uuid4().hex}"
    expires_at = datetime.now() + timedelta(days=30)
    fetch_one(
        """
        INSERT INTO user_sessions (token, user_id, openid, unionid, session_key, expires_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING token
        """,
        (token, user["db_id"], openid, unionid or None, session_key, expires_at),
    )
    return token


def _ensure_user(user_id: str, nickname: Optional[str] = None) -> dict[str, Any]:
    clean_user_id = user_id.strip()
    clean_nickname = (nickname or "").strip()

    row = fetch_one(
        """
        SELECT id, openid, nickname, avatar, created_at, updated_at
        FROM users
        WHERE openid = %s
        LIMIT 1
        """,
        (clean_user_id,),
    )
    if row:
        if clean_nickname and clean_nickname != (row.get("nickname") or ""):
            row = fetch_one(
                """
                UPDATE users
                SET nickname = %s, updated_at = CURRENT_TIMESTAMP
                WHERE openid = %s
                RETURNING id, openid, nickname, avatar, created_at, updated_at
                """,
                (clean_nickname, clean_user_id),
            )
        return _user_from_row(row)

    row = fetch_one(
        """
        INSERT INTO users (openid, nickname, avatar)
        VALUES (%s, %s, '')
        RETURNING id, openid, nickname, avatar, created_at, updated_at
        """,
        (clean_user_id, clean_nickname or f"骑士{clean_user_id[-4:]}"),
    )
    return _user_from_row(row)


def _get_user(user_id: str) -> Optional[dict[str, Any]]:
    row = fetch_one(
        """
        SELECT id, openid, nickname, avatar, created_at, updated_at
        FROM users
        WHERE openid = %s
        LIMIT 1
        """,
        (user_id,),
    )
    return _user_from_row(row) if row else None


def _save_user(user_id: str, user: dict[str, Any]) -> dict[str, Any]:
    row = fetch_one(
        """
        UPDATE users
        SET nickname = %s, avatar = %s, updated_at = CURRENT_TIMESTAMP
        WHERE openid = %s
        RETURNING id, openid, nickname, avatar, created_at, updated_at
        """,
        (
            user.get("nickname") or f"骑士{user_id[-4:]}",
            user.get("avatar") or "",
            user_id,
        ),
    )
    return _user_from_row(row)


def get_user_db_id(user_id: str) -> int:
    user = _get_user(user_id) or _ensure_user(user_id=user_id)
    return int(user["db_id"])


def _vehicle_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("item_id") or "",
        "brand": row.get("brand") or "",
        "model": row.get("model") or "",
        "displacement": row.get("displacement") or "",
        "plate_no": row.get("plate_no") or "",
    }


def _equipment_from_row(row: dict[str, Any]) -> dict[str, Any]:
    weight = row.get("weight_kg")
    return {
        "id": row.get("item_id") or "",
        "name": row.get("name") or "",
        "category": row.get("category") or "",
        "weight_kg": float(weight) if weight is not None else None,
        "note": row.get("note") or "",
    }


def _template_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("item_id") or "",
        "title": row.get("title") or "",
        "desc": row.get("description") or "",
        "days": row.get("days") or 1,
        "schedule": row.get("schedule") if isinstance(row.get("schedule"), list) else [],
    }


def _list_user_assets(user_id: str, table: str, mapper) -> list[dict[str, Any]]:
    user_db_id = get_user_db_id(user_id)
    rows = fetch_all(
        f"""
        SELECT *
        FROM {table}
        WHERE user_id = %s
        ORDER BY position ASC, created_at ASC
        """,
        (user_db_id,),
    )
    return [mapper(row) for row in rows]


def _list_vehicles(user_id: str) -> list[dict[str, Any]]:
    return _list_user_assets(user_id, "user_vehicles", _vehicle_from_row)


def _list_equipments(user_id: str) -> list[dict[str, Any]]:
    return _list_user_assets(user_id, "user_equipments", _equipment_from_row)


def _list_templates(user_id: str) -> list[dict[str, Any]]:
    return _list_user_assets(user_id, "user_templates", _template_from_row)


def _list_completed_routes(user_id: str) -> list[dict[str, Any]]:
    try:
        user_db_id = get_user_db_id(user_id)
        rows = fetch_all(
            """
            SELECT *
            FROM routes
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_db_id,),
        )
    except Exception:
        return []

    out: list[dict[str, Any]] = []
    today = date.today()
    for row in rows:
        wp = row.get("waypoints")
        if not isinstance(wp, dict):
            continue
        if wp.get("user_id") != user_id:
            continue
        end_s = wp.get("end_date")
        if isinstance(end_s, str):
            try:
                end_d = date.fromisoformat(end_s)
                if end_d > today:
                    continue
            except Exception:
                continue
        schedule = wp.get("schedule")
        days = len(schedule) if isinstance(schedule, list) else wp.get("estimated_days", 0)
        out.append(
            {
                "route_id": row.get("id"),
                "route_name": row.get("route_name") or "未命名行程",
                "origin_name": row.get("origin_name") or "",
                "dest_name": row.get("dest_name") or "",
                "total_distance": row.get("total_distance") or 0,
                "end_date": end_s,
                "days": days,
            }
        )
    return out


def _replace_user_assets(table: str, user_id: str, rows: list[dict[str, Any]]) -> None:
    user_db_id = get_user_db_id(user_id)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"DELETE FROM {table} WHERE user_id = %s", (user_db_id,))
            if table == "user_vehicles":
                for row in rows:
                    cur.execute(
                        """
                        INSERT INTO user_vehicles (
                            user_id, item_id, brand, model, displacement, plate_no, position
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            user_db_id,
                            row["item_id"],
                            row["brand"],
                            row["model"],
                            row["displacement"],
                            row["plate_no"],
                            row["position"],
                        ),
                    )
            elif table == "user_equipments":
                for row in rows:
                    cur.execute(
                        """
                        INSERT INTO user_equipments (
                            user_id, item_id, name, category, weight_kg, note, position
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            user_db_id,
                            row["item_id"],
                            row["name"],
                            row["category"],
                            row["weight_kg"],
                            row["note"],
                            row["position"],
                        ),
                    )
            elif table == "user_templates":
                for row in rows:
                    cur.execute(
                        """
                        INSERT INTO user_templates (
                            user_id, item_id, title, description, days, schedule, position
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            user_db_id,
                            row["item_id"],
                            row["title"],
                            row["description"],
                            row["days"],
                            jsonb(row["schedule"]),
                            row["position"],
                        ),
                    )
            else:
                raise ValueError(f"Unsupported asset table: {table}")


def _save_vehicles(user_id: str, items: list["VehicleItem"]) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(items):
        brand = item.brand.strip()
        model = item.model.strip()
        if not brand or not model:
            continue
        rows.append(
            {
                "user_id": user_id,
                "item_id": item.id or uuid4().hex,
                "brand": brand,
                "model": model,
                "displacement": (item.displacement or "").strip(),
                "plate_no": (item.plate_no or "").strip(),
                "position": idx,
                "updated_at": _now_iso(),
            }
        )
    _replace_user_assets("user_vehicles", user_id, rows)
    return _list_vehicles(user_id)


def _save_equipments(user_id: str, items: list["EquipmentItem"]) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(items):
        name = item.name.strip()
        if not name:
            continue
        rows.append(
            {
                "user_id": user_id,
                "item_id": item.id or uuid4().hex,
                "name": name,
                "category": (item.category or "").strip(),
                "weight_kg": item.weight_kg,
                "note": (item.note or "").strip(),
                "position": idx,
                "updated_at": _now_iso(),
            }
        )
    _replace_user_assets("user_equipments", user_id, rows)
    return _list_equipments(user_id)


def _save_templates(user_id: str, items: list["MyTemplateItem"]) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(items):
        title = item.title.strip()
        if not title:
            continue
        rows.append(
            {
                "user_id": user_id,
                "item_id": item.id or uuid4().hex,
                "title": title,
                "description": (item.desc or "").strip(),
                "days": max(1, int(item.days or 1)),
                "schedule": item.schedule or [],
                "position": idx,
                "updated_at": _now_iso(),
            }
        )
    _replace_user_assets("user_templates", user_id, rows)
    return _list_templates(user_id)


def _build_profile(user: dict[str, Any]) -> dict[str, Any]:
    user_id = user["user_id"]
    history = _list_completed_routes(user_id)
    cities = set()
    total_distance_km = 0.0
    for item in history:
        if item.get("origin_name"):
            cities.add(item["origin_name"])
        if item.get("dest_name"):
            cities.add(item["dest_name"])
        total_distance_km += float(item.get("total_distance", 0)) / 1000
    return {
        "user_id": user_id,
        "nickname": user.get("nickname", f"骑士{user_id[-4:]}"),
        "avatar": user.get("avatar", ""),
        "age": user.get("age", 0),
        "totalDistance": int(total_distance_km),
        "trips": len(history),
        "cities": len(cities),
        "vehicles": len(_list_vehicles(user_id)),
        "equipments": len(_list_equipments(user_id)),
        "templates": len(_list_templates(user_id)),
    }


class WxLoginRequest(BaseModel):
    code: str = Field(..., min_length=1, description="wx.login 获取到的临时登录凭证 code")
    nickname: Optional[str] = None


class VehicleItem(BaseModel):
    id: str
    brand: str
    model: str
    displacement: Optional[str] = ""
    plate_no: Optional[str] = ""


class EquipmentItem(BaseModel):
    id: str
    name: str
    category: Optional[str] = ""
    weight_kg: Optional[float] = None
    note: Optional[str] = ""


class MyTemplateItem(BaseModel):
    id: str
    title: str
    desc: Optional[str] = ""
    days: int = 1
    schedule: list[dict[str, Any]] = Field(default_factory=list)


class VehiclesPayload(BaseModel):
    items: list[VehicleItem]


class EquipmentsPayload(BaseModel):
    items: list[EquipmentItem]


class TemplatesPayload(BaseModel):
    items: list[MyTemplateItem]


@router.post("/api/v1/auth/wx-login")
def wx_login(payload: WxLoginRequest):
    code = payload.code.strip()
    try:
        wx_session = _exchange_code_to_wechat_session(code)
        openid = wx_session["openid"]
        session_key = wx_session["session_key"]
        unionid = wx_session.get("unionid") or None
        user = _upsert_wechat_user(
            openid=openid,
            unionid=unionid,
            session_key=session_key,
            nickname=payload.nickname,
        )
        token = _create_user_session(
            user=user,
            openid=openid,
            unionid=unionid,
            session_key=session_key,
        )
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

    return {
        "status": "success",
        "data": {
            "token": token,
            "user_id": openid,
            "profile": _build_profile(user),
        },
    }


@router.get("/api/v1/me/profile")
def get_my_profile(authorization: Optional[str] = Header(None), x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    user = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _build_profile(user)}


@router.get("/api/v1/me/vehicles")
def get_my_vehicles(authorization: Optional[str] = Header(None), x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    _ = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _list_vehicles(user_id)}


@router.put("/api/v1/me/vehicles")
def save_my_vehicles(
    payload: VehiclesPayload,
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    _ = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _save_vehicles(user_id, payload.items)}


@router.get("/api/v1/me/equipments")
def get_my_equipments(authorization: Optional[str] = Header(None), x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    _ = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _list_equipments(user_id)}


@router.put("/api/v1/me/equipments")
def save_my_equipments(
    payload: EquipmentsPayload,
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    _ = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _save_equipments(user_id, payload.items)}


@router.get("/api/v1/me/templates")
def get_my_templates(authorization: Optional[str] = Header(None), x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    _ = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _list_templates(user_id)}


@router.put("/api/v1/me/templates")
def save_my_templates(
    payload: TemplatesPayload,
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    _ = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _save_templates(user_id, payload.items)}


@router.get("/api/v1/me/history")
def get_my_history(authorization: Optional[str] = Header(None), x_user_id: Optional[str] = Header(None)):
    user_id = get_current_user_id(authorization, x_user_id)
    if not user_id:
        return {"status": "error", "message": "未登录"}
    _ = _get_user(user_id) or _ensure_user(user_id=user_id)
    return {"status": "success", "data": _list_completed_routes(user_id)}


@router.get("/api/v1/auth/dev-login-random")
def dev_login_random():
    code = uuid4().hex[:8]
    user_id = f"wx_{code}"
    user = _ensure_user(user_id=user_id)
    return {"status": "success", "data": {"token": user_id, "user_id": user_id, "profile": _build_profile(user)}}
