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


def _fetch_juhe_top_result(key: str) -> tuple[list[dict[str, Any]], Optional[str]]:
    resp = requests.get(
        "http://v.juhe.cn/toutiao/index",
        params={"type": "top", "key": key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json() or {}
    error_code = data.get("error_code")
    if error_code not in (None, 0, "0"):
        return [], str(data.get("reason") or f"聚合数据错误码 {error_code}")

    result = data.get("result") or {}
    items = result.get("data") or []
    return [it for it in items if isinstance(it, dict)], None


def _filter_items_by_keywords(items: list[dict[str, Any]], keywords: list[str], max_total: int) -> list[dict[str, Any]]:
    kws = [k for k in [(x or "").strip() for x in keywords] if k]
    if not kws:
        return []

    matched: list[dict[str, Any]] = []
    for it in items:
        title = (it.get("title") or "").strip()
        content = " ".join(
            str(it.get(k) or "")
            for k in ("content", "description", "author_name", "category")
        )
        haystack = f"{title} {content}"
        if not haystack.strip():
            continue
        if any(k in haystack for k in kws):
            matched.append(it)
        if len(matched) >= max_total:
            break
    return matched


def _dedupe_alerts(alerts: list[dict[str, Any]], max_total: int) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in alerts:
        key = (item.get("url") or item.get("title") or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_total:
            break
    return deduped


def _fetch_news_alerts(keywords: list[str], max_total: int) -> tuple[list[dict[str, Any]], str, str]:
    alerts: list[dict[str, Any]] = []

    juhe_key = _juhe_key()
    if not juhe_key:
        return [], "none", "未配置 NEWS_API_KEY"

    if juhe_key:
        try:
            items, juhe_error = _fetch_juhe_top_result(juhe_key)
            if juhe_error:
                return [], "juhe", juhe_error
            filtered = _filter_items_by_keywords(items, keywords, max_total=max_total)
            alerts.extend(_to_news_item(it) for it in filtered)
            if alerts:
                return _dedupe_alerts(alerts, max_total), "juhe", "聚合数据"
            if items:
                return [], "juhe", "聚合数据有返回，但未命中当前行程关键词"
            return [], "juhe", "聚合数据未返回新闻列表"
        except Exception as exc:
            return [], "juhe", f"聚合数据请求失败: {exc}"

    return [], "none", "未获取到相关新闻"


@router.get("/api/v1/news/alerts")
def get_news_alerts(keyword: str, count: int = 3):
    k = (keyword or "").strip()
    if not k:
        return {"status": "success", "keyword": keyword, "alerts": []}

    max_total = max(1, min(10, count))
    alerts, source, source_detail = _fetch_news_alerts([k], max_total)
    return {"status": "success", "keyword": keyword, "source": source, "source_detail": source_detail, "alerts": alerts}


@router.get("/api/v1/news/route-alerts")
def get_route_news_alerts(origin: str, destination: str, waypoints: Optional[str] = None, count: int = 6):
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
    alerts, source, source_detail = _fetch_news_alerts(keywords, max_total)
    return {
        "status": "success",
        "origin": origin,
        "destination": destination,
        "keywords": keywords,
        "source": source,
        "source_detail": source_detail,
        "alerts": alerts,
    }
