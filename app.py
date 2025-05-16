import streamlit as st

# 设置页面配置 - Must be the first Streamlit command
st.set_page_config(
    page_title="FridgeChef AI",
    page_icon="🍳",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=None
)

import os
from PIL import Image
import io
import time
import random
from food_recognition import recognize_food
from recipe_generation import generate_recipes
from agent import FridgeChefAgent

# 导入配置
from config import OPENAI_API_KEY, MAX_API_CALLS_PER_HOUR, YOUTUBE_API_KEY
from translations import TRANSLATIONS

# 定义CSS样式
st.markdown("""
<style>
    /* 隐藏汉堡菜单 - 使用更精确的选择器 */
    .css-1rs6os.edgvbvh3, 
    header[data-testid="stHeader"] button, 
    [data-testid="collapsedControl"],
    header button svg,
    header div[data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* 隐藏整个顶部菜单栏 */
    header {
        visibility: hidden;
    }
    
    /* 隐藏 "made with streamlit" */
    footer {
        display: none !important;
    }
    
    /* 移除标题的链接/锚点行为 */
    .main h1 a, .main h2 a, .main h3 a, .main h4 a {
        display: none !important;
    }
    
    /* 重置Streamlit默认最大宽度 */
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 确保容器居中 */
    .reportview-container .main {
        display: flex;
        justify-content: center;
    }
    
    /* 确保按钮样式统一且居中 */
    .stButton>button {
        width: 100%;
    }
    
    /* 食材删除按钮样式 */
    .stButton>button[data-baseweb="button"] {
        font-size: 14px;
        padding: 2px 8px;
        min-width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: #f0f0f0;
        color: #ff5252;
    }
    
    /* 食材项样式 */
    .ingredient-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 5px;
        border-radius: 5px;
        background-color: #f9f9f9;
        margin-bottom: 8px;
    }
    
    /* 页面内容居中 */
    .centered-container {
        width: 100%;
        max-width: 700px;
        margin: 0 auto;
    }
    
    /* 菜谱卡片样式 */
    .recipe-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #f9f9f9;
        width: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* 菜谱标题样式 */
    .recipe-title {
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
    }
    
    /* 标签样式 */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 12px;
        margin-right: 5px;
        margin-bottom: 5px;
    }
    
    /* 标签颜色 */
    .badge-easy {background-color: #C8E6C9; color: #2E7D32;}
    .badge-medium {background-color: #FFE0B2; color: #E65100;}
    .badge-hard {background-color: #FFCDD2; color: #B71C1C;}
    .badge-time {background-color: #E1F5FE; color: #0288D1;}
    
    /* 语言选择器位置 */
    .language-selector {
        position: absolute;
        top: 10px;
        right: 10px;
    }
    
    /* 页面导航按钮样式 */
    .nav-button {
        margin-top: 30px;
        margin-bottom: 20px;
    }
    
    /* 页面头部和标题样式 */
    h1, h2, h3 {
        text-align: center;
        margin-bottom: 20px;
        font-weight: normal;
    }
    
    /* 视频容器样式 */
    .youtube-container {
        margin-top: 20px;
        margin-bottom: 20px;
        width: 100%;
    }
    
    /* 分隔符样式 */
    hr {
        margin-top: 30px;
        margin-bottom: 30px;
    }
    
    /* 图片居中显示 */
    .image-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
    
    /* 表单项样式 */
    .form-item {
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


def scroll_to_top():
    st.components.v1.html(
        """
        <script>
            window.onload = function() {
                window.scrollTo(0, 0);
            }
        </script>
        """,
        height=0
    )

# 获取YouTube视频链接
def get_youtube_link(recipe_name, language="en"):
    """基于菜谱名称获取YouTube链接"""
    # 如果已有YouTube API密钥，使用API搜索
    if YOUTUBE_API_KEY:
        try:
            import requests
            
            # 构建搜索查询
            search_query = recipe_name

            
            # 构建YouTube Data API请求
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query,
                'key': YOUTUBE_API_KEY,
                'maxResults': 1,
                'type': 'video',
                'videoEmbeddable': 'true',
            }
            
            # 发送请求
            response = requests.get(url, params=params)
            data = response.json()
            
            # 如果有结果，返回第一个视频的链接
            if 'items' in data and len(data['items']) > 0:
                video_id = data['items'][0]['id']['videoId']
                return f"https://www.youtube.com/embed/{video_id}"
        
        except Exception as e:
            st.warning(f"YouTube API error: {str(e)}")
            # 如果没有API密钥或API调用失败，使用默认数据
    
    # 如果没有API密钥或API调用失败，使用常规定义的视频链接
    video_links = {
        "en": {
            "scrambled eggs with tomatoes": "https://www.youtube.com/embed/Uu5zGHjRaMo",
            "stir-fried potato": "https://www.youtube.com/embed/MU9RUCo_HZM",
            "steamed shrimp": "https://www.youtube.com/embed/rbDScJAZQrY",
            "default": "https://www.youtube.com/embed/dA9q_GXYOPo"
        },
        "zh": {
            "番茄炒蛋": "https://www.youtube.com/embed/Uu5zGHjRaMo",
            "青椒土豆丝": "https://www.youtube.com/embed/MU9RUCo_HZM",
            "蒜蓉蒸虾": "https://www.youtube.com/embed/rbDScJAZQrY",
            "default": "https://www.youtube.com/embed/dA9q_GXYOPo"
        }
    }
    
    # 将菜谱名称转为小写用于匹配
    recipe_name_lower = recipe_name.lower()
    
    # 查找匹配的视频链接
    for key in video_links[language]:
        if key in recipe_name_lower and key != "default":
            selected_link = video_links[language][key]
            print(f"[YouTube] Matched preset: {key} → {selected_link}")
            return selected_link

    # 如果没有匹配，返回默认视频
    default_link = video_links[language]["default"]
    print(f"[YouTube] No match for: {recipe_name} → using default: {default_link}")
    return default_link

# 隐私声明
def show_privacy_notice(texts):
    with st.expander(texts["privacy_title"], expanded=False):
        st.write(texts["privacy_text"])

# 自定义错误处理函数
def show_error(message):
    st.error(message)

# 初始化聊天助手
def init_agent():
    if 'agent' not in st.session_state:
        language = st.session_state.get('language', 'en')
        st.session_state.agent = FridgeChefAgent(language)
    return st.session_state.agent

# 上传照片页面
def upload_page(texts):
    # 主页标题放在居中容器内
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    st.title(texts["title"])
    st.subheader(texts["subtitle"])
    
    st.header(texts["step1_title"])
    # 添加分隔线
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 居中显示上传区域
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(texts["upload_photo"], type=["jpg", "jpeg", "png"])
        
        if st.button(texts["take_photo"], key="capture"):
            st.info(texts["photo_hint"])
    
    if uploaded_file is not None:
        try:
            # 显示上传的图片
            image = Image.open(uploaded_file)
            
            # 居中显示图片
            st.image(image, caption=texts["uploaded_photo"], use_column_width=True)
            
            # 中心化确认按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(texts["confirm_and_recognize"], key="confirm_image"):
                    # 使用Agent识别图片中的食材
                    with st.spinner(texts["recognizing"]):
                        # 初始化聊天助手
                        agent = init_agent()
                        
                        start_time = time.time()
                        # 使用Agent处理图片
                        result = agent.process_image(image)
                        recognized_ingredients = result
                        end_time = time.time()
                        
                        # 如果识别时间超过5秒，显示警告
                        if end_time - start_time > 5:
                            st.warning(texts["recognition_slow"])
                        
                        # 如果识别结果为空
                        if not recognized_ingredients:
                            st.warning(texts["no_ingredients"])
                            recognized_ingredients = []
                        
                        # 保存识别结果到会话状态
                        st.session_state.ingredients = recognized_ingredients
                        # 设置页面为第2步
                        st.session_state.page = 2
                        # 触发页面重载
                        st.experimental_rerun()
                
        except Exception as e:
            show_error(f"{texts['recognizing']} {str(e)}")

# 确认食材页面
def confirm_ingredients_page(texts):
    scroll_to_top()
    # 使用居中容器包裹整个页面内容
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    st.title(texts["title"])
    st.header(texts["step2_title"])
    # 添加分隔线
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 初始化食材列表
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = []
    
    edited_ingredients = list(st.session_state.ingredients)  # 复制一份以便编辑
    
    # 显示当前选择的食材列表
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    st.subheader(texts["current_ingredients"])
    
    if edited_ingredients:
        # 修改为移动视图友好的布局
        for i, ingredient in enumerate(edited_ingredients):
            cols = st.columns([4, 1])
            with cols[0]:
                st.write(ingredient)
            with cols[1]:
                if st.button("×", key=f"delete_{i}", help="删除"):
                    edited_ingredients.pop(i)
                    st.session_state.ingredients = edited_ingredients
                    st.experimental_rerun()
    else:
        st.info(texts["no_ingredients"])
    
    # 在当前食材与添加食材部分之间添加分隔线
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 添加手动添加食材的功能
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    st.subheader(texts["add_more"])
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_ingredient = st.text_input(
            label=texts["ingredient_name"],
            key="new_ingredient",
            label_visibility="collapsed"
        )
    with col2:
        if st.button(texts["add_button"]):
            if new_ingredient:
                if len(edited_ingredients) >= 15:
                    st.warning(texts["max_ingredients"])
                elif new_ingredient.lower() in [ing.lower() for ing in edited_ingredients]:
                    st.warning(texts["already_added"])
                else:
                    edited_ingredients.append(new_ingredient)
                    st.session_state.ingredients = edited_ingredients
                    st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 在添加食材与饮食限制部分之间添加分隔线
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 添加饮食限制输入框
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    st.subheader(texts.get("dietary_restrictions", "Dietary Restrictions"))
    st.text_area(
        label=texts.get("dietary_description", "Enter any dietary restrictions or preferences"),
        value=st.session_state.get("dietary_restrictions", ""),
        key="dietary_restrictions",
        label_visibility="collapsed",
        height=20  # 减小文本框高度
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 添加下一步按钮和返回按钮，左右对齐
    st.markdown("<div class='nav-button'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    # 左侧：返回按钮
    with col1:
        if st.button(texts["back_button"], key="btn_back"):
            st.session_state.page = 1
            st.experimental_rerun()

    # 中间空出来，什么都不放
    # col2 不写

    # 右侧：下一步按钮
    with col3:
        if st.button(texts["next_button"], key="btn_next"):
            if edited_ingredients:
                st.session_state.ingredients = edited_ingredients
                st.session_state.page = 3
                st.experimental_rerun()
            else:
                st.warning(texts["no_ingredients"])

    st.markdown("</div>", unsafe_allow_html=True)
# 菜谱生成页面
def recipe_page(texts):
    # 使用居中容器包裹整个页面内容
    scroll_to_top()
    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    st.title(texts["title"])
    st.header(texts["step3_title"])
    # 添加分隔线
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 初始化聊天助手
    agent = init_agent()
    
    # 判断是否已生成菜谱
    if "recipes" not in st.session_state or not st.session_state.recipes:
        # 自动生成菜谱
        with st.spinner(texts["generating"]):
            try:
                st.session_state.loading = True
                
                # 使用Agent生成菜谱
                dietary_restrictions = st.session_state.get('dietary_restrictions', '')
                recipes = agent.generate_recipes(
                    st.session_state.ingredients, 
                    dietary_restrictions
                )
                
                st.session_state.recipes = recipes
                st.session_state.loading = False
                st.experimental_rerun()
            except Exception as e:
                st.session_state.loading = False
                show_error(f"{texts['recipe_error']}: {str(e)}")
                st.warning(texts["retry_different"])
    else:
        # 显示菜谱内容
        for i, recipe in enumerate(st.session_state.recipes):
            st.subheader(f"{i+1}. {recipe['name']}")
            
            # 创建菜谱卡片
            with st.expander("View Recipe", expanded=i==0):
                st.markdown(f"""
                <div class="recipe-card">
                    <div class="recipe-title">{recipe['name']}</div>
                    <div style="text-align: center; margin-bottom: 15px;">
                        <span class="badge badge-{'easy' if recipe['difficulty']=='简单' or recipe['difficulty']=='Easy' else 'medium' if recipe['difficulty']=='中等' or recipe['difficulty']=='Medium' else 'hard'}">{recipe['difficulty']}</span>
                        <span class="badge badge-time">{recipe['time']}</span>
                    </div>
                    <ul>
                """, unsafe_allow_html=True)
                
                # 显示材料，标记哪些是已有的，哪些需要购买
                for material in recipe['materials']:
                    st.markdown(f"<li>{material}</li>", unsafe_allow_html=True)
                
                st.markdown("</ul>", unsafe_allow_html=True)
                
                # 显示烹饪步骤，不显示标题
                for j, step in enumerate(recipe['steps']):
                    st.write(f"{j+1}. {step}")
                
                # 获取并显示YouTube视频
                st.write(f"#### {texts['watch_video']}")
                
                # 直接使用get_youtube_link函数，不再使用GPT生成的链接
                video_link = get_youtube_link(recipe['name'], st.session_state.language)
                
                # 将视频链接转换为嵌入格式
                try:
                    if video_link and "watch?v=" in video_link:
                        # 将普通YouTube链接转换为嵌入链接
                        video_id = video_link.split("watch?v=")[1].split("&")[0]
                        embed_link = f"https://www.youtube.com/embed/{video_id}"
                    else:
                        # 如果不是标准的YouTube链接或链接为空，使用默认视频
                        embed_link = video_link
                    
                    # 显示视频嵌入
                    st.markdown(f"""
                    <div class="youtube-container">
                        <iframe width="100%" height="315" src="{embed_link}" 
                        frameborder="0" allow="accelerometer; autoplay; clipboard-write; 
                        encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    # 如果嵌入视频出错，显示错误信息并提供直接链接
                    if st.session_state.language == "zh":
                        error_msg = f"无法加载视频。您可以直接访问: {video_link}"
                    else:
                        error_msg = f"Unable to load video. You can visit directly: {video_link}"
                    st.error(error_msg)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # 重新生成按钮，居中显示
        st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(texts["regenerate"]):
                with st.spinner(texts["generating"]):
                    try:
                        # 使用Agent重新生成菜谱
                        dietary_restrictions = st.session_state.get('dietary_restrictions', '')
                        recipes = agent.generate_recipes(
                            st.session_state.ingredients,
                            dietary_restrictions
                        )
                        
                        st.session_state.recipes = recipes
                        st.experimental_rerun()
                    except Exception as e:
                        show_error(f"{texts['recipe_error']}: {str(e)}")
    
    # 导航按钮
    st.markdown("<div class='nav-button'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(texts["back_button"]):
            st.session_state.page = 2
            st.experimental_rerun()
    
    with col3:
        if st.button(texts["start_over"]):
            # 重置会话状态
            for key in list(st.session_state.keys()):
                if key not in ["language", "agent"]:
                    del st.session_state[key]
            st.session_state.page = 1
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # API调用次数限制提示
    if 'api_calls' not in st.session_state:
        st.session_state.api_calls = 0
    
    if st.session_state.api_calls >= 5:
        st.warning(texts["api_limit"])
    
    st.markdown("</div>", unsafe_allow_html=True)  # 关闭居中容器
    



# 主函数
def main():
    # 初始化语言设置
    if 'language' not in st.session_state:
        st.session_state.language = "en"  # 默认英文
    
    # 语言选择器
    col_space, col_lang = st.columns([3, 1])
    with col_lang:
        selected_lang = st.selectbox(
            label="Language/语言",
            options=["English", "中文"],
            index=0 if st.session_state.language == "en" else 1,
            label_visibility="collapsed"
        )
        
        if selected_lang == "English" and st.session_state.language != "en":
            st.session_state.language = "en"
            # 更新Agent语言
            if 'agent' in st.session_state:
                st.session_state.agent.language = "en"
            st.experimental_rerun()
        elif selected_lang == "中文" and st.session_state.language != "zh":
            st.session_state.language = "zh"
            # 更新Agent语言
            if 'agent' in st.session_state:
                st.session_state.agent.language = "zh"
            st.experimental_rerun()
    
    # 获取当前语言的文本
    texts = TRANSLATIONS[st.session_state.language]
    
    # 初始化页面状态
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    # 初始化会话状态变量
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = []
    
    if 'loading' not in st.session_state:
        st.session_state.loading = False
    
    # 初始化饮食限制
    if 'dietary_restrictions' not in st.session_state:
        st.session_state.dietary_restrictions = ""
    
    # 根据页面状态显示对应页面
    if st.session_state.page == 1:
        upload_page(texts)
    elif st.session_state.page == 2:
        confirm_ingredients_page(texts)
    elif st.session_state.page == 3:
        recipe_page(texts)
    
        # 页脚已移除

if __name__ == "__main__":
    main() 