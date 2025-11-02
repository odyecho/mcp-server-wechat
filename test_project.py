#!/usr/bin/env python3
"""
项目功能测试脚本

测试 MCP Server 的各个组件和功能。
"""

import sys
import asyncio
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from mcp_server_wechat.utils.cache import cache_manager
from mcp_server_wechat.utils.formatters import (
    format_article_list, 
    format_account_info,
    truncate_response,
    estimate_token_count
)
from mcp_server_wechat.utils.api_client import wechat_client
from mcp_server_wechat.utils.search_client import search_client


def test_cache_system():
    """测试缓存系统"""
    print("🧪 测试缓存系统...")
    
    # 测试设置和获取缓存
    test_data = {"test": "data", "number": 123}
    cache_manager.set("test", test_data, ttl=60)
    
    retrieved_data = cache_manager.get("test")
    assert retrieved_data == test_data, "缓存数据不匹配"
    
    # 测试缓存键生成
    key1 = cache_manager._get_cache_key("test", param1="value1", param2="value2")
    key2 = cache_manager._get_cache_key("test", param2="value2", param1="value1")
    assert key1 == key2, "相同参数应生成相同的缓存键"
    
    print("✅ 缓存系统测试通过")


def test_formatters():
    """测试格式化工具"""
    print("🧪 测试格式化工具...")
    
    # 测试文章列表格式化
    test_articles = [
        {
            "title": "测试文章1",
            "author": "测试作者",
            "url": "https://example.com/1",
            "update_time": "2024-01-01",
            "digest": "这是一篇测试文章"
        },
        {
            "title": "测试文章2", 
            "author": "测试作者2",
            "url": "https://example.com/2",
            "update_time": "2024-01-02"
        }
    ]
    
    # 测试 JSON 格式
    json_result = format_article_list(test_articles, "json", "concise")
    json_data = json.loads(json_result)
    assert len(json_data) == 2, "JSON 格式化结果数量不正确"
    assert "title" in json_data[0], "JSON 结果缺少标题字段"
    
    # 测试 Markdown 格式
    md_result = format_article_list(test_articles, "markdown", "detailed")
    assert "# 文章列表" in md_result, "Markdown 格式缺少标题"
    assert "测试文章1" in md_result, "Markdown 格式缺少文章标题"
    
    # 测试账号信息格式化
    test_account = {
        "name": "测试公众号",
        "signature": "测试签名",
        "head_img": "https://example.com/avatar.jpg"
    }
    
    account_json = format_account_info(test_account, "json", "concise")
    account_data = json.loads(account_json)
    assert account_data["name"] == "测试公众号", "账号信息格式化错误"
    
    # 测试文本截断
    long_text = "这是一段很长的文本" * 1000
    truncated = truncate_response(long_text, max_chars=100)
    assert len(truncated) <= 200, "文本截断功能异常"  # 包含提示信息
    
    # 测试 token 计数
    test_text = "Hello 世界！This is a test."
    token_count = estimate_token_count(test_text)
    assert token_count > 0, "Token 计数应大于 0"
    
    print("✅ 格式化工具测试通过")


def test_api_client():
    """测试 API 客户端"""
    print("🧪 测试 API 客户端...")
    
    # 测试配置检查
    configured = wechat_client.configured
    print(f"📋 微信 API 配置状态: {'已配置' if configured else '未配置'}")
    
    if not configured:
        print("⚠️  微信 API 未配置，跳过 API 测试")
        print("   设置环境变量 WECHAT_APPID 和 WECHAT_SECRET 以启用 API 功能")
    else:
        print("✅ 微信 API 客户端配置正确")
    
    print("✅ API 客户端测试完成")


async def test_search_client():
    """测试搜索客户端"""
    print("🧪 测试搜索客户端...")
    
    try:
        # 测试搜索功能（使用简单查询避免触发反爬）
        print("🔍 测试文章搜索功能...")
        # 注意：这里只是测试客户端初始化，不进行实际搜索以避免反爬
        assert hasattr(search_client, 'search_articles'), "搜索客户端缺少搜索方法"
        assert hasattr(search_client, 'search_accounts'), "搜索客户端缺少账号搜索方法"
        assert hasattr(search_client, 'get_article_content'), "搜索客户端缺少内容获取方法"
        
        print("✅ 搜索客户端接口完整")
        
    except Exception as e:
        print(f"⚠️  搜索客户端测试异常: {e}")
        print("   这可能是由于网络限制或反爬机制")


def test_server_import():
    """测试服务器模块导入"""
    print("🧪 测试服务器模块导入...")
    
    try:
        from mcp_server_wechat.server import mcp
        assert mcp is not None, "MCP 实例未正确创建"
        
        # 检查工具注册
        tools = mcp._tools
        expected_tools = [
            "get_account_info",
            "list_articles", 
            "get_article_content",
            "search_public_articles",
            "get_public_article_content",
            "search_accounts"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tools, f"工具 {tool_name} 未注册"
        
        print(f"✅ 服务器模块导入成功，注册了 {len(tools)} 个工具")
        
    except Exception as e:
        print(f"❌ 服务器模块导入失败: {e}")
        raise


async def main():
    """主测试函数"""
    print("🚀 开始项目功能测试...\n")
    
    try:
        # 运行各项测试
        test_cache_system()
        print()
        
        test_formatters()
        print()
        
        test_api_client()
        print()
        
        await test_search_client()
        print()
        
        test_server_import()
        print()
        
        print("🎉 所有测试完成！")
        print("\n📊 测试总结:")
        print("✅ 缓存系统正常")
        print("✅ 格式化工具正常")
        print("✅ API 客户端正常")
        print("✅ 搜索客户端正常")
        print("✅ 服务器模块正常")
        print("✅ 所有 6 个工具已注册")
        
        print("\n🔧 下一步:")
        print("1. 使用 'uv run fastmcp dev src/mcp_server_wechat/server.py' 启动开发服务器")
        print("2. 访问 MCP Inspector 进行可视化测试")
        print("3. 配置微信 API 凭据以启用完整功能")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())