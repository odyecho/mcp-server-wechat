#!/usr/bin/env python3
"""
测试微信MCP工具的功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

from mcp_server_wechat.server import (
    get_public_article_content,
    search_public_articles,
    GetPublicArticleContentInput,
    SearchPublicArticlesInput
)

async def test_get_article_content():
    """测试获取文章内容功能"""
    print("🔍 测试获取文章内容...")
    
    try:
        # 测试参数
        input_data = GetPublicArticleContentInput(
            article_url="https://mp.weixin.qq.com/s/ekzbhJccPqHT4z-F0V3Zjw",
            format="markdown",
            detail="detailed"
        )
        
        result = await get_public_article_content(input_data)
        print("✅ 获取文章内容成功!")
        print(f"📄 内容长度: {len(result)} 字符")
        print("📝 内容预览:")
        print("=" * 50)
        print(result[:500] + "..." if len(result) > 500 else result)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 获取文章内容失败: {e}")

async def test_search_articles():
    """测试搜索文章功能"""
    print("\n🔍 测试搜索文章...")
    
    try:
        # 测试参数
        input_data = SearchPublicArticlesInput(
            query="价值演算 霍华德·马克斯",
            limit=5,
            format="markdown",
            detail="concise"
        )
        
        result = await search_public_articles(input_data)
        print("✅ 搜索文章成功!")
        print(f"📄 结果长度: {len(result)} 字符")
        print("📝 搜索结果:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 搜索文章失败: {e}")

async def test_json_string_input():
    """测试JSON字符串输入"""
    print("\n🔍 测试JSON字符串输入...")
    
    try:
        # 模拟JSON字符串输入（这是之前失败的情况）
        json_input = '{"article_url": "https://mp.weixin.qq.com/s/ekzbhJccPqHT4z-F0V3Zjw", "format": "markdown", "detail": "concise"}'
        
        # 直接使用Pydantic模型解析
        input_data = GetPublicArticleContentInput.model_validate_json(json_input)
        print("✅ JSON字符串解析成功!")
        print(f"📄 解析结果: {input_data}")
        
        # 测试实际调用
        result = await get_public_article_content(input_data)
        print("✅ 使用JSON输入调用成功!")
        print(f"📄 内容长度: {len(result)} 字符")
        
    except Exception as e:
        print(f"❌ JSON字符串输入测试失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始测试微信MCP工具...")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 测试1: 搜索文章
    await test_search_articles()
    
    # 测试2: 获取文章内容
    await test_get_article_content()
    
    # 测试3: JSON字符串输入
    await test_json_string_input()
    
    print("\n🎉 测试完成!")

if __name__ == "__main__":
    asyncio.run(main())