from flask_compat import APIRouter
from typing import Optional, Any

router = APIRouter()

# 获取智能出行建议和装备推荐的路由
@router.get("/api/v1/suggestions")
def get_smart_suggestions(destination: str, days: int, month: int, origin: Optional[str] = None):
    """
    根据目的地、出行天数、出行月份，智能生成摩旅建议及装备清单。
    在实际生产中可以结合 AI 大模型（如 GPT、文心一言）或者复杂的规则引擎。
    """
    
    # 模拟规则引擎生成的建议
    suggestions = []
    equipment = [
        {"category": "基础安全", "items": ["全盔", "骑行服(带护具)", "骑行手套", "骑行靴"]},
        {"category": "车辆备件", "items": ["补胎工具", "便携充气泵", "备用机油", "链条油"]},
    ]
    
    # 规则1：高海拔或西藏相关
    if "拉萨" in destination or "西藏" in destination or "川藏" in destination:
        suggestions.extend([
            {"type": "health", "title": "防高反准备", "content": "提前1-2周服用红景天，切忌带病上高原。初到高原前三天不要洗澡。"},
            {"type": "vehicle", "title": "化油器/电喷调整", "content": "高海拔氧气稀薄，会导致动力下降，建议提前检查空滤，部分老车需调整混合比。"}
        ])
        equipment.append({"category": "高海拔特供", "items": ["便携氧气罐", "抗高反药物", "防寒保暖内衣", "防风面罩"]})
        
    # 规则2：长途旅行（>3天）
    if days > 3:
        suggestions.append(
            {"type": "schedule", "title": "体能分配", "content": f"本次行程长达 {days} 天，建议不要每天赶路，每骑行3-4天安排1天的纯休整日。"}
        )
        equipment.append({"category": "长途生活", "items": ["换洗衣物", "洗漱包", "高热量零食", "保温水壶"]})
        
    # 规则3：冬季或寒冷月份 (11, 12, 1, 2)
    if month in [11, 12, 1, 2]:
        suggestions.append(
            {"type": "weather", "title": "冬季保暖防滑", "content": "低温会导致轮胎抓地力下降，起步前需充分热胎。注意防风保暖，防止失温。"}
        )
        equipment.append({"category": "冬季特供", "items": ["电加热手套", "加厚护膝", "防雾贴", "保暖内胆"]})
        
    # 默认兜底建议
    if not suggestions:
        suggestions.append(
            {"type": "general", "title": "安全第一", "content": "遵守交通规则，控制车速，避免夜间山路骑行。"}
        )

    try:
        from amap_service import get_geocode, get_driving_route
        from llm_service import generate_plan, is_configured
        import weather as weather_module
        import restriction as restriction_module
        import news as news_module

        llm_context = {
            "origin": origin,
            "destination": destination,
            "days": days,
            "month": month,
            "map": {},
            "weather": {},
            "policy": {},
            "news": {},
        }

        if origin:
            o = get_geocode(origin)
            d = get_geocode(destination)
            if o and d:
                route_info = get_driving_route(o[0], o[1], d[0], d[1])
                if route_info:
                    llm_context["map"] = {
                        "distance_m": route_info["distance"],
                        "duration_s": route_info["duration"],
                    }

        llm_context["weather"] = weather_module.get_weather_alerts(destination)
        llm_context["policy"] = restriction_module.get_city_restriction(destination)
        if origin:
            llm_context["news"] = news_module.get_route_news_alerts(origin, destination, None, 6)
        else:
            llm_context["news"] = news_module.get_news_alerts(destination, 3)

        if is_configured():
            plan = generate_plan(llm_context)
            if isinstance(plan, dict):
                risk_items = plan.get("risk_items") or []
                llm_suggestions = []
                for r in risk_items:
                    if not isinstance(r, dict):
                        continue
                    llm_suggestions.append(
                        {
                            "type": r.get("type") or "risk",
                            "title": r.get("title") or "风险提醒",
                            "content": f"{r.get('reason') or ''} {r.get('action') or ''}".strip(),
                        }
                    )
                if llm_suggestions:
                    suggestions = llm_suggestions

                llm_equipment = plan.get("equipment")
                if isinstance(llm_equipment, list) and llm_equipment:
                    equipment = llm_equipment

                return {
                    "status": "success",
                    "destination": destination,
                    "days": days,
                    "month": month,
                    "data": {
                        "suggestions": suggestions,
                        "equipment_list": equipment,
                        "ai_plan": plan,
                    },
                }
    except Exception:
        pass

    return {
        "status": "success",
        "destination": destination,
        "days": days,
        "month": month,
        "data": {
            "suggestions": suggestions,
            "equipment_list": equipment
        }
    }
