import os

# 集中管理API密钥
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# YouTube Data API密钥
# 注意：需要在Google Cloud Console中创建项目并启用YouTube Data API v3
# 然后创建API密钥并替换下面的占位符
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# 其他可能的配置参数
MAX_API_CALLS_PER_HOUR = 5
DEFAULT_LANGUAGE = "en" 