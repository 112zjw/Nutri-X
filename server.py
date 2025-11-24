from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
import shutil
import utils
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为前端的具体地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 辅助函数：设置 API Key
def configure_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key:
        utils.setup_api_key(x_api_key)
    else:
        # 尝试从环境变量加载
        env_key = os.getenv("DASHSCOPE_API_KEY")
        if env_key:
            utils.setup_api_key(env_key)
        # 如果都没有，utils 内部可能会报错，或者在调用时报错

class IngredientsRequest(BaseModel):
    ingredients: List[str]

class MealPlanRequest(BaseModel):
    plan: Dict[str, List[str]]

@app.post("/api/identify")
async def identify_ingredients(file: UploadFile = File(...), x_api_key: Optional[str] = Header(None)):
    try:
        configure_api_key(x_api_key)
        
        # 保存上传的文件
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 识别食材
        result = utils.identify_ingredients(temp_file_path)
        
        # 删除临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        if isinstance(result, dict):
            if not result.get("is_food", False):
                return {
                    "status": "error", 
                    "message": "未识别到有效食材，请上传包含食物的图片。",
                    "is_food": False
                }
            
            items = result.get("items", [])
            
            # 仅提取被标记为食物的物品名称用于营养分析
            food_items = [item for item in items if item.get("is_food", True)]
            ingredient_names = [item["name"] for item in food_items]
            
            # 获取营养信息
            nutrition_info = utils.get_nutrition_info(ingredient_names)
            
            return {
                "status": "success",
                "ingredients": ingredient_names,
                "items_with_loc": items, # 返回所有识别结果（包含非食物）以便前端展示警告
                "nutrition": nutrition_info
            }
        else:
            return {"status": "error", "message": "识别服务异常"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/recommend")
async def recommend_recipes(request: IngredientsRequest, x_api_key: Optional[str] = Header(None)):
    try:
        configure_api_key(x_api_key)
        recommendations = utils.recommend_recipes(request.ingredients)
        return {"status": "success", "data": recommendations}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/evaluate")
async def evaluate_plan(request: MealPlanRequest, x_api_key: Optional[str] = Header(None)):
    try:
        configure_api_key(x_api_key)
        report = utils.evaluate_meal_plan(request.plan)
        return {"status": "success", "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
