"""
Embedding 封装 - 本地模型加载与编码
"""

import os
import sys
import warnings
from typing import List, Union
import numpy as np

# 禁用警告信息
warnings.filterwarnings('ignore')

# 设置环境变量禁用各种进度条和日志
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'

# 禁用 tqdm 进度条（safetensors 使用）
try:
    from tqdm import tqdm
    from functools import partialmethod
    tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
except:
    pass

from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL


class Embedder:
    """
    Embedding 模型封装类
    """
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        初始化 Embedding 模型
        
        Args:
            model_name: 模型名称或路径
        """
        self.model_name = model_name
        self.model = None
    
    def load_model(self):
        """
        加载模型（延迟加载）
        优先从本地缓存加载，避免每次联网检查更新
        """
        if self.model is None:
            print(f"正在加载 Embedding 模型: {self.model_name}")
            try:
                # 尝试离线模式加载，设置 local_files_only=True 避免联网检查
                # device='cpu' 避免不必要的 GPU 检测信息
                self.model = SentenceTransformer(
                    self.model_name, 
                    local_files_only=True,
                    device='cpu'
                )
            except Exception:
                # 如果本地没有模型，则联网下载（仅在第一次运行时触发）
                print(f"本地未找到模型 {self.model_name}，正在从 Hugging Face 联网下载...")
                self.model = SentenceTransformer(self.model_name, device='cpu')
            print("模型加载完成!")
        return self.model
    
    def encode(self, texts: Union[str, List[str]], show_progress: bool = False) -> np.ndarray:
        """
        将文本编码为向量
        
        Args:
            texts: 单个文本或文本列表
            show_progress: 是否显示进度条
            
        Returns:
            向量数组
        """
        self.load_model()
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts, 
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def get_dimension(self) -> int:
        """
        获取向量维度
        
        Returns:
            向量维度
        """
        self.load_model()
        return self.model.get_sentence_embedding_dimension()


# 全局单例
_embedder_instance = None


def get_embedder() -> Embedder:
    """
    获取全局 Embedder 实例
    
    Returns:
        Embedder 实例
    """
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance
