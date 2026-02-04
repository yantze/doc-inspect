#!/usr/bin/env python3
"""
MD 语义检索知识库 - 命令行入口
"""

import sys
import argparse
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from src.qa_engine import get_qa_engine
from config import TOP_K, OPENAI_BASE_URL, OPENAI_MODEL


console = Console()


def cmd_index(args):
    """
    建立索引命令
    """
    docs_dir = args.docs_dir
    
    if not Path(docs_dir).exists():
        console.print(f"[red]错误: 目录不存在: {docs_dir}[/red]")
        return
    
    console.print(Panel.fit(
        f"[bold blue]开始建立索引[/bold blue]\n目录: {docs_dir}",
        title="📚 MD 知识库"
    ))
    
    qa_engine = get_qa_engine()
    result = qa_engine.build_index(docs_dir, recreate=True)
    
    if result["success"]:
        console.print(Panel.fit(
            f"[green]索引建立成功![/green]\n"
            f"文件数: {result['total_files']}\n"
            f"文本块: {result['total_chunks']}\n"
            f"向量维度: {result['vector_dimension']}",
            title="✅ 完成"
        ))
    else:
        console.print(f"[red]索引建立失败: {result.get('message', '未知错误')}[/red]")


def cmd_query(args):
    """
    问答查询命令
    """
    qa_engine = get_qa_engine()
    
    # 检查索引是否存在
    stats = qa_engine.get_stats()
    if not stats.get("exists") or stats.get("count", 0) == 0:
        console.print("[yellow]警告: 索引为空，请先运行 index 命令建立索引[/yellow]")
        console.print("示例: python main.py index --docs-dir ./docs")
        return
    
    console.print(Panel.fit(
        f"[bold blue]MD 语义检索知识库[/bold blue]\n"
        f"索引文档块: {stats.get('count', 0)}\n"
        f"输入问题进行检索，输入 [bold]q[/bold] 或 [bold]quit[/bold] 退出",
        title="🔍 问答模式"
    ))
    
    top_k = args.top_k if hasattr(args, 'top_k') else TOP_K
    
    while True:
        try:
            console.print()
            question = console.input("[bold cyan]请输入问题: [/bold cyan]").strip()
            
            if not question:
                continue
            
            if question.lower() in ['q', 'quit', 'exit']:
                console.print("[green]再见！[/green]")
                break
            
            # 执行查询
            results = qa_engine.query(question, top_k=top_k)
            
            if not results:
                console.print("[yellow]未找到相关结果[/yellow]")
                continue
            
            # 显示结果
            console.print(f"\n[bold green]📚 找到 {len(results)} 个相关结果：[/bold green]\n")
            
            for i, result in enumerate(results, 1):
                score = result["score"]
                source = result["source_file"]
                text = result["text"]
                
                # 截断过长的文本
                if len(text) > 300:
                    text = text[:300] + "..."
                
                # 使用 Panel 显示结果
                panel_content = f"[dim]相似度: {score:.2f}[/dim]\n"
                panel_content += f"[dim]来源: {source}[/dim]\n\n"
                panel_content += text
                
                console.print(Panel(
                    panel_content,
                    title=f"[{i}]",
                    border_style="blue" if score > 0.7 else "dim"
                ))
        
        except KeyboardInterrupt:
            console.print("\n[green]再见！[/green]")
            break
        except Exception as e:
            console.print(f"[red]查询出错: {e}[/red]")


def cmd_stats(args):
    """
    显示统计信息命令
    """
    qa_engine = get_qa_engine()
    stats = qa_engine.get_stats()
    
    table = Table(title="📊 知识库统计")
    table.add_column("项目", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("索引状态", "✅ 已建立" if stats.get("exists") else "❌ 未建立")
    table.add_row("文档块数量", str(stats.get("count", 0)))
    
    console.print(table)


def cmd_ask(args):
    """
    AI 问答命令（RAG）
    """
    qa_engine = get_qa_engine()
    
    # 检查索引是否存在
    stats = qa_engine.get_stats()
    if not stats.get("exists") or stats.get("count", 0) == 0:
        console.print("[yellow]警告: 索引为空，请先运行 index 命令建立索引[/yellow]")
        console.print("示例: python main.py index --docs-dir ./docs")
        return
    
    # 获取 API 配置
    base_url = args.base_url if hasattr(args, 'base_url') and args.base_url else None
    api_key = args.api_key if hasattr(args, 'api_key') and args.api_key else None
    model = args.model if hasattr(args, 'model') and args.model else None
    top_k = args.top_k if hasattr(args, 'top_k') else TOP_K
    
    # 显示配置信息
    config_info = f"[bold blue]AI 问答模式[/bold blue]\n"
    config_info += f"索引文档块: {stats.get('count', 0)}\n"
    config_info += f"模型: {model or OPENAI_MODEL}\n"
    if base_url:
        config_info += f"API: {base_url}\n"
    config_info += f"\n输入问题，AI 将基于知识库回答\n"
    config_info += f"输入 [bold]q[/bold] 或 [bold]quit[/bold] 退出"
    
    console.print(Panel.fit(config_info, title="🤖 RAG 问答"))
    
    while True:
        try:
            console.print()
            question = console.input("[bold cyan]请输入问题: [/bold cyan]").strip()
            
            if not question:
                continue
            
            if question.lower() in ['q', 'quit', 'exit']:
                console.print("[green]再见！[/green]")
                break
            
            # 显示检索进度
            with console.status("[bold green]正在检索知识库...", spinner="dots"):
                result = qa_engine.ask_with_ai(
                    question,
                    top_k=top_k,
                    base_url=base_url,
                    api_key=api_key,
                    model=model
                )
            
            if not result.get("success"):
                console.print(f"[red]错误: {result.get('error', '未知错误')}[/red]")
                if "API Key" in result.get('error', ''):
                    console.print("\n[yellow]提示：[/yellow]")
                    console.print("1. 在 config.py 中设置 OPENAI_API_KEY")
                    console.print("2. 或者设置环境变量: export OPENAI_API_KEY='your-key'")
                    console.print("3. 或者使用 --api-key 参数传入")
                continue
            
            # 显示 AI 回答
            console.print("\n[bold green]🤖 AI 回答：[/bold green]\n")
            console.print(Panel(
                result["answer"],
                title="答案",
                border_style="green",
                expand=False,
                width=None  # 不限制宽度
            ))
            
            # 显示使用的 token
            if "usage" in result:
                usage = result["usage"]
                console.print(
                    f"\n[dim]Token 使用: 输入 {usage['prompt_tokens']} | "
                    f"输出 {usage['completion_tokens']} | "
                    f"总计 {usage['total_tokens']}[/dim]"
                )
            
            # 显示参考文档
            console.print(f"\n[bold blue]📚 参考文档 ({result.get('context_count', 0)} 个)：[/bold blue]")
            for i, ctx in enumerate(result.get("contexts", []), 1):
                score = ctx["score"]
                source = ctx["source_file"]
                text = ctx["text"]
                
                # 截断过长的文本
                if len(text) > 150:
                    text = text[:150] + "..."
                
                console.print(
                    f"\n[cyan][{i}][/cyan] [dim]相似度: {score:.2f} | 来源: {source}[/dim]\n"
                    f"    {text}"
                )
        
        except KeyboardInterrupt:
            console.print("\n[green]再见！[/green]")
            break
        except Exception as e:
            console.print(f"[red]查询出错: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


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
