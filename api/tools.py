from flask_compat import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from llm_service import ask_llm_json

router = APIRouter()

class EquipmentRequest(BaseModel):
    items: List[str]

@router.post("/api/v1/tools/equipment-calc")
def calculate_equipment(req: EquipmentRequest):
    if not req.items:
        return {"status": "error", "message": "装备列表不能为空"}
    
    system_prompt = (
        "你是专业的摩托车旅行装备专家。请根据用户提供的装备列表，"
        "预估这些装备的总重量（kg）和总体积（升），并给出每件装备的预估重量、体积，以及一句话的打包建议。"
        "你必须严格返回 JSON 格式，结构如下："
        "{"
        "\"total_weight_kg\": number,"
        "\"total_volume_L\": number,"
        "\"items\": [{\"name\": string, \"weight_kg\": number, \"volume_L\": number}],"
        "\"advice\": string"
        "}"
    )
    user_prompt = f"请评估以下装备：{', '.join(req.items)}"
    
    result = ask_llm_json(system_prompt, user_prompt)
    if not result:
        raise HTTPException(status_code=500, detail="大模型评估失败或未配置 LLM API KEY")
        
    return {"status": "ok", "data": result}

class BudgetRequest(BaseModel):
    origin: str
    destination: str
    days: int
    via_cities: Optional[str] = ""
    notes: Optional[str] = ""

@router.post("/api/v1/tools/budget-estimate")
def estimate_budget(req: BudgetRequest):
    if not req.origin or not req.destination or req.days <= 0:
        return {"status": "error", "message": "参数不合法"}

    system_prompt = (
        "你是专业的摩托车旅行财务规划师，擅长中国境内摩旅预算估算。"
        "请结合出发地、目的地、途径城市、旅行天数和备注信息，做出保守且合理的人民币预算估算。"
        "你需要综合判断路线长度、城市级别、热门旅游区溢价、住宿与饮食消费差异，以及高速/国道取向、同行人数、车型油耗、旅行风格等信息。"
        "如果用户备注未提供关键信息，请采用常见摩旅默认值：1人出行、中排量摩托、标准舒适型住宿、正常餐饮、适度景点和杂费。"
        "请确保 total_cny 约等于 fuel_cny、accommodation_cny、food_cny、other_cny 之和，数值取整数。"
        "advice 需要给出 2-3 句有用建议，说明预算高低的主要原因以及节省成本的方向。"
        "你必须严格返回 JSON 格式，结构如下："
        "{"
        "\"total_cny\": number,"
        "\"fuel_cny\": number,"
        "\"accommodation_cny\": number,"
        "\"food_cny\": number,"
        "\"other_cny\": number,"
        "\"advice\": string"
        "}"
    )
    via_text = req.via_cities.strip() if req.via_cities else "无"
    notes_text = req.notes.strip() if req.notes else "无"
    user_prompt = (
        f"出发地：{req.origin}\n"
        f"目的地：{req.destination}\n"
        f"途径城市：{via_text}\n"
        f"旅行天数：{req.days}天\n"
        f"备注：{notes_text}\n"
        "请基于以上信息输出本次摩旅预算估算。"
    )

    try:
        result = ask_llm_json(system_prompt, user_prompt)
        if not result:
            return {"status": "error", "message": "大模型评估失败或未返回可解析结果"}
        return {"status": "ok", "data": result}
    except Exception as e:
        return {"status": "error", "message": f"预算估算超时或失败：{str(e)}"}
