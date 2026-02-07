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
    # 使用更高效的方式，避免在大文件上内存爆炸
    lines = content.split('\n')
    sections = []
    current_section = []
    
    for line in lines:
        # 检查是否是标题行
        if line.strip() and line.lstrip().startswith('#'):
            # 如果有累积的内容，先保存
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
        current_section.append(line)
    
    # 保存最后一个段落
    if current_section:
        sections.append('\n'.join(current_section))
    
    return [s for s in sections if s.strip()]


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
    text_len = len(text)
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        
        # 只在不是最后一块时才尝试句子边界分割
        if end < text_len:
            # 查找最近的句子结束符
            best_end = end
            search_start = max(start, end - 200)  # 只在最后 200 个字符中查找
            
            for sep in ['\n\n', '\n', '。', '！', '？', '.', '!', '?']:
                idx = text.find(sep, search_start, end)
                if idx > start:
                    # 找到分隔符，更新end
                    best_end = idx + len(sep)
                    break
            end = best_end
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # 计算下一个起始位置（带重叠）
        new_start = end - overlap
        
        # 确保始终向前移动，避免死循环
        if new_start <= start:
            new_start = end
        
        start = new_start
    
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
    
    for doc_idx, doc in enumerate(documents):
        content = doc["content"]
        file_path = doc["file_path"]
        file_name = doc["file_name"]
        
        # 打印进度（每 20 个文档）
        if (doc_idx + 1) % 20 == 0 or doc_idx == 0:
            print(f"   处理文档 {doc_idx + 1}/{len(documents)}: {file_name}")
        
        try:
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
        except Exception as e:
            print(f"   ⚠️  处理文档失败 {file_name}: {e}")
            # 继续处理其他文档
            continue
    
    return all_chunks
