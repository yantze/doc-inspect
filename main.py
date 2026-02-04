#!/usr/bin/env python3
"""
MD 语义检索知识库 - 命令行入口
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from src.cli_commands import cmd_index, cmd_query, cmd_ask, cmd_stats
from config import TOP_K


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(
        description="MD 语义检索知识库 - 基于 Milvus Lite 的本地知识库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  建立索引:  python main.py index --docs-dir ./docs
  语义查询:  python main.py query
  AI 问答:   python main.py ask
  查看统计:  python main.py stats
  
使用自定义 API:
  python main.py ask --base-url https://api.example.com/v1 --api-key YOUR_KEY --model gpt-4
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # index 命令
    index_parser = subparsers.add_parser("index", help="建立索引")
    index_parser.add_argument(
        "--docs-dir", "-d",
        type=str,
        default="./docs",
        help="md 文档目录路径 (默认: ./docs)"
    )
    
    # query 命令
    query_parser = subparsers.add_parser("query", help="问答查询")
    query_parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=TOP_K,
        help=f"返回结果数量 (默认: {TOP_K})"
    )
    
    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示统计信息")
    
    # ask 命令
    ask_parser = subparsers.add_parser("ask", help="AI 问答模式（RAG）")
    ask_parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=TOP_K,
        help=f"检索文档数量 (默认: {TOP_K})"
    )
    ask_parser.add_argument(
        "--base-url",
        type=str,
        help="OpenAI 兼容 API 地址"
    )
    ask_parser.add_argument(
        "--api-key",
        type=str,
        help="API 密钥"
    )
    ask_parser.add_argument(
        "--model", "-m",
        type=str,
        help="模型名称"
    )
    
    args = parser.parse_args()
    
    if args.command == "index":
        cmd_index(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "ask":
        cmd_ask(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
