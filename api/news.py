from flask_compat import APIRouter
import os
from typing import Any, Optional

import requests
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()


def _juhe_key() -> Optional[str]:
    key = os.getenv("NEWS_API_KEY")
    if not key:
        return None
    return key.strip() or None


def _to_news_item(item: dict[str, Any]) -> dict[str, Any]:
    title = (item.get("title") or "").strip()
    author = (item.get("author_name") or "").strip()
    date = (item.get("date") or "").strip()
    url = (item.get("url") or "").strip()

    desc = title
    if url:
        desc = f"{title}（详情链接已提供）"

    return {
        "type": "news",
        "severity": "low",
        "title": f"【新闻】{title}" if title else "【新闻】最新资讯",
        "description": desc,
        "source": author or "聚合数据",
        "time": date or "刚刚",
        "url": url or None,
    }


def _normalize_place_tokens(place: str) -> list[str]:
    place = (place or "").strip()
    if not place:
        return []

    tokens: list[str] = []
    tokens.append(place)

    for suffix in ["省", "市", "自治区", "地区", "盟", "州", "县", "区", "旗"]:
        if suffix in place:
            head = place.split(suffix, 1)[0].strip()
            if head:
                tokens.append(head)

    for sep in ["-", "—", "·", " ", "到", "至", "→", "—>", "->", "—＞", "／", "/", ",", "，"]:
        if sep in place:
            for part in [p.strip() for p in place.split(sep) if p.strip()]:
                tokens.extend(_normalize_place_tokens(part))

    dedup: list[str] = []
    seen: set[str] = set()
    for t in tokens:
        if t and t not in seen:
            seen.add(t)
            dedup.append(t)
    return dedup[:10]


def _fetch_juhe_top_items(key: str) -> list[dict[str, Any]]:
    resp = requests.get(
        "http://v.juhe.cn/toutiao/index",
        params={"type": "top", "key": key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json() or {}
    result = data.get("result") or {}
    items = result.get("data") or []
    return [it for it in items if isinstance(it, dict)]


def _filter_items_by_keywords(items: list[dict[str, Any]], keywords: list[str], max_total: int) -> list[dict[str, Any]]:
    kws = [k for k in [(x or "").strip() for x in keywords] if k]
    if not kws:
        return []

    matched: list[dict[str, Any]] = []
    for it in items:
        title = (it.get("title") or "").strip()
        if not title:
            continue
        if any(k in title for k in kws):
            matched.append(it)
        if len(matched) >= max_total:
            break
    return matched


@router.get("/api/v1/news/alerts")
def get_news_alerts(keyword: str, count: int = 3):
    key = _juhe_key()
    if not key:
        return {"status": "success", "keyword": keyword, "alerts": []}

    k = (keyword or "").strip()
    if not k:
        return {"status": "success", "keyword": keyword, "alerts": []}

    try:
        items = _fetch_juhe_top_items(key)
        filtered = _filter_items_by_keywords(items, [k], max_total=max(1, min(10, count)))
        alerts = [_to_news_item(it) for it in filtered]
        return {"status": "success", "keyword": keyword, "alerts": alerts}
    except Exception:
        return {"status": "success", "keyword": keyword, "alerts": []}


@router.get("/api/v1/news/route-alerts")
def get_route_news_alerts(origin: str, destination: str, waypoints: Optional[str] = None, count: int = 6):
    key = _juhe_key()
    if not key:
        return {"status": "success", "alerts": []}

    places: list[str] = []
    places.extend(_normalize_place_tokens(origin))
    places.extend(_normalize_place_tokens(destination))
    if waypoints:
        for w in [s.strip() for s in waypoints.split(",") if s.strip()]:
            places.extend(_normalize_place_tokens(w))

    keywords: list[str] = []
    seen: set[str] = set()
    for p in places:
        if p and p not in seen:
            seen.add(p)
            keywords.append(p)

    max_total = max(1, min(20, count))

    try:
        items = _fetch_juhe_top_items(key)
        filtered = _filter_items_by_keywords(items, keywords, max_total=max_total)
        alerts = [_to_news_item(it) for it in filtered]
        return {
            "status": "success",
            "origin": origin,
            "destination": destination,
            "keywords": keywords,
            "alerts": alerts,
        }
    except Exception:
        return {"status": "success", "origin": origin, "destination": destination, "keywords": keywords, "alerts": []}
