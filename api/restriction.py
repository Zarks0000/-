from flask_compat import APIRouter
from pydantic import BaseModel
import os
import requests
import json
from llm_service import ask_llm_json

router = APIRouter()

def search_tavily(query: str) -> str:
    """使用 Tavily API 进行联网搜索"""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "未配置 Tavily API KEY，无法进行联网搜索。"
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "include_images": False,
        "include_raw_content": False,
        "max_results": 3
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return "未搜索到相关禁摩政策信息。"
            
        search_context = []
        for r in results:
            search_context.append(f"来源: {r.get('title', '')}\n内容摘要: {r.get('content', '')}")
            
        return "\n\n".join(search_context)
    except Exception as e:
        return f"联网搜索失败: {str(e)}"

# 获取城市禁摩政策的路由
@router.get("/api/v1/restriction/city")
def get_city_restriction(city: str):
    """
    获取指定城市的禁摩政策，通过 Tavily 联网搜索并由大模型总结。
    """
    
    search_query = f"2026年最新 {city} 禁摩限摩政策 摩托车限行规定"
    search_results = search_tavily(search_query)
    
    try:
        # 修改：为了兼容 Moonshot Kimi API，把所有内容放在 user role 里，而不是 system role
        # 所以 ask_llm_json(system_prompt, user_prompt) 这里我们把指令全塞给 user_prompt，system_prompt 给一句基础设定
        system_prompt = "你是一个专业的摩托旅行规划助手。请你严格按照要求的 JSON 格式输出结果，不要输出任何多余的解释或 markdown 标记。"
        
        user_prompt = f"""
        请根据以下联网搜索结果，总结 {city} 最新（截至 2026 年）的禁摩/限摩政策。
        
        请严格按照以下 JSON 格式返回结果：
        {{
            "is_restricted": true,
            "level": "string",
            "title": "string",
            "description": "string",
            "source": "string",
            "time": "string"
        }}
        说明：
        - level: 严重程度。全城禁摩为 "high"，部分区域限行为 "medium"，不限制为 "low"
        - title: 政策简短标题，如 "【禁摩警示】北京四环内禁摩"
        - description: 详细的政策说明，如果搜索不到信息，请说明“暂未搜索到明确的禁摩政策”
        - source: 信息来源（综合搜索结果）
        - time: 更新时间，如 "2026年最新"
        
        联网搜索结果：
        {search_results}
        """
        
        result_dict = ask_llm_json(system_prompt, user_prompt)
        
        # 兼容一些可能未正确返回的情况
        if result_dict is None:
            raise Exception("大模型返回为空或无法解析为 JSON")
            
        return {
            "status": "success",
            "city": city,
            "data": result_dict
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
                "description": "大模型查询或解析失败，请检查 API 配置。",
                "source": "系统提示",
                "time": "N/A"
            }
        }
