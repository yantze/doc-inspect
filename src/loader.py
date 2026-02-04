"""
文档加载器 - 递归扫描 md 文件夹
"""

import os
from pathlib import Path
from typing import List, Dict


def load_md_files(docs_dir: str) -> List[Dict]:
    """
    递归扫描指定目录下的所有 .md 文件
    
    Args:
        docs_dir: 文档目录路径
        
    Returns:
        文档列表 [{content, file_path, file_name}]
    """
    documents = []
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        raise FileNotFoundError(f"目录不存在: {docs_dir}")
    
    # 递归查找所有 .md 文件
    for md_file in docs_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            documents.append({
                "content": content,
                "file_path": str(md_file.absolute()),
                "file_name": md_file.name
            })
        except Exception as e:
            print(f"警告: 无法读取文件 {md_file}: {e}")
    
    return documents


def get_file_stats(documents: List[Dict]) -> Dict:
    """
    获取文档统计信息
    
    Args:
        documents: 文档列表
        
    Returns:
        统计信息字典
    """
    total_chars = sum(len(doc["content"]) for doc in documents)
    return {
        "total_files": len(documents),
        "total_chars": total_chars,
        "avg_chars": total_chars // len(documents) if documents else 0
    }
