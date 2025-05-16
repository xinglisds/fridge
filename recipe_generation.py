import os
import json
import time
import random
from typing import List, Dict, Any, Optional

# 导入集中管理的API密钥
from config import OPENAI_API_KEY
import openai
openai.api_key = OPENAI_API_KEY

# Mock recipe data for demonstration when API key is not available
MOCK_RECIPES_ZH = [
    # 番茄炒蛋菜谱
    {
        "name": "番茄炒蛋",
        "difficulty": "简单",
        "time": "15分钟",
        "materials": [
            "鸡蛋 4个",
            "番茄 2个",
            "葱花 适量",
            "盐 适量",
            "食用油 适量",
            "糖 少许"
        ],
        "steps": [
            "将鸡蛋打散，番茄切块",
            "热锅冷油，倒入打散的鸡蛋液，炒至金黄",
            "加入番茄块，翻炒至番茄软化出汁",
            "加入盐、糖调味",
            "撒上葱花即可出锅"
        ]
    },
    # 青椒土豆丝菜谱
    {
        "name": "青椒土豆丝",
        "difficulty": "中等",
        "time": "20分钟",
        "materials": [
            "土豆 2个",
            "青椒 2个",
            "干辣椒 少许",
            "蒜 3瓣",
            "盐 适量",
            "醋 少许"
        ],
        "steps": [
            "土豆、青椒切丝，蒜切片",
            "土豆丝用清水浸泡10分钟去除淀粉",
            "热锅下油，放入干辣椒和蒜片爆香",
            "加入土豆丝翻炒3分钟，再加入青椒丝翻炒2分钟",
            "加入盐和醋调味即可"
        ]
    },
    # 蒜蓉蒸虾菜谱
    {
        "name": "蒜蓉蒸虾",
        "difficulty": "中等",
        "time": "25分钟",
        "materials": [
            "虾 500克",
            "蒜 8瓣",
            "姜 少许",
            "葱 适量",
            "酱油 少许",
            "食用油 适量"
        ],
        "steps": [
            "虾去头去壳，留尾，剪开背部去除虾线",
            "蒜剁成蒜蓉，姜切末，葱切段",
            "将虾摆盘，撒上蒜蓉和姜末",
            "锅中烧开水，放入虾盘隔水蒸8分钟",
            "淋上热油和酱油，撒上葱花即可"
        ]
    }
]

# English mock recipes
MOCK_RECIPES_EN = [
    # Scrambled Eggs with Tomatoes
    {
        "name": "Scrambled Eggs with Tomatoes",
        "difficulty": "Easy",
        "time": "15 minutes",
        "materials": [
            "4 eggs",
            "2 tomatoes",
            "green onion, chopped",
            "salt to taste",
            "cooking oil",
            "sugar, a pinch"
        ],
        "steps": [
            "Beat the eggs, cut tomatoes into chunks",
            "Heat oil in a pan, add beaten eggs and scramble until golden",
            "Add tomato chunks, stir-fry until soft and juicy",
            "Season with salt and sugar",
            "Sprinkle chopped green onions before serving"
        ]
    },
    # Stir-fried Potato and Bell Pepper Shreds
    {
        "name": "Stir-fried Potato and Bell Pepper Shreds",
        "difficulty": "Medium",
        "time": "20 minutes",
        "materials": [
            "2 potatoes",
            "2 bell peppers",
            "dried chili peppers",
            "3 cloves of garlic",
            "salt to taste",
            "vinegar"
        ],
        "steps": [
            "Cut potatoes and bell peppers into thin strips, slice garlic",
            "Soak potato strips in water for 10 minutes to remove starch",
            "Heat oil, add dried chilies and garlic slices to release aroma",
            "Stir-fry potato strips for 3 minutes, then add bell pepper strips for 2 minutes",
            "Season with salt and vinegar"
        ]
    },
    # Steamed Shrimp with Garlic
    {
        "name": "Steamed Shrimp with Garlic",
        "difficulty": "Medium",
        "time": "25 minutes",
        "materials": [
            "500g shrimp",
            "8 cloves of garlic",
            "ginger",
            "green onion",
            "soy sauce",
            "cooking oil"
        ],
        "steps": [
            "Remove shrimp heads, leave tails on, devein",
            "Mince garlic and ginger, cut green onion into sections",
            "Arrange shrimp on a plate, sprinkle with garlic and ginger",
            "Bring water to a boil, steam the shrimp plate for 8 minutes",
            "Drizzle hot oil and soy sauce, garnish with green onions"
        ]
    }
]

