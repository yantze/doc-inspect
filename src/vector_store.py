"""
向量存储 - Milvus Lite 封装
"""

from typing import List, Dict, Optional
from pymilvus import MilvusClient
from config import MILVUS_DB_PATH, COLLECTION_NAME, VECTOR_DIM, TOP_K


class VectorStore:
    """
    Milvus Lite 向量存储封装类
    """
    
    def __init__(self, db_path: str = MILVUS_DB_PATH, collection_name: str = COLLECTION_NAME):
        """
        初始化向量存储
        
        Args:
            db_path: 数据库文件路径
            collection_name: 集合名称
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = None
    
    def connect(self):
        """
        连接到 Milvus Lite
        """
        if self.client is None:
            self.client = MilvusClient(self.db_path)
        return self.client
    
    def create_collection(self, dimension: int = VECTOR_DIM, recreate: bool = False):
        """
        创建集合
        
        Args:
            dimension: 向量维度
            recreate: 是否重新创建（删除旧集合）
        """
        self.connect()
        
        # 检查集合是否存在
        if self.client.has_collection(self.collection_name):
            if recreate:
                print(f"删除旧集合: {self.collection_name}")
                self.client.drop_collection(self.collection_name)
            else:
                print(f"集合已存在: {self.collection_name}")
                return
        
        # 创建新集合
        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=dimension,
            metric_type="COSINE"  # 使用余弦相似度
        )
        print(f"创建集合成功: {self.collection_name}, 维度: {dimension}")
    
    def insert(self, vectors: List[List[float]], metadata: List[Dict]) -> List[int]:
        """
        插入向量和元数据
        
        Args:
            vectors: 向量列表
            metadata: 元数据列表 [{chunk_text, source_file, file_path, chunk_index}]
            
        Returns:
            插入的 ID 列表
        """
        self.connect()
        
        # 构建插入数据
        data = []
        for i, (vector, meta) in enumerate(zip(vectors, metadata)):
            data.append({
                "id": i,
                "vector": vector,
                "text": meta["chunk_text"],
                "source_file": meta["source_file"],
                "file_path": meta["file_path"],
                "chunk_index": meta["chunk_index"]
            })
        
        # 插入数据
        result = self.client.insert(
            collection_name=self.collection_name,
            data=data
        )
        
        return result.get("ids", [])
    
    def search(self, query_vector: List[float], top_k: int = TOP_K) -> List[Dict]:
        """
        相似度搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表 [{id, distance, text, source_file, file_path}]
        """
        self.connect()
        
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["text", "source_file", "file_path", "chunk_index"]
        )
        
        # 格式化结果
        formatted_results = []
        if results and len(results) > 0:
            for hit in results[0]:
                formatted_results.append({
                    "id": hit["id"],
                    "score": 1 - hit["distance"],  # 转换为相似度分数
                    "text": hit["entity"].get("text", ""),
                    "source_file": hit["entity"].get("source_file", ""),
                    "file_path": hit["entity"].get("file_path", ""),
                    "chunk_index": hit["entity"].get("chunk_index", 0)
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """
        获取集合统计信息
        
        Returns:
            统计信息字典
        """
        self.connect()
        
        if not self.client.has_collection(self.collection_name):
            return {"exists": False, "count": 0}
        
        stats = self.client.get_collection_stats(self.collection_name)
        return {
            "exists": True,
            "count": stats.get("row_count", 0)
        }
    
    def close(self):
        """
        关闭连接
        """
        if self.client:
            self.client.close()
            self.client = None


# 全局单例
_vector_store_instance = None


def get_vector_store() -> VectorStore:
    """
    获取全局 VectorStore 实例
    
    Returns:
        VectorStore 实例
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
