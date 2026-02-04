"""
AI 服务模块 - OpenAI 兼容接口集成
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from config import (
    OPENAI_BASE_URL, 
    OPENAI_API_KEY, 
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKENS
)


class AIService:
    """
    AI 服务类，用于与 OpenAI 兼容的 API 进行交互
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化 AI 服务
        
        Args:
            base_url: API 基础 URL（可选，默认从配置读取）
            api_key: API 密钥（可选，默认从配置读取）
            model: 模型名称（可选，默认从配置读取）
        """
        # 优先使用传入参数，否则使用配置文件，最后使用环境变量
        self.base_url = base_url or OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL")
        self.api_key = api_key or OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.model = model or OPENAI_MODEL or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if not self.api_key or self.api_key == "your-api-key-here":
            raise ValueError(
                "未设置 API Key，请在 config.py 中设置 OPENAI_API_KEY "
                "或设置环境变量 OPENAI_API_KEY"
            )
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def generate_answer(
        self,
        question: str,
        contexts: List[str],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        基于检索到的上下文生成答案
        
        Args:
            question: 用户问题
            contexts: 检索到的相关文本列表
            temperature: 温度参数（可选）
            max_tokens: 最大生成长度（可选）
            
        Returns:
            包含答案和元信息的字典
        """
        # 构建上下文
        context_text = "\n\n".join([
            f"参考资料 {i+1}:\n{ctx}" 
            for i, ctx in enumerate(contexts)
        ])
        
        # 构建系统提示词
        system_prompt = """你是一个专业的技术文档助手。你的任务是根据提供的参考资料回答用户的问题。

回答要求：
1. 基于提供的参考资料回答问题
2. 如果参考资料中没有相关信息，请明确说明
3. 回答要准确、清晰、有条理
4. 如果可能，引用具体的参考资料编号"""
        
        # 构建用户提示词
        user_prompt = f"""参考资料:
{context_text}

问题: {question}

请基于以上参考资料回答问题。"""
        
        # 调用 AI 服务
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature or OPENAI_TEMPERATURE,
                max_tokens=max_tokens or OPENAI_MAX_TOKENS
            )
            
            # 提取答案，支持多种格式
            message = response.choices[0].message
            answer = None
            
            # 尝试从 content 获取（标准 OpenAI 格式）
            if message.content:
                answer = message.content
            # 尝试从 reasoning_content 获取（某些模型如 glm-4.7）
            elif hasattr(message, 'reasoning_content') and message.reasoning_content:
                answer = message.reasoning_content
            # 尝试从其他可能的字段获取
            elif hasattr(message, 'text') and message.text:
                answer = message.text
            else:
                answer = "[API 返回了响应但未找到答案内容]"
            
            return {
                "success": True,
                "answer": answer,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": None
            }
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        直接对话（不使用 RAG）
        
        Args:
            messages: 对话消息列表
            temperature: 温度参数（可选）
            max_tokens: 最大生成长度（可选）
            
        Returns:
            包含回复和元信息的字典
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or OPENAI_TEMPERATURE,
                max_tokens=max_tokens or OPENAI_MAX_TOKENS
            )
            
            reply = response.choices[0].message.content
            
            return {
                "success": True,
                "reply": reply,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "reply": None
            }


# 全局单例
_ai_service_instance = None


def get_ai_service(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> AIService:
    """
    获取全局 AIService 实例
    
    Args:
        base_url: API 基础 URL（可选）
        api_key: API 密钥（可选）
        model: 模型名称（可选）
        
    Returns:
        AIService 实例
    """
    global _ai_service_instance
    
    # 如果传入了自定义参数，创建新实例
    if base_url or api_key or model:
        return AIService(base_url=base_url, api_key=api_key, model=model)
    
    # 否则返回单例
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
