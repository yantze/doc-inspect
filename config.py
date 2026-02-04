"""
MD 语义检索知识库 - 配置文件
"""

# Embedding 模型配置
# 可选模型 (效果从强到弱):
# - "moka-ai/m3e-base" (中英文，768维，效果最好)
# - "BAAI/bge-base-zh-v1.5" (中文为主，768维)
# - "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" (多语言，384维，较小)
# - "sentence-transformers/all-MiniLM-L6-v2" (英文，384维，最小)
EMBEDDING_MODEL = "moka-ai/m3e-base"  # 中英文双语模型，效果最好
VECTOR_DIM = 768                       # 向量维度

# Milvus 配置
MILVUS_DB_PATH = "./data/milvus.db"   # 本地数据库路径
COLLECTION_NAME = "md_knowledge_base"  # 集合名称

# 文本分割配置
CHUNK_SIZE = 500                       # 分块大小（字符数）
CHUNK_OVERLAP = 50                     # 分块重叠（字符数）

# 检索配置
TOP_K = 5                              # 默认返回结果数量

# AI 服务配置 (OpenAI 兼容)
OPENAI_BASE_URL = "https://xxx/v1"  # OpenAI 兼容的 API 地址
OPENAI_API_KEY = "xxxi"           # API 密钥
OPENAI_MODEL = "glm-4.7"                 # 使用的模型名称
OPENAI_TEMPERATURE = 0.7                       # 温度参数
OPENAI_MAX_TOKENS = 100000                       # 最大回复长度（增加以支持更长的回答）