def generate_recipes_with_gpt(ingredients: List[str], language: str = "en", dietary_restrictions: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate recipes using OpenAI GPT API based on provided ingredients
    """
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not provided. Please set the OPENAI_API_KEY environment variable.")
    
    # Increment API call counter
    import streamlit as st
    if 'api_calls' in st.session_state:
        st.session_state.api_calls += 1
    
    # Prepare prompt based on language
    if language == "zh":
        prompt = f"""
        请根据以下食材生成3道中式家常菜谱:
        {', '.join(ingredients)}
        
        每道菜包括:
        1. 菜名
        2. 难度级别(简单/中等/复杂)
        3. 预计烹饪时间
        4. 所需材料清单(包括调料)
        5. 烹饪步骤(最多5步)
        
        注意:
        - 仅使用用户提供的现有食材
        - 所有菜谱的材料和烹饪步骤必须使用中文
        
        请用中文回答，以JSON格式输出，结构如下:
        ```json
        [
          {{
            "name": "菜名",
            "difficulty": "难度",
            "time": "烹饪时间",
            "materials": ["材料1", "材料2", ...],
            "steps": ["步骤1", "步骤2", ...]
          }},
          ...共3道菜
        ]
        ```
        """
        system_message = "你是一名专业中餐厨师，擅长根据现有食材创造美味的家常菜谱。务必使用普通家庭中的食材，不提示添加新的食材。"
        
        # Add dietary restrictions if provided
        if dietary_restrictions:
            prompt += f"\n\n请注意以下饮食限制：{dietary_restrictions}"
    else:
        prompt = f"""
        Create 3 Chinese home-style recipes based on these ingredients:
        {', '.join(ingredients)}
        
        Each recipe should include:
        1. Recipe name
        2. Difficulty level (Easy/Medium/Hard)
        3. Estimated cooking time
        4. Required ingredients list (including seasonings)
        5. Cooking steps (maximum 5 steps)
        
        Note:
        - Only use the ingredients provided by the user
        - All materials and steps should be in English
        
        Please respond in English, in JSON format as follows:
        ```json
        [
          {{
            "name": "Recipe Name",
            "difficulty": "Difficulty Level",
            "time": "Cooking Time",
            "materials": ["Ingredient 1", "Ingredient 2", ...],
            "steps": ["Step 1", "Step 2", ...]
          }},
          ...total of 3 recipes
        ]
        ```
        """
        system_message = "You are a professional Chinese cuisine chef who specializes in creating delicious home-style dishes from available ingredients. Use only the ingredients the user already has, don't suggest adding new ingredients."

        # Add dietary restrictions if provided
        if dietary_restrictions:
            prompt += f"\n\nPlease consider these dietary restrictions: {dietary_restrictions}"
    
    try:
        # Call the GPT API
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract JSON part
        import re
        json_match = re.search(r'```json\n([\s\S]*?)\n```', content)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = content
        
        # Clean and parse JSON
        json_str = json_str.replace("```", "").strip()
        recipes = json.loads(json_str)
        
        return recipes
    
    except Exception as e:
        print(f"GPT API call error: {str(e)}")
        raise e

def mock_generate_recipes(ingredients: List[str], language: str = "en") -> List[Dict[str, Any]]:
    """
    Mock recipe generation for demonstration
    """
    # Simulate processing delay
    time.sleep(random.uniform(3.0, 5.0))
    
    # Return mock recipes based on language
    return MOCK_RECIPES_EN if language == "en" else MOCK_RECIPES_ZH

def generate_recipes(ingredients: List[str], dietary_restrictions: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Main function to generate recipes based on ingredients
    """
    try:
        # Get current language and increment API call counter
        import streamlit as st
        language = st.session_state.get('language', 'en')
        
        # Initialize API call counter if it doesn't exist
        if 'api_calls' not in st.session_state:
            st.session_state.api_calls = 0
        
        # Check if API limit has been reached
        if st.session_state.api_calls >= 5:
            st.warning(TRANSLATIONS[language]["api_limit"])
            return []
        
        # Use real API if key is available
        if OPENAI_API_KEY:
            recipes = generate_recipes_with_gpt(ingredients, language, dietary_restrictions)
        # Otherwise use mock data
        else:
            recipes = mock_generate_recipes(ingredients, language)
        
        return recipes
    
    except Exception as e:
        print(f"Recipe generation error: {str(e)}")
        # Return at least one mock recipe to avoid breaking the app
        return [MOCK_RECIPES_EN[0]] if language == "en" else [MOCK_RECIPES_ZH[0]]

# Access translations from translations.py (needed for error messages)
from translations import TRANSLATIONS
# ... rest of the file ... 