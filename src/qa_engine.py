"""
问答引擎 - 检索与问答核心逻辑
"""

from typing import List, Dict, Optional
from src.embedder import get_embedder
from src.vector_store import get_vector_store
from src.loader import load_md_files, get_file_stats
from src.splitter import split_documents
from src.ai_service import get_ai_service
from config import TOP_K


class QAEngine:
    """
    问答引擎类
    """
    
    def __init__(self):
        """
        初始化问答引擎
        """
        self.embedder = get_embedder()
        self.vector_store = get_vector_store()
        self.ai_service = None  # 延迟初始化
    
    def build_index(self, docs_dir: str, recreate: bool = True) -> Dict:
        """
        构建索引
        
        Args:
            docs_dir: 文档目录路径
            recreate: 是否重新创建索引
            
        Returns:
            构建结果统计
        """
        # 1. 加载文档
        print(f"\n📂 扫描目录: {docs_dir}")
        documents = load_md_files(docs_dir)
        file_stats = get_file_stats(documents)
        print(f"   找到 {file_stats['total_files']} 个 md 文件, 共 {file_stats['total_chars']} 字符")
        
        if not documents:
            return {"success": False, "message": "未找到任何 md 文件"}
        
        # 2. 分割文档
        print("\n✂️  分割文档...")
        chunks = split_documents(documents)
        print(f"   生成 {len(chunks)} 个文本块")
        
        # 3. 生成向量
        print("\n🔢 生成向量...")
        texts = [chunk["chunk_text"] for chunk in chunks]
        vectors = self.embedder.encode(texts, show_progress=True)
        print(f"   向量维度: {vectors.shape[1]}")
        
        # 4. 创建集合并插入数据
        print("\n💾 存储到向量数据库...")
        self.vector_store.create_collection(
            dimension=vectors.shape[1],
            recreate=recreate
        )
        
        # 将 numpy 数组转换为列表
        vectors_list = vectors.tolist()
        ids = self.vector_store.insert(vectors_list, chunks)
        print(f"   插入 {len(ids)} 条记录")
        
        return {
            "success": True,
            "total_files": file_stats["total_files"],
            "total_chunks": len(chunks),
            "vector_dimension": vectors.shape[1]
        }
    
    def query(self, question: str, top_k: int = TOP_K) -> List[Dict]:
        """
        查询问答
        
        Args:
            question: 用户问题
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        # 1. 将问题编码为向量
        query_vector = self.embedder.encode(question)[0].tolist()
        
        # 2. 在向量数据库中搜索
        results = self.vector_store.search(query_vector, top_k)
        
        return results
    
    def get_stats(self) -> Dict:
        """
        获取索引统计信息
        
        Returns:
            统计信息
        """
        return self.vector_store.get_collection_stats()
    
    def ask_with_ai(
        self,
        question: str,
        top_k: int = TOP_K,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict:
        """
        使用 AI 基于知识库回答问题（RAG）
        
        Args:
            question: 用户问题
            top_k: 检索结果数量
            base_url: API 基础 URL（可选）
            api_key: API 密钥（可选）
            model: 模型名称（可选）
            
        Returns:
            包含答案、检索结果和元信息的字典
        """
        # 1. 检索相关文档
        search_results = self.query(question, top_k)
        
        if not search_results:
            return {
                "success": False,
                "error": "未找到相关文档",
                "answer": None,
                "contexts": []
            }
        
        # 2. 提取上下文文本
        contexts = [result["text"] for result in search_results]
        
        # 3. 初始化或更新 AI 服务
        if base_url or api_key or model:
            self.ai_service = get_ai_service(base_url, api_key, model)
        elif self.ai_service is None:
            try:
                self.ai_service = get_ai_service()
            except ValueError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "answer": None,
                    "contexts": search_results
                }
        
        # 4. 使用 AI 生成答案
        ai_result = self.ai_service.generate_answer(question, contexts)
        
        # 5. 返回完整结果
        return {
            **ai_result,
            "contexts": search_results,
            "context_count": len(search_results)
        }


# 全局单例
_qa_engine_instance = None


def get_qa_engine() -> QAEngine:
    """
    获取全局 QAEngine 实例
    
    Returns:
        QAEngine 实例
    """
    global _qa_engine_instance
    if _qa_engine_instance is None:
        _qa_engine_instance = QAEngine()
    return _qa_engine_instance
