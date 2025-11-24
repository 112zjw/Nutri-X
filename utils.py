import os
import json
import dashscope
from dashscope import MultiModalConversation, Generation
from http import HTTPStatus
import tempfile

# 默认使用 qwen-vl-max 进行图像识别，qwen-plus 进行文本生成
VL_MODEL = "qwen-vl-max"
TEXT_MODEL = "qwen-plus"

def setup_api_key(api_key):
    """配置 API Key"""
    if api_key:
        dashscope.api_key = api_key
    elif os.getenv('DASHSCOPE_API_KEY'):
        dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
    else:
        raise ValueError("未找到 API Key，请在侧边栏输入或配置 .env 文件")

def save_uploaded_file(uploaded_file):
    """将上传的文件保存为临时文件，以便 SDK 读取"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def identify_ingredients(image_path):
    """
    使用 Qwen-VL 识别图片中的食材
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"file://{image_path}"},
                {"text": """
                请分析这张图片。
                1. 首先判断图片中是否包含食材或食物。如果不包含，请直接返回 JSON: {"is_food": false}。
                2. 如果包含食材，请识别所有食材，并给出它们在图片中的位置（bounding box，0-1000坐标系）。
                3. 对于每个识别出的物体，请判断它是否是食物（is_food: true/false）。
                4. 请以严格的 JSON 格式返回，不要包含 Markdown 标记。
                格式示例：
                {
                    "is_food": true,
                    "items": [
                        {"name": "西红柿", "box_2d": [250, 300, 400, 450], "is_food": true},
                        {"name": "盘子", "box_2d": [200, 250, 800, 850], "is_food": false}
                    ]
                }
                注意：box_2d 格式为 [x1, y1, x2, y2]，其中 x1, y1 是左上角坐标，x2, y2 是右下角坐标。
                """}
            ]
        }
    ]
    
    try:
        response = MultiModalConversation.call(model=VL_MODEL, messages=messages)
        if response.status_code == HTTPStatus.OK:
            content = response.output.choices[0].message.content[0]['text']
            content = content.replace('```json', '').replace('```', '').strip()
            try:
                data = json.loads(content)
                return data
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {"is_food": False, "error": "解析响应失败"}
        else:
            return {"is_food": False, "error": f"API Error: {response.code}"}
    except Exception as e:
        return {"is_food": False, "error": str(e)}

def get_nutrition_info(ingredients_list):
    """
    获取食材的营养成分（JSON格式）
    """
    prompt = f"""
    请分析以下食材的营养成分：{', '.join(ingredients_list)}。
    请以严格的 JSON 格式返回数据，不要包含 Markdown 格式标记（如 ```json）。
    返回格式为一个列表，每个元素包含：
    - name: 食材名称
    - calories: 每100g卡路里(kcal)
    - protein: 蛋白质(g)
    - fat: 脂肪(g)
    - carbs: 碳水化合物(g)
    - benefit: 主要营养价值简述(10字以内)
    """
    
    try:
        response = Generation.call(model=TEXT_MODEL, messages=[{'role': 'user', 'content': prompt}], result_format='message')
        if response.status_code == HTTPStatus.OK:
            content = response.output.choices[0].message.content
            # 尝试清理可能存在的 markdown 标记
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        else:
            print(f"Error: {response.code} - {response.message}")
            return []
    except Exception as e:
        print(f"Exception: {str(e)}")
        return []

def recommend_recipes(selected_ingredients):
    """
    根据选择的食材推荐菜肴
    """
    prompt = f"""
    我手头有以下食材：{', '.join(selected_ingredients)}。
    请为我推荐 3 道适合用这些食材制作的佳肴。
    请以严格的 JSON 格式返回数据，不要包含 Markdown 格式标记。
    返回格式为一个列表，每个元素包含：
    - name: 菜肴名称
    - description: 简短介绍
    - ingredients: 所需食材列表
    - steps: 详细做法步骤（字符串列表）
    - nutrition_eval: 营养价值评价
    - taste_eval: 口感偏好评价
    - video_keyword: 用于搜索该菜做法视频的关键词（例如“西红柿炒鸡蛋 做法”）
    """
    
    try:
        response = Generation.call(model=TEXT_MODEL, messages=[{'role': 'user', 'content': prompt}], result_format='message')
        if response.status_code == HTTPStatus.OK:
            content = response.output.choices[0].message.content
            content = content.replace('```json', '').replace('```', '').strip()
            return json.loads(content)
        else:
            return []
    except Exception as e:
        print(f"Exception: {str(e)}")
        return []

def evaluate_meal_plan(meal_plan):
    """
    评估三餐规划的合理性
    """
    plan_str = json.dumps(meal_plan, ensure_ascii=False)
    prompt = f"""
    这是我一天的三餐规划：
    {plan_str}
    
    请从以下几个维度进行专业评估：
    1. 营养均衡性（碳水、蛋白质、脂肪比例，维生素摄入等）
    2. 热量合理性
    3. 食材多样性
    4. 改进建议
    
    请用 Markdown 格式输出一份精美的评估报告。
    """
    
    try:
        response = Generation.call(model=TEXT_MODEL, messages=[{'role': 'user', 'content': prompt}], result_format='message')
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0].message.content
        else:
            return "评估失败，请稍后重试。"
    except Exception as e:
        return f"评估出错: {str(e)}"
