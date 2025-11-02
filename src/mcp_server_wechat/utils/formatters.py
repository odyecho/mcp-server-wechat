"""
响应格式化工具

提供 JSON 和 Markdown 格式的响应格式化功能。
"""

import json
from typing import Any, Dict, List, Literal
from datetime import datetime


def format_article_list(
    articles: List[Dict[str, Any]], 
    format: Literal["json", "markdown"],
    detail: Literal["concise", "detailed"]
) -> str:
    """格式化文章列表"""
    if format == "json":
        if detail == "concise":
            simplified = []
            for article in articles:
                simplified.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "update_time": article.get("update_time", ""),
                    "author": article.get("author", "")
                })
            return json.dumps(simplified, ensure_ascii=False, indent=2)
        else:
            return json.dumps(articles, ensure_ascii=False, indent=2)
    
    else:  # markdown
        lines = ["# 文章列表\n"]
        for i, article in enumerate(articles, 1):
            title = article.get("title", "无标题")
            author = article.get("author", "未知作者")
            update_time = article.get("update_time", "")
            url = article.get("url", "")
            
            lines.append(f"## {i}. {title}")
            lines.append(f"**作者**: {author}")
            if update_time:
                lines.append(f"**更新时间**: {update_time}")
            if url:
                lines.append(f"**链接**: [查看原文]({url})")
                
            if detail == "detailed":
                digest = article.get("digest", "")
                if digest:
                    lines.append(f"**摘要**: {digest}")
                    
            lines.append("")  # 空行分隔
            
        return "\n".join(lines)


def format_article_content(
    article: Dict[str, Any],
    format: Literal["json", "markdown"],
    detail: Literal["concise", "detailed"],
    include_html: bool = False
) -> str:
    """格式化文章内容"""
    if format == "json":
        if detail == "concise":
            content = article.get("content", "")
            if len(content) > 1000:
                content = content[:1000] + "..."
            return json.dumps({
                "title": article.get("title", ""),
                "author": article.get("author", ""),
                "content": content,
                "url": article.get("url", "")
            }, ensure_ascii=False, indent=2)
        else:
            result = article.copy()
            if not include_html and "content_html" in result:
                del result["content_html"]
            return json.dumps(result, ensure_ascii=False, indent=2)
    
    else:  # markdown
        lines = []
        title = article.get("title", "无标题")
        author = article.get("author", "未知作者")
        content = article.get("content", "")
        
        lines.append(f"# {title}\n")
        lines.append(f"**作者**: {author}")
        
        if detail == "detailed":
            update_time = article.get("update_time", "")
            if update_time:
                lines.append(f"**发布时间**: {update_time}")
                
            digest = article.get("digest", "")
            if digest:
                lines.append(f"**摘要**: {digest}")
                
            url = article.get("url", "")
            if url:
                lines.append(f"**原文链接**: [查看原文]({url})")
                
        lines.append("\n## 正文\n")
        lines.append(content)
        
        return "\n".join(lines)


def format_account_info(
    account_info: Dict[str, Any],
    format: Literal["json", "markdown"],
    detail: Literal["concise", "detailed"]
) -> str:
    """格式化公众号信息"""
    if format == "json":
        if detail == "concise":
            return json.dumps({
                "name": account_info.get("name", ""),
                "type": account_info.get("type", ""),
                "verified": account_info.get("verified", False),
                "status": account_info.get("status", "")
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps(account_info, ensure_ascii=False, indent=2)
    
    else:  # markdown
        lines = ["# 公众号信息\n"]
        
        name = account_info.get("name", "未知")
        account_type = account_info.get("type", "未知")
        verified = account_info.get("verified", False)
        status = account_info.get("status", "未知")
        
        lines.append(f"**名称**: {name}")
        lines.append(f"**类型**: {account_type}")
        lines.append(f"**认证状态**: {'已认证' if verified else '未认证'}")
        lines.append(f"**状态**: {status}")
        
        if detail == "detailed":
            stats = account_info.get("stats", {})
            if stats:
                lines.append("\n## 统计信息")
                for key, value in stats.items():
                    lines.append(f"**{key}**: {value}")
                    
            api_quota = account_info.get("api_quota", {})
            if api_quota:
                lines.append("\n## API 配额")
                for key, value in api_quota.items():
                    lines.append(f"**{key}**: {value}")
        
        return "\n".join(lines)


def format_search_results(
    results: List[Dict[str, Any]],
    format: Literal["json", "markdown"],
    detail: Literal["concise", "detailed"]
) -> str:
    """格式化搜索结果"""
    if format == "json":
        if detail == "concise":
            simplified = []
            for result in results:
                simplified.append({
                    "title": result.get("title", ""),
                    "account": result.get("account", ""),
                    "url": result.get("url", ""),
                    "publish_time": result.get("publish_time", "")
                })
            return json.dumps(simplified, ensure_ascii=False, indent=2)
        else:
            return json.dumps(results, ensure_ascii=False, indent=2)
    
    else:  # markdown
        lines = ["# 搜索结果\n"]
        for i, result in enumerate(results, 1):
            title = result.get("title", "无标题")
            account = result.get("account", "未知公众号")
            publish_time = result.get("publish_time", "")
            url = result.get("url", "")
            
            lines.append(f"## {i}. {title}")
            lines.append(f"**公众号**: {account}")
            if publish_time:
                lines.append(f"**发布时间**: {publish_time}")
            if url:
                lines.append(f"**链接**: [查看原文]({url})")
                
            if detail == "detailed":
                digest = result.get("digest", "")
                if digest:
                    lines.append(f"**摘要**: {digest}")
                    
                read_count = result.get("read_count", "")
                if read_count:
                    lines.append(f"**阅读量**: {read_count}")
                    
            lines.append("")  # 空行分隔
            
        return "\n".join(lines)


def truncate_response(text: str, max_chars: int = 100000) -> str:
    """截断过长的响应"""
    if len(text) <= max_chars:
        return text
        
    truncated = text[:max_chars]
    return f"""{truncated}

... [响应内容因长度限制被截断]

建议：
1. 使用 'concise' 详细级别
2. 分批获取内容
3. 使用更具体的搜索条件

完整内容字符数：{len(text)}
显示字符数：{max_chars}
"""


def estimate_token_count(text: str) -> int:
    """估算文本的 token 数量（粗略估算）"""
    # 中文字符按 1.5 个 token 计算，英文按 0.25 个 token 计算
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    other_chars = len(text) - chinese_chars
    
    return int(chinese_chars * 1.5 + other_chars * 0.25)