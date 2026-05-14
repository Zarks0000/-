from flask_compat import APIRouter

from llm_service import ask_kimi_json_with_web_search

router = APIRouter()


@router.get("/api/v1/restriction/city")
def get_city_restriction(city: str):
    """
    获取指定城市的禁摩政策，通过 Kimi 内置联网搜索工具查询并总结。
    """

    system_prompt = (
        "你是一个专业的摩托旅行规划助手。"
        "你必须使用联网搜索核对最新公开信息，并严格输出 JSON，"
        "不要输出任何解释、markdown 或 JSON 之外的文本。"
    )
    user_prompt = f"""
请联网搜索并总结 {city} 最新禁摩/限摩政策，重点关注摩托车限行、禁行区域、临时交通管制和通行证要求。

当前日期为 2026-05-14，请优先参考近两年的公开信息、政府/交警/公安/交通管理部门信息。

请严格按照以下 JSON 格式返回：
{{
  "is_restricted": true,
  "level": "high",
  "title": "【禁摩警示】示例标题",
  "description": "用一段话说明核心政策、限制区域、适用车辆和需要注意的出行建议。如果搜索不到明确政策，请说明暂未搜索到明确禁摩政策。",
  "source": "简要列出主要参考来源名称",
  "time": "2026年最新"
}}

字段规则：
- is_restricted: 有明确禁摩/限摩/核心区域限制则为 true，否则为 false。
- level: 全城或大范围禁摩为 "high"，部分区域/时段限制为 "medium"，未查到明确限制为 "low"。
- title: 简短标题。
- description: 不要编造，无法确认就明确写“暂未搜索到明确政策”。
- source: 写来源名称，不要写长链接。
- time: 写信息时效。
"""

    try:
        result_dict = ask_kimi_json_with_web_search(system_prompt, user_prompt, max_tokens=900)
        if result_dict is None:
            raise Exception("Kimi 联网搜索返回为空或无法解析为 JSON")

        return {
            "status": "success",
            "city": city,
            "data": result_dict,
        }
    except Exception as e:
        return {
            "status": "error",
            "city": city,
            "message": str(e),
            "data": {
                "is_restricted": False,
                "level": "low",
                "title": "查询失败",
                "description": "Kimi 联网搜索查询或解析失败，请检查 LLM_BASE_URL、LLM_API_KEY 和 LLM_MODEL 配置。",
                "source": "系统提示",
                "time": "N/A",
            },
        }
