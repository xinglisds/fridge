import os
import base64
import requests
import io
from PIL import Image
import time
from typing import List, Optional
import random

# 导入集中管理的API密钥
from config import OPENAI_API_KEY
import openai
openai.api_key = OPENAI_API_KEY

# Food categories for better organization
FOOD_CATEGORIES = {
    "en": {
        "vegetables_fruits": ["tomato", "potato", "carrot", "cucumber", "eggplant", "cabbage", "greens", "bell pepper", "apple", "banana", "onion", "garlic", "ginger"],
        "meat": ["pork", "beef", "chicken", "fish", "shrimp", "egg", "tofu"],
        "staple_food": ["rice", "noodles", "bread", "pasta", "flour"],
        "condiments": ["salt", "sugar", "vinegar", "soy sauce", "cooking wine", "oil", "pepper", "chili"]
    },
    "zh": {
        "vegetables_fruits": ["番茄", "土豆", "胡萝卜", "黄瓜", "茄子", "白菜", "青菜", "青椒", "苹果", "香蕉", "洋葱", "蒜", "姜"],
        "meat": ["猪肉", "牛肉", "鸡肉", "鱼", "虾", "鸡蛋", "豆腐"],
        "staple_food": ["米饭", "面条", "面包", "意面", "面粉"],
        "condiments": ["盐", "糖", "醋", "酱油", "料酒", "食用油", "胡椒", "辣椒"]
    }
}

def encode_image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def recognize_food_with_gpt_vision(image: Image.Image, language: str = "en") -> List[str]:
    """
    Use GPT-4 Vision API to recognize ingredients in an image
    """
    if not OPENAI_API_KEY:
        raise ValueError("No OpenAI API key provided. Please set the OPENAI_API_KEY environment variable.")
    
    base64_image = encode_image_to_base64(image)
    
    # Prepare the prompt based on language
    if language == "zh":
        prompt = """请分析这张冰箱照片，识别其中的食物。
- 只输出可以吃或喝的食材名
- 不需要加入“可能是”、“看起来像”等模糊词汇
- 输出结果请用英文逗号分隔，例如：鸡蛋, 番茄, 牛奶, 牛肉"""
    else:
        prompt = """Please analyze the fridge photo and identify the edible items.

- Only list food or drink ingredients
- Do not include vague words like "possibly" or "looks like"
- Return a single comma-separated list, e.g.: egg, tomato, milk, beef"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=300
        )
        
        # Extract ingredients from response
        result = response.choices[0].message.content.strip()
        
        # 从逗号分隔的列表中提取食材
        # 首先尝试按逗号分隔
        if ',' in result:
            items = [item.strip() for item in result.split(',')]
        # 如果没有逗号，则按行分隔
        else:
            items = [line.strip() for line in result.split('\n')]
        
        # 过滤和清理结果
        ingredients = []
        for item in items:
            # 清理每个食材
            item = item.strip()
            # 去除可能的标点符号
            while item and item[-1] in '.,;:，。；：':
                item = item[:-1].strip()
            # 去除可能的编号前缀
            if item and item[0].isdigit() and len(item) > 1 and item[1] in '.,、) ':
                item = item[2:].strip()
            # 去除可能的非食材关键词
            if item and not any(non_food in item.lower() for non_food in ['bag', 'bottle', 'container', 'package', 'wrapper', 'possibly', 'could be', 'maybe', '包装', '袋', '瓶', '容器', '可能', '也许']):
                if item:  # 确保处理后不是空字符串
                    ingredients.append(item)
        
        return ingredients
    
    except Exception as e:
        print(f"Error calling GPT-4 Vision: {str(e)}")
        return []

def recognize_food_mock(image: Image.Image, language: str = "en") -> List[str]:
    """
    Mock function for food recognition when API key is not available
    """
    # Simulate processing delay
    time.sleep(2)
    
    # Select food items based on language
    categories = FOOD_CATEGORIES[language]
    
    # Randomly select 3-6 ingredients from various categories
    import random
    all_ingredients = []
    for category, items in categories.items():
        all_ingredients.extend(items)
    
    num_items = random.randint(3, 6)
    return random.sample(all_ingredients, min(num_items, len(all_ingredients)))

def recognize_food(image: Image.Image) -> List[str]:
    """
    Main function to recognize food in an image
    """
    try:
        # Get current language setting
        import streamlit as st
        language = st.session_state.get('language', 'en')
        
        # Use GPT-4 Vision if API key is available
        if OPENAI_API_KEY:
            return recognize_food_with_gpt_vision(image, language)
        # Otherwise use mock function
        else:
            return recognize_food_mock(image, language)
    except Exception as e:
        print(f"Food recognition error: {str(e)}")
        # Return basic ingredients on error to ensure continuity
        default_items = ["egg", "tomato"] if language == "en" else ["鸡蛋", "番茄"]
        return default_items 