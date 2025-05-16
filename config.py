import os

# 集中管理API密钥
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))

# YouTube API 密钥
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", os.environ.get("YOUTUBE_API_KEY", ""))

# 其他可能的配置参数
MAX_API_CALLS_PER_HOUR = 5
DEFAULT_LANGUAGE = "en" 
