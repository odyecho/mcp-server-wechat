#!/usr/bin/env python3
"""
直接测试微信搜索功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

from mcp_server_wechat.utils.search_client import search_client
from mcp_server_wechat.utils.formatters import format_article_content, format_search_results

async def test_search_articles():
    """测试搜索文章功能"""
    print("🔍 测试搜索文章...")
    
    try:
        results = await search_client.search_articles(
            query="价值演算 霍华德·马克斯",
            limit=3
        )
        
        print("✅ 搜索文章成功!")
        print(f"📄 找到 {len(results)} 篇文章")
        
        for i, article in enumerate(results, 1):
            print(f"\n📝 文章 {i}:")
            print(f"   标题: {article.get('title', 'N/A')}")
            print(f"   作者: {article.get('account', 'N/A')}")
            print(f"   链接: {article.get('url', 'N/A')}")
            print(f"   时间: {article.get('time', 'N/A')}")
        
        return results
        
    except Exception as e:
        print(f"❌ 搜索文章失败: {e}")
        return []

async def test_get_article_content(url):
    """测试获取文章内容功能"""
    print(f"\n🔍 测试获取文章内容: {url}")
    
    try:
        article = await search_client.get_article_content(url)
        
        print("✅ 获取文章内容成功!")
        print(f"📄 标题: {article.get('title', 'N/A')}")
        print(f"📄 作者: {article.get('author', 'N/A')}")
        print(f"📄 发布时间: {article.get('publish_time', 'N/A')}")
        print(f"📄 内容长度: {len(article.get('content', ''))} 字符")
        
        # 显示内容预览
        content = article.get('content', '')
        if content:
            print("\n📝 内容预览:")
            print("=" * 50)
            preview = content[:300] + "..." if len(content) > 300 else content
            print(preview)
            print("=" * 50)
        
        return article
        
    except Exception as e:
        print(f"❌ 获取文章内容失败: {e}")
        return None

async def test_target_article():
    """测试目标文章"""
    target_url = "https://mp.weixin.qq.com/s/ekzbhJccPqHT4z-F0V3Zjw"
    
    print(f"🎯 直接测试目标文章: {target_url}")
    
    article = await test_get_article_content(target_url)
    
    if article:
        # 测试格式化
        print("\n🔧 测试Markdown格式化...")
        formatted = format_article_content(article, "markdown", "detailed")
        print(f"📄 格式化后长度: {len(formatted)} 字符")
        
        print("\n📝 格式化预览:")
        print("=" * 50)
        preview = formatted[:500] + "..." if len(formatted) > 500 else formatted
        print(preview)
        print("=" * 50)

async def main():
    """主测试函数"""
    print("🚀 开始直接测试微信搜索功能...")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 测试1: 搜索相关文章
    search_results = await test_search_articles()
    
    # 测试2: 直接获取目标文章
    await test_target_article()
    
    # 测试3: 如果搜索到结果，测试第一个
    if search_results:
        first_article = search_results[0]
        if 'url' in first_article:
            print(f"\n🔍 测试搜索结果中的第一篇文章...")
            await test_get_article_content(first_article['url'])
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    asyncio.run(main())