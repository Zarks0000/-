from datetime import date, datetime, timedelta
import os
import uuid
from typing import Any, List, Optional

import requests
from flask_compat import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

from account import get_current_user_id, get_user_db_id
from amap_service import get_driving_route, get_geocode
from database import execute, fetch_all, fetch_one, jsonable_row, jsonb
from llm_service import ask_llm_json

router = APIRouter()


def _env_bool(name: str, default: bool = False) -> bool:
    raw = (os.getenv(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


class Waypoint(BaseModel):
    name: str
    location: str
    stay_days: int = 1


class ScheduleItem(BaseModel):
    day: int
    title: Optional[str] = None
    start_location: Optional[str] = None
    end_location: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    distance_km: Optional[float] = None
    description: Optional[str] = None


class RoutePlanRequest(BaseModel):
    name: str
    origin: str
    destination: str
    start_date: date
    waypoints: Optional[List[Waypoint]] = []
    riding_style: str = "leisure"
    schedule: Optional[List[ScheduleItem]] = None


class ScheduleUpdateRequest(BaseModel):
    schedule: List[ScheduleItem]


class ManualTodoItem(BaseModel):
    id: str
    title: str
    done: bool = False


class ManualTodosUpdateRequest(BaseModel):
    todos: Optional[List[ManualTodoItem]] = None
    manual_todos: Optional[List[ManualTodoItem]] = None


SYSTEM_TODO_CANDIDATES = [
    "全面检查车辆机油、刹车和轮胎",
    "检查灯光、链条/皮带、胎压和随车工具",
    "确认导航路线、备用路线和离线地图",
    "查看目的地及沿途天气预报",
    "查询目的地和途经城市禁摩/限行政策",
    "确认沿途加油点、维修点和补给点",
    "规划每天的具体住宿点",
    "准备换洗衣物和分层保暖装备",
    "准备雨具、防水袋和行李固定绑带",
    "准备常用药品、急救包和个人证件",
    "检查保险、驾驶证、行驶证和车辆手续",
    "准备充电宝、线缆、对讲/耳机等电子设备",
    "规划每日骑行里程和休息节奏",
    "告知家人/同行者路线与每日落脚点",
    "预留应急预算和备用现金",
]


def _get_request_user_id(http_request: Request) -> Optional[str]:
    return get_current_user_id(
        http_request.headers.get("Authorization"),
        http_request.headers.get("X-User-Id"),
    )


def _require_user_id(http_request: Request) -> str:
    user_openid = _get_request_user_id(http_request)
    if not user_openid:
        raise HTTPException(status_code=401, detail="未登录")
    return user_openid


def _as_iso(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _route_row_for_response(row: dict) -> dict:
    data = jsonable_row(row) or {}
    wp = data.get("waypoints") if isinstance(data.get("waypoints"), dict) else {}

    if data.get("user_openid") and not wp.get("user_id"):
        wp["user_id"] = data.get("user_openid")
    if data.get("start_date") and not wp.get("start_date"):
        wp["start_date"] = data.get("start_date")
    if data.get("end_date") and not wp.get("end_date"):
        wp["end_date"] = data.get("end_date")
    if data.get("estimated_days") and not wp.get("estimated_days"):
        wp["estimated_days"] = data.get("estimated_days")
    if isinstance(data.get("schedule"), list) and not wp.get("schedule"):
        wp["schedule"] = data.get("schedule")
    if isinstance(data.get("manual_todos"), list) and not wp.get("manual_todos"):
        wp["manual_todos"] = data.get("manual_todos")
    if data.get("polyline") and not wp.get("polyline"):
        wp["polyline"] = data.get("polyline")

    data["waypoints"] = wp
    data.pop("user_openid", None)
    return data


def _select_route(route_id: str) -> Optional[dict]:
    return fetch_one(
        """
        SELECT r.*, u.openid AS user_openid
        FROM routes r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.id = %s
        LIMIT 1
        """,
        (route_id,),
    )


def _authorize_route(row: dict, user_openid: Optional[str]) -> None:
    if not user_openid:
        raise HTTPException(status_code=401, detail="未登录")

    wp = row.get("waypoints") if isinstance(row.get("waypoints"), dict) else {}
    wp_owner = wp.get("user_id")
    if wp_owner and wp_owner != user_openid:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_owner = row.get("user_id")
    if db_owner is not None and int(db_owner) != get_user_db_id(user_openid):
        raise HTTPException(status_code=403, detail="Forbidden")


def _fallback_todo_titles(estimated_days: int, distance_km: float) -> list[str]:
    if estimated_days >= 5 or distance_km >= 1000:
        return [
            "全面检查车辆机油、刹车和轮胎",
            "准备换洗衣物和分层保暖装备",
            "规划每天的具体住宿点",
            "确认沿途加油点、维修点和补给点",
            "准备常用药品、应急工具和证件",
        ]
    if estimated_days <= 1 and distance_km <= 300:
        return [
            "检查车辆机油及机滤",
            "检查刹车片及制动液",
            "检查轮胎胎压及磨损",
            "确认导航路线和返程时间",
            "查看目的地天气与禁摩信息",
        ]

    return [
        "全面检查车辆机油、刹车和轮胎",
        "确认导航路线、备用路线和离线地图",
        "查看目的地及沿途天气预报",
        "准备雨具、防水袋和行李固定绑带",
        "确认沿途加油点、维修点和补给点",
    ]


def _canonical_todo_title(title: str) -> str:
    text = (title or "").strip()
    aliases = {
        "检查车辆机油及机滤": "全面检查车辆机油、刹车和轮胎",
        "检查刹车片及制动液": "全面检查车辆机油、刹车和轮胎",
        "检查轮胎胎压及磨损": "检查灯光、链条/皮带、胎压和随车工具",
        "确认导航路线和返程时间": "确认导航路线、备用路线和离线地图",
        "查看目的地天气与禁摩信息": "查看目的地及沿途天气预报",
        "准备雨具和基础保暖装备": "准备雨具、防水袋和行李固定绑带",
        "确认沿途加油点和休息点": "确认沿途加油点、维修点和补给点",
        "准备常用药品、应急工具和证件": "准备常用药品、急救包和个人证件",
    }
    return aliases.get(text, text)


def _normalize_existing_todos(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []

    out: list[dict[str, Any]] = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        out.append(
            {
                "id": str(item.get("id") or f"todo-{idx}"),
                "title": title,
                "done": bool(item.get("done")),
            }
        )
    return out


def _select_five_titles(selected: Any, estimated_days: int, distance_km: float) -> list[str]:
    allowed = set(SYSTEM_TODO_CANDIDATES)
    titles: list[str] = []
    if isinstance(selected, list):
        for item in selected:
            if isinstance(item, str):
                title = _canonical_todo_title(item)
            elif isinstance(item, dict):
                title = _canonical_todo_title(str(item.get("title") or ""))
            else:
                title = ""
            if title in allowed and title not in titles:
                titles.append(title)
            if len(titles) >= 5:
                break

    for title in _fallback_todo_titles(estimated_days, distance_km):
        canonical = _canonical_todo_title(title)
        if canonical in allowed and canonical not in titles:
            titles.append(canonical)
        if len(titles) >= 5:
            break

    for title in SYSTEM_TODO_CANDIDATES:
        if title not in titles:
            titles.append(title)
        if len(titles) >= 5:
            break
    return titles[:5]


def _build_todos_from_titles(titles: list[str], existing_todos: Any = None) -> list[dict[str, Any]]:
    existing = _normalize_existing_todos(existing_todos)
    by_title = {_canonical_todo_title(item["title"]): item for item in existing}

    selected = []
    selected_titles = set()
    for title in titles[:5]:
        old = by_title.get(title)
        selected_titles.add(title)
        selected.append(
            {
                "id": old["id"] if old else f"init-{uuid.uuid4()}",
                "title": title,
                "done": bool(old.get("done")) if old else False,
            }
        )

    manual_items = [
        item
        for item in existing
        if item["id"].startswith("manual-") and _canonical_todo_title(item["title"]) not in selected_titles
    ]
    return selected + manual_items


def _fallback_route_reminders(origin: str, destination: str, start_date: date, end_date: date, estimated_days: int, distance_km: float) -> list[dict[str, Any]]:
    reminders = [
        {
            "severity": "medium",
            "title": "关注沿途天气变化",
            "description": f"{origin} 到 {destination} 行程建议出发前再次确认天气，雨天或低温路段提前准备防水和保暖装备。",
        },
        {
            "severity": "medium",
            "title": "核对禁摩与通行政策",
            "description": f"出发日期 {start_date.isoformat()} 前，检查目的地及途经城市是否存在禁摩、限行或临时交通管制。",
        },
        {
            "severity": "low",
            "title": "控制每日骑行强度",
            "description": f"本次预计 {estimated_days} 天、约 {round(distance_km, 1)} 公里，建议按每日路书安排补给和休息。",
        },
    ]
    if estimated_days >= 5 or distance_km >= 1000:
        reminders.insert(
            0,
            {
                "severity": "high",
                "title": "长途行程需要预留缓冲",
                "description": "行程跨度较长，建议至少预留半天机动时间，并提前确认每天住宿点和维修补给点。",
            },
        )
    return reminders[:4]


def _normalize_route_reminders(raw: Any, fallback: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        raw = []

    out = []
    for idx, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        description = (item.get("description") or item.get("reason") or item.get("action") or "").strip()
        if not title or not description:
            continue
        severity = (item.get("severity") or item.get("level") or "medium").strip()
        if severity not in {"high", "medium", "low"}:
            severity = "medium"
        out.append(
            {
                "id": str(item.get("id") or f"route-ai-{uuid.uuid4()}"),
                "type": "route_ai",
                "severity": severity,
                "title": title,
                "description": description,
                "source": "AI出行提醒",
            }
        )
        if len(out) >= 4:
            break

    if out:
        return out
    return [
        {
            "id": f"route-ai-{uuid.uuid4()}",
            "type": "route_ai",
            "severity": item["severity"],
            "title": item["title"],
            "description": item["description"],
            "source": "系统出行提醒",
        }
        for item in fallback
    ]


def _route_guidance_context(
    route_name: str,
    origin: str,
    destination: str,
    start_date: date,
    end_date: date,
    estimated_days: int,
    distance_km: float,
    schedule: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "route_name": route_name,
        "origin": origin,
        "destination": destination,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "estimated_days": int(estimated_days),
        "total_distance_km": round(float(distance_km or 0), 1),
        "schedule": [
            {
                "day": item.get("day"),
                "title": item.get("title"),
                "distance_km": item.get("distance_km"),
                "description": item.get("description"),
            }
            for item in schedule
        ],
    }


def _generate_route_guidance(
    route_name: str,
    origin: str,
    destination: str,
    start_date: date,
    end_date: date,
    estimated_days: int,
    distance_km: float,
    schedule: list[dict[str, Any]],
    existing_todos: Any = None,
) -> dict[str, Any]:
    context = _route_guidance_context(
        route_name=route_name,
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        estimated_days=estimated_days,
        distance_km=distance_km,
        schedule=schedule,
    )
    fallback_titles = _fallback_todo_titles(estimated_days, distance_km)
    fallback_reminders = _fallback_route_reminders(
        origin, destination, start_date, end_date, estimated_days, distance_km
    )

    llm_result = None
    if not _env_bool("ROUTE_PLAN_USE_LLM", False):
        selected_titles = _select_five_titles(None, estimated_days, distance_km)
        route_reminders = _normalize_route_reminders(None, fallback_reminders)
        manual_todos = _build_todos_from_titles(selected_titles, existing_todos)
        return {
            "manual_todos": manual_todos,
            "route_reminders": route_reminders,
            "ai_guidance": {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "llm_used": False,
                "context": context,
                "todo_candidates": SYSTEM_TODO_CANDIDATES,
                "selected_todo_titles": selected_titles,
            },
        }

    system_prompt = (
        "你是专业摩托车旅行出行顾问，只输出严格 JSON。"
        f"当前行程内容：行程名={route_name}；起点城市={origin}；目的城市={destination}；"
        f"总里程约={round(float(distance_km or 0), 1)}km；出发日期={start_date.isoformat()}；"
        f"结束日期={end_date.isoformat()}；行程天数={int(estimated_days)}天。"
        "请基于这些城市、里程、日期和每日路书，完成两件事："
        "1. 从系统候选事项中选择最适合本行程的 5 条建议完成项；"
        "2. 生成 2-4 条出行提醒。"
        "JSON 结构必须为："
        "{\"selected_todos\":[string,string,string,string,string],"
        "\"reminders\":[{\"severity\":\"high|medium|low\",\"title\":string,\"description\":string}]}。"
        "selected_todos 必须逐字来自候选事项，不要自创事项。"
    )
    user_prompt = {
        "route": context,
        "system_todo_candidates": SYSTEM_TODO_CANDIDATES,
    }

    try:
        import json

        llm_result = ask_llm_json(system_prompt, json.dumps(user_prompt, ensure_ascii=False), max_tokens=900)
    except Exception:
        llm_result = None

    selected_titles = _select_five_titles(
        (llm_result or {}).get("selected_todos"),
        estimated_days,
        distance_km,
    )
    route_reminders = _normalize_route_reminders(
        (llm_result or {}).get("reminders"),
        fallback_reminders,
    )
    manual_todos = _build_todos_from_titles(selected_titles, existing_todos)

    return {
        "manual_todos": manual_todos,
        "route_reminders": route_reminders,
        "ai_guidance": {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "llm_used": bool(llm_result),
            "context": context,
            "todo_candidates": SYSTEM_TODO_CANDIDATES,
            "selected_todo_titles": selected_titles,
        },
    }



def _normalize_schedule_items(items: Optional[List[ScheduleItem]]) -> list[dict]:
    if not items:
        return []

    normalized = []
    for idx, item in enumerate(items):
        data = item.model_dump()
        data["day"] = idx + 1
        data["title"] = (data.get("title") or "").strip() or f"Day {idx + 1}"
        data["start_location"] = (data.get("start_location") or "").strip() or None
        data["end_location"] = (data.get("end_location") or "").strip() or None
        data["start_time"] = data.get("start_time") or "09:00"
        data["end_time"] = data.get("end_time") or "17:00"
        data["description"] = (data.get("description") or "").strip()

        distance = data.get("distance_km")
        if distance is not None:
            try:
                data["distance_km"] = max(0.0, float(distance))
            except (TypeError, ValueError):
                data["distance_km"] = None

        normalized.append(data)

    return normalized


def _clean_location_text(value: Any) -> Optional[str]:
    text = str(value or "").strip()
    return text or None


def _parse_segment_title(title: Any) -> tuple[Optional[str], Optional[str]]:
    text = str(title or "").strip()
    if not text:
        return None, None
    if text.lower().startswith("day ") or text.startswith("第"):
        return None, None

    for sep in ("->", "→", " - ", "—", "–", " 到 ", " 至 ", "到", "至"):
        if sep not in text:
            continue
        parts = [part.strip() for part in text.split(sep) if part.strip()]
        if len(parts) >= 2:
            return parts[0], parts[-1]
    return None, None


def _schedule_segment_locations(schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for item in schedule:
        start = _clean_location_text(
            item.get("start_location")
            or item.get("from_location")
            or item.get("from")
            or item.get("origin")
        )
        end = _clean_location_text(
            item.get("end_location")
            or item.get("to_location")
            or item.get("to")
            or item.get("destination")
        )

        if not start or not end:
            parsed_start, parsed_end = _parse_segment_title(item.get("title"))
            start = start or parsed_start
            end = end or parsed_end

        if start and end and start != end:
            segments.append(
                {
                    "day": int(item.get("day") or len(segments) + 1),
                    "start_location": start,
                    "end_location": end,
                }
            )
    return segments


def _build_schedule_route(
    schedule: list[dict[str, Any]],
    route_origin: str,
    route_destination: str,
) -> tuple[Optional[str], list[dict[str, Any]]]:
    segments = _schedule_segment_locations(schedule)
    if not segments:
        return None, []

    geocode_cache: dict[str, Optional[tuple[str, str]]] = {}

    def geocode(location: str) -> Optional[tuple[str, str]]:
        key = location.strip()
        if key not in geocode_cache:
            geocode_cache[key] = get_geocode(key)
        return geocode_cache[key]

    polylines: list[str] = []
    route_segments: list[dict[str, Any]] = []
    for segment in segments[:12]:
        try:
            start_geo = geocode(segment["start_location"])
            end_geo = geocode(segment["end_location"])
            if not start_geo or not end_geo:
                continue

            route_info = get_driving_route(start_geo[0], start_geo[1], end_geo[0], end_geo[1])
            segment_polyline = (route_info or {}).get("polyline")
            if not segment_polyline:
                continue

            polylines.append(segment_polyline)
            route_segments.append(
                {
                    "day": segment["day"],
                    "start_location": segment["start_location"],
                    "end_location": segment["end_location"],
                    "distance_km": round(float((route_info or {}).get("distance") or 0) / 1000, 1),
                    "duration_s": int((route_info or {}).get("duration") or 0),
                    "polyline": segment_polyline,
                }
            )
        except Exception:
            continue

    if not polylines:
        return None, []
    return ";".join(polylines), route_segments


@router.post("/api/v1/routes/plan")
def plan_route(request: RoutePlanRequest, http_request: Request):
    user_openid = _require_user_id(http_request)
    user_db_id = get_user_db_id(user_openid)

    origin_lng = None
    origin_lat = None
    dest_lng = None
    dest_lat = None
    base_distance = 0.0
    total_duration = 0
    polyline = None

    try:
        origin = get_geocode(request.origin)
        if not origin:
            raise HTTPException(status_code=400, detail="未找到起点，请换用更明确的城市或地点名称")
        origin_lng, origin_lat = origin

        dest = get_geocode(request.destination)
        if not dest:
            raise HTTPException(status_code=400, detail="未找到终点，请换用更明确的城市或地点名称")
        dest_lng, dest_lat = dest

        wp_str = None
        if request.waypoints:
            wp_coords = []
            for wp in request.waypoints:
                wp_geo = get_geocode(wp.location)
                if not wp_geo:
                    raise HTTPException(status_code=400, detail=f"未找到途经点：{wp.location}")
                wp_coords.append(f"{wp_geo[0]},{wp_geo[1]}")
            if wp_coords:
                wp_str = ";".join(wp_coords[:16])

        route_info = get_driving_route(
            origin_lng, origin_lat, dest_lng, dest_lat, waypoints=wp_str
        )
        if not route_info:
            raise HTTPException(status_code=502, detail="路线查询失败，请稍后重试或调整起终点")

        base_distance = route_info["distance"] / 1000.0
        total_duration = route_info["duration"]
        polyline = route_info.get("polyline")
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="路线服务暂不可用，请稍后重试") from exc

    daily_km = 300
    if request.riding_style == "aggressive":
        daily_km = 500
    elif request.riding_style == "scenic":
        daily_km = 200

    schedule = _normalize_schedule_items(request.schedule)
    if schedule:
        estimated_days = len(schedule)
    else:
        estimated_days = max(1, round(base_distance / daily_km))
        current_distance = 0
        for day in range(1, estimated_days + 1):
            day_distance = min(daily_km, base_distance - current_distance)
            current_distance += day_distance
            schedule.append(
                {
                    "day": day,
                    "title": f"第 {day} 天骑行",
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "distance_km": round(day_distance, 1),
                    "description": f"预计骑行 {round(day_distance, 1)} 公里，建议每 1.5 小时休息一次。",
                }
            )

    schedule_polyline, schedule_route_segments = _build_schedule_route(
        schedule,
        request.origin,
        request.destination,
    )
    end_date = request.start_date + timedelta(days=estimated_days - 1)

    guidance = _generate_route_guidance(
        route_name=request.name,
        origin=request.origin,
        destination=request.destination,
        start_date=request.start_date,
        end_date=end_date,
        estimated_days=estimated_days,
        distance_km=base_distance,
        schedule=schedule,
    )
    initial_todos = guidance["manual_todos"]
    route_reminders = guidance["route_reminders"]

    waypoints_payload = {
        "user_id": user_openid,
        "points": [wp.model_dump() for wp in request.waypoints] if request.waypoints else [],
        "start_date": str(request.start_date),
        "end_date": str(end_date),
        "estimated_days": int(estimated_days),
        "schedule": schedule,
        "manual_todos": initial_todos,
        "route_reminders": route_reminders,
        "ai_guidance": guidance["ai_guidance"],
        "polyline": polyline,
    }
    if schedule_polyline:
        waypoints_payload["schedule_polyline"] = schedule_polyline
        waypoints_payload["schedule_route_segments"] = schedule_route_segments

    try:
        row = fetch_one(
            """
            INSERT INTO routes (
                user_id, route_name, origin_name, origin_lng, origin_lat,
                dest_name, dest_lng, dest_lat, total_distance, total_duration,
                waypoints, start_date, end_date, estimated_days, schedule,
                manual_todos, polyline
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            )
            RETURNING id
            """,
            (
                user_db_id,
                request.name,
                request.origin,
                float(origin_lng) if origin_lng else None,
                float(origin_lat) if origin_lat else None,
                request.destination,
                float(dest_lng) if dest_lng else None,
                float(dest_lat) if dest_lat else None,
                int(base_distance * 1000),
                total_duration,
                jsonb(waypoints_payload),
                request.start_date,
                end_date,
                int(estimated_days),
                jsonb(schedule),
                jsonb(initial_todos),
                polyline,
            ),
        )
        inserted_id = str(row["id"]) if row else str(uuid.uuid4())
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save route")

    return {
        "status": "success",
        "data": {
            "route_id": inserted_id,
            "name": request.name,
            "origin": request.origin,
            "destination": request.destination,
            "total_distance_km": round(base_distance, 1),
            "total_duration_s": int(total_duration),
            "start_date": str(request.start_date),
            "end_date": str(end_date),
            "polyline": polyline,
            "schedule_polyline": schedule_polyline,
            "schedule_route_segments": schedule_route_segments,
            "estimated_days": estimated_days,
            "riding_style": request.riding_style,
            "schedule": schedule,
            "manual_todos": initial_todos,
            "route_reminders": route_reminders,
            "ai_guidance": guidance["ai_guidance"],
        },
    }


@router.get("/api/v1/routes")
def get_routes(http_request: Request):
    user_openid = _require_user_id(http_request)
    try:
        rows = fetch_all(
            """
            SELECT r.*, u.openid AS user_openid
            FROM routes r
            LEFT JOIN users u ON u.id = r.user_id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
            """,
            (get_user_db_id(user_openid),),
        )
        return {"status": "success", "data": [_route_row_for_response(row) for row in rows]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/api/v1/routes/{route_id}")
def get_route(route_id: str, http_request: Request):
    user_openid = _get_request_user_id(http_request)
    try:
        row = _select_route(route_id)
        if not row:
            raise HTTPException(status_code=404, detail="Route not found")
        _authorize_route(row, user_openid)
        return {"status": "success", "data": _route_row_for_response(row)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch route")


@router.put("/api/v1/routes/{route_id}/schedule")
def update_route_schedule(route_id: str, payload: ScheduleUpdateRequest, http_request: Request):
    user_openid = _get_request_user_id(http_request)
    try:
        row = _select_route(route_id)
        if not row:
            raise HTTPException(status_code=404, detail="Route not found")
        _authorize_route(row, user_openid)

        wp = row.get("waypoints") if isinstance(row.get("waypoints"), dict) else {}

        start_raw = row.get("start_date") or wp.get("start_date")
        if isinstance(start_raw, date):
            start_d = start_raw
        else:
            try:
                start_d = date.fromisoformat(str(start_raw)) if start_raw else date.today()
            except Exception:
                start_d = date.today()

        items = payload.schedule or []
        tmp = [it.model_dump() for it in items]
        tmp.sort(key=lambda x: int(x.get("day") or 0))
        if not tmp:
            raise HTTPException(status_code=400, detail="Schedule is empty")

        normalized = []
        for idx, it in enumerate(tmp):
            it["day"] = idx + 1
            if it.get("distance_km") is not None:
                try:
                    distance_km = max(0.0, float(it.get("distance_km") or 0))
                    it["distance_km"] = distance_km
                except (TypeError, ValueError):
                    it["distance_km"] = None
            normalized.append(it)

        estimated_days = len(normalized)
        end_d = start_d + timedelta(days=estimated_days - 1)
        schedule_polyline, schedule_route_segments = _build_schedule_route(
            normalized,
            str(row.get("origin_name") or ""),
            str(row.get("dest_name") or ""),
        )
        wp["schedule"] = normalized
        wp["estimated_days"] = int(estimated_days)
        wp["start_date"] = start_d.isoformat()
        wp["end_date"] = end_d.isoformat()
        if schedule_polyline:
            wp["schedule_polyline"] = schedule_polyline
            wp["schedule_route_segments"] = schedule_route_segments
        else:
            wp.pop("schedule_polyline", None)
            wp.pop("schedule_route_segments", None)

        execute(
            """
            UPDATE routes
            SET waypoints = %s,
                start_date = %s,
                end_date = %s,
                estimated_days = %s,
                schedule = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                jsonb(wp),
                start_d,
                end_d,
                int(estimated_days),
                jsonb(normalized),
                route_id,
            ),
        )

        return {
            "status": "success",
            "data": {
                "route_id": route_id,
                "start_date": wp.get("start_date"),
                "end_date": wp.get("end_date"),
                "estimated_days": wp.get("estimated_days"),
                "schedule": normalized,
                "schedule_polyline": schedule_polyline,
                "schedule_route_segments": schedule_route_segments,
            },
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update schedule")


@router.put("/api/v1/routes/{route_id}/manual-todos")
def update_route_manual_todos(route_id: str, payload: ManualTodosUpdateRequest, http_request: Request):
    user_openid = _get_request_user_id(http_request)
    try:
        row = _select_route(route_id)
        if not row:
            raise HTTPException(status_code=404, detail="Route not found")
        _authorize_route(row, user_openid)

        wp = row.get("waypoints") if isinstance(row.get("waypoints"), dict) else {}
        source_items = payload.todos if payload.todos is not None else payload.manual_todos

        normalized = []
        for item in source_items or []:
            title = (item.title or "").strip()
            if not title:
                continue
            normalized.append({"id": item.id, "title": title, "done": bool(item.done)})

        wp["manual_todos"] = normalized
        execute(
            """
            UPDATE routes
            SET waypoints = %s,
                manual_todos = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (jsonb(wp), jsonb(normalized), route_id),
        )

        return {"status": "success", "data": {"route_id": route_id, "manual_todos": normalized}}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update manual todos")


@router.get("/api/v1/routes/{route_id}/static-map")
def get_route_static_map(route_id: str, width: int = 690, height: int = 320):
    try:
        row = fetch_one("SELECT polyline, waypoints FROM routes WHERE id = %s LIMIT 1", (route_id,))
        if not row:
            raise HTTPException(status_code=404, detail="Route not found")

        wp = row.get("waypoints") if isinstance(row.get("waypoints"), dict) else {}
        polyline = (wp.get("schedule_polyline") or row.get("polyline") or wp.get("polyline") or "").strip() or None
        if not polyline:
            raise HTTPException(status_code=404, detail="No polyline")

        key = os.getenv("AMAP_WEB_API_KEY")
        if not key:
            raise HTTPException(status_code=500, detail="Missing AMAP key")

        w = max(200, min(1024, int(width)))
        h = max(200, min(1024, int(height)))

        points = polyline.split(";")
        max_points = 90
        if len(points) > max_points:
            step = len(points) / max_points
            sampled_points = [points[int(i * step)] for i in range(max_points)]
            if points[-1] not in sampled_points:
                sampled_points.append(points[-1])
            polyline = ";".join(sampled_points)

        params = {
            "key": key,
            "size": f"{w}*{h}",
            "scale": 2,
            "paths": f"5,0x2563EB,1,,:{polyline}",
        }
        r = requests.get("https://restapi.amap.com/v3/staticmap", params=params, timeout=20)
        r.raise_for_status()
        return Response(content=r.content, media_type="image/png")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate map")


@router.delete("/api/v1/routes/{route_id}")
def delete_route(route_id: str, http_request: Request):
    user_openid = _get_request_user_id(http_request)
    try:
        row = _select_route(route_id)
        if not row:
            raise HTTPException(status_code=404, detail="Route not found")
        _authorize_route(row, user_openid)
        execute("DELETE FROM routes WHERE id = %s", (route_id,))
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e)}
