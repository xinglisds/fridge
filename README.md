# FridgeChef AI

FridgeChef AI is a lightweight AI application where users upload refrigerator photos, the system identifies ingredients, and generates home-style recipes for reference. No login required, simple to use, helping users solve the daily challenge of "I have ingredients in my fridge but don't know what to cook".

[中文版本](#fridgechef-ai-小厨)

## Features

- **AI-Powered Image Recognition**: Upload refrigerator photos to automatically identify ingredients using GPT-4 Vision API
- **Ingredient Editing**: Add, delete, and confirm recognized ingredients
- **Smart Recipe Recommendations**: Generate 3 Chinese home-style recipes based on available ingredients with GPT
- **Detailed Recipes**: Including recipe name, required ingredients, cooking steps, estimated time, and difficulty level
- **YouTube Cooking Videos**: Watch related cooking videos for each recipe
- **Intelligent Assistant**: Chat with the AI assistant about recipes, cooking techniques, and food questions
- **Dietary Restrictions**: Specify dietary preferences for personalized recipe generation
- **Multilingual Support**: Switch between English and Chinese interfaces

## Technology Stack

- **Frontend**: Streamlit for the interactive web interface
- **AI Brain**: GPT-4 and GPT-4 Vision powering the intelligence
- **Agent Architecture**: Function calling capability for flexible tool usage
- **Multimodal Processing**: Image and text processing in one application

## Project Structure

- **app.py**: Main application file with Streamlit UI and user flow
- **agent.py**: Agent architecture that coordinates different tools and services
- **food_recognition.py**: Food ingredient recognition using GPT-4 Vision API
- **recipe_generation.py**: Recipe creation based on recognized ingredients
- **config.py**: Centralized configuration file for API keys and settings

## Installation & Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/fridgechef-ai.git
   cd fridgechef-ai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key (required) in the following ways:
   - Environment variable (recommended):
     ```bash
     # Linux/Mac
     export OPENAI_API_KEY=your_openai_api_key
     
     # Windows
     set OPENAI_API_KEY=your_openai_api_key
     ```
   - Or directly edit the config.py file (not recommended for production)

4. Run the application:
   ```bash
   streamlit run app.py
   ```

5. Visit `http://localhost:8501` in your browser

## Example Flow

1. User visits the application
2. Select language if needed (English/Chinese)
3. Upload a refrigerator photo
4. GPT-4 Vision identifies ingredients in the image
5. User confirms the recognition results, can modify ingredients or add dietary restrictions
6. Click "Generate Recipe Recommendations" button
7. System generates and displays 3 recipes with YouTube videos
8. User can chat with the AI assistant about recipes or cooking questions

## Notes

- This application requires an OpenAI API key to function properly
- Images are only used for immediate recognition and are not permanently stored
- API call limit is 5 times per hour to manage costs

---

# FridgeChef AI 小厨

FridgeChef AI 小厨是一个轻量级AI应用，用户上传冰箱照片，系统识别出其中食材，并生成家常菜谱供参考。无需登录，使用简单便捷，帮助用户解决"冰箱有食材但不知道做什么"的日常难题。

## 功能特点

- **AI图像识别**：使用GPT-4 Vision API上传冰箱照片，自动识别食材
- **食材编辑**：添加、删除、确认识别的食材
- **智能菜谱推荐**：通过GPT根据现有食材生成3道中式家常菜谱
- **详细菜谱**：包含菜名、所需材料、烹饪步骤、所需时间和难度
- **YouTube烹饪视频**：每道菜谱配有相关烹饪视频教程
- **智能助手**：与AI助手聊天，询问菜谱、烹饪技巧和食物问题
- **饮食限制**：指定饮食偏好，获取个性化菜谱推荐
- **多语言支持**：支持英文和中文界面切换

## 技术栈

- **前端**：Streamlit交互式Web界面
- **AI大脑**：GPT-4和GPT-4 Vision提供智能支持
- **Agent架构**：函数调用能力实现灵活工具使用
- **多模态处理**：在一个应用中实现图像和文本处理

## 项目结构

- **app.py**：主应用文件，包含Streamlit界面和用户流程
- **agent.py**：Agent架构，协调不同工具和服务
- **food_recognition.py**：使用GPT-4 Vision API的食材识别功能
- **recipe_generation.py**：基于识别食材的菜谱生成
- **config.py**：集中管理API密钥和设置的配置文件

## 安装与运行

1. 克隆此仓库：
   ```bash
   git clone https://github.com/yourusername/fridgechef-ai.git
   cd fridgechef-ai
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 设置OpenAI API密钥（必需），可通过以下方式：
   - 环境变量（推荐）：
     ```bash
     # Linux/Mac
     export OPENAI_API_KEY=your_openai_api_key
     
     # Windows
     set OPENAI_API_KEY=your_openai_api_key
     ```
   - 或直接编辑config.py文件（生产环境不推荐）

4. 运行应用：
   ```bash
   streamlit run app.py
   ```

5. 在浏览器中访问 `http://localhost:8501`

## 示例流程

1. 用户访问应用
2. 根据需要选择语言（英文/中文）
3. 上传冰箱照片
4. GPT-4 Vision识别出图片中的食材
5. 用户确认识别结果，可修改食材或添加饮食限制
6. 点击"生成菜谱推荐"按钮
7. 系统根据食材生成并展示3道菜谱及YouTube视频
8. 用户可与AI助手聊天，询问菜谱或烹饪问题

## 注意事项

- 此应用需要OpenAI API密钥才能正常运行
- 图片仅用于即时识别，不会永久存储
- 每小时API调用次数限制为5次以控制成本 