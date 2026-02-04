"""
文本分割器 - 针对 Markdown 的智能分块
"""

import re
from typing import List, Dict
from config import CHUNK_SIZE, CHUNK_OVERLAP


def split_by_headers(content: str) -> List[str]:
    """
    按 Markdown 标题分割文档
    
    Args:
        content: Markdown 文本内容
        
    Returns:
        分割后的段落列表
    """
    # 按标题分割 (# ## ### 等)
    pattern = r'(^#{1,6}\s+.+$)'
    parts = re.split(pattern, content, flags=re.MULTILINE)
    
    sections = []
    current_section = ""
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        if re.match(r'^#{1,6}\s+', part):
            # 这是一个标题，如果有累积的内容，先保存
            if current_section:
                sections.append(current_section)
            current_section = part + "\n"
        else:
            current_section += part + "\n"
    
    # 保存最后一个段落
    if current_section:
        sections.append(current_section)
    
    return sections


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    将文本分割成指定大小的块
    
    Args:
        text: 输入文本
        chunk_size: 每块的最大字符数
        overlap: 块之间的重叠字符数
        
    Returns:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 尝试在句子边界处分割
        if end < len(text):
            # 查找最近的句子结束符
            for sep in ['\n\n', '。', '！', '？', '.', '!', '?', '\n']:
                last_sep = text.rfind(sep, start, end)
                if last_sep > start:
                    end = last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start < 0:
            start = 0
    
    return chunks


def split_documents(documents: List[Dict], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """
    分割所有文档
    
    Args:
        documents: 文档列表
        chunk_size: 每块的最大字符数
        overlap: 块之间的重叠字符数
        
    Returns:
        分块列表 [{chunk_text, source_file, file_path, chunk_index}]
    """
    all_chunks = []
    
    for doc in documents:
        content = doc["content"]
        file_path = doc["file_path"]
        file_name = doc["file_name"]
        
        # 先按标题分割
        sections = split_by_headers(content)
        
        chunk_index = 0
        for section in sections:
            # 再按大小分割
            chunks = split_text(section, chunk_size, overlap)
            
            for chunk in chunks:
                if chunk.strip():
                    all_chunks.append({
                        "chunk_text": chunk,
                        "source_file": file_name,
                        "file_path": file_path,
                        "chunk_index": chunk_index
                    })
                    chunk_index += 1
    
    return all_chunks
