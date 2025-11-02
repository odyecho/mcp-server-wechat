"""
微信公众号 MCP Server

为 AI Agent 提供微信公众号文章访问和管理能力的 MCP Server。
"""

import os
import sys
import json
from pathlib import Path
from typing import Literal, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, model_validator
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from utils.api_client import wechat_client
from utils.search_client import search_client
from utils.formatters import (
    format_account_info, 
    format_article_list, 
    format_article_content,
    format_search_results,
    truncate_response
)
from utils.cache import cache_manager

# 创建 FastMCP 实例
mcp = FastMCP(
    name="WeChat Official Account MCP Server",
    instructions="A MCP server for accessing WeChat Official Account articles and content"
)


# 输入模型定义
class GetAccountInfoInput(BaseModel):
    model_config = {"extra": "forbid"}
    
    format: Literal["json", "markdown"] = Field(
        default="json",
        description="响应格式：json 返回结构化数据，markdown 返回可读文本"
    )
    
    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="详细程度：concise 返回基本信息，detailed 返回完整统计"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_json_string(cls, data: Any) -> Any:
        """解析 JSON 字符串输入"""
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return parsed
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试作为单个参数处理
                print(f"JSON解析失败: {e}, 原始数据: {data}")
                pass
        return data


class ListArticlesInput(BaseModel):
    model_config = {"extra": "forbid"}
    
    offset: int = Field(
        default=0,
        ge=0,
        description="偏移量，从第几条开始获取",
        examples=[0, 10, 20]
    )
    
    count: int = Field(
        default=10,
        ge=1,
        le=20,
        description="获取数量，最多20条",
        examples=[5, 10, 20]
    )
    
    format: Literal["json", "markdown"] = Field(
        default="json",
        description="响应格式"
    )
    
    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="详细程度"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_json_string(cls, data: Any) -> Any:
        """解析 JSON 字符串输入"""
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return parsed
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试作为单个参数处理
                print(f"JSON解析失败: {e}, 原始数据: {data}")
                pass
        return data


class GetArticleContentInput(BaseModel):
    model_config = {"extra": "forbid"}
    
    media_id: str = Field(
        description="文章的媒体ID，从 list_articles 获取",
        min_length=1,
        examples=["BM_Vc7hGvWUiRSqbROjwQ-qGHisVjia6tVPwl2r1NjqzjJFbkCBsZtDvSMJY8bL"]
    )
    
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="响应格式，推荐使用 markdown 以获得更好的可读性"
    )
    
    detail: Literal["concise", "detailed"] = Field(
        default="detailed",
        description="详细程度"
    )
    
    include_html: bool = Field(
        default=False,
        description="是否包含原始HTML内容（仅在 json 格式下有效）"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_json_string(cls, data: Any) -> Any:
        """解析 JSON 字符串输入"""
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return parsed
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试作为单个参数处理
                print(f"JSON解析失败: {e}, 原始数据: {data}")
                pass
        return data


class SearchPublicArticlesInput(BaseModel):
    model_config = {"extra": "forbid"}
    
    query: str = Field(
        description="搜索关键词，支持多个词语组合",
        min_length=1,
        max_length=100,
        examples=["人工智能", "ChatGPT 应用", "Python 教程"]
    )
    
    account_name: Optional[str] = Field(
        default=None,
        description="指定公众号名称（可选），用于精确搜索",
        examples=["机器之心", "AI科技大本营"]
    )
    
    limit: int = Field(
        default=10,
        ge=1,
        le=20,
        description="返回结果数量"
    )
    
    format: Literal["json", "markdown"] = Field(
        default="json",
        description="响应格式"
    )
    
    detail: Literal["concise", "detailed"] = Field(
        default="concise",
        description="详细程度"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_json_string(cls, data: Any) -> Any:
        """解析 JSON 字符串输入"""
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return parsed
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试作为单个参数处理
                print(f"JSON解析失败: {e}, 原始数据: {data}")
                pass
        return data


class GetPublicArticleContentInput(BaseModel):
    model_config = {"extra": "forbid"}
    
    article_url: str = Field(
        description="文章URL地址，通常来自搜索结果",
        pattern=r"^https?://mp\.weixin\.qq\.com/s/",
        examples=["https://mp.weixin.qq.com/s/abcdefghijk"]
    )
    
    format: Literal["json", "markdown"] = Field(
        default="markdown",
        description="响应格式"
    )
    
    detail: Literal["concise", "detailed"] = Field(
        default="detailed",
        description="详细程度"
    )
    
    extract_images: bool = Field(
        default=False,
        description="是否提取图片链接"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_json_string(cls, data: Any) -> Any:
        """解析 JSON 字符串输入"""
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return parsed
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试作为单个参数处理
                print(f"JSON解析失败: {e}, 原始数据: {data}")
                pass
        return data


class SearchAccountsInput(BaseModel):
    model_config = {"extra": "forbid"}
    
    query: str = Field(
        description="公众号名称或关键词",
        min_length=1,
        max_length=50,
        examples=["机器之心", "AI", "Python"]
    )
    
    limit: int = Field(
        default=10,
        ge=1,
        le=20,
        description="返回结果数量"
    )
    
    format: Literal["json", "markdown"] = Field(
        default="json",
        description="响应格式"
    )

    @model_validator(mode='before')
    @classmethod
    def parse_json_string(cls, data: Any) -> Any:
        """解析 JSON 字符串输入"""
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                return parsed
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，尝试作为单个参数处理
                print(f"JSON解析失败: {e}, 原始数据: {data}")
                pass
        return data


# 工具实现
@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_account_info(
    format: Literal["json", "markdown"] = "json",
    detail: Literal["concise", "detailed"] = "concise"
) -> str:
    """
    获取当前配置的公众号基本信息。

    此工具用于验证微信公众号 API 配置是否正确，并获取公众号的基本信息和统计数据。
    在开始使用其他功能前，建议先调用此工具确认配置正确。

    Args:
        format: 响应格式 - "json" 返回结构化数据，"markdown" 返回可读文本
        detail: 详细程度 - "concise" 返回基本信息，"detailed" 返回完整统计

    Returns:
        格式化的公众号信息，包含名称、类型、认证状态等

    Examples:
        get_account_info(format="json", detail="concise")
        get_account_info(format="markdown", detail="detailed")

    Error Handling:
        - 配置错误：检查 WECHAT_APPID 和 WECHAT_SECRET 环境变量
        - 认证失败：确认公众号已认证并开启开发者模式
        - 网络错误：检查网络连接和防火墙设置
        - 权限不足：确认公众号类型支持 API 功能
    """
    try:
        # 清理过期缓存
        cache_manager.clear_expired()
        
        # 获取公众号信息
        account_info = await wechat_client.get_account_info()
        
        # 格式化响应
        response = format_account_info(account_info, format, detail)
        
        # 截断过长响应
        return truncate_response(response)
        
    except Exception as e:
        raise ToolError(f"""获取公众号信息失败：{str(e)}

请检查：
1. 环境变量 WECHAT_APPID 和 WECHAT_SECRET 是否正确设置
2. 公众号是否已认证并开启开发者模式
3. 服务器 IP 是否已添加到微信公众平台白名单
4. 网络连接是否正常

配置示例：
export WECHAT_APPID=your_app_id
export WECHAT_SECRET=your_app_secret""")


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_articles(input: ListArticlesInput) -> str:
    """
    获取公众号的图文消息列表。

    此工具用于获取当前公众号发布的图文消息列表，支持分页浏览。
    只能获取通过微信公众平台发布的永久素材。

    Args:
        offset: 偏移量，从第几条开始获取（从0开始）
        count: 获取数量，最多20条
        format: 响应格式 - "json" 或 "markdown"
        detail: 详细程度 - "concise" 返回基本信息，"detailed" 返回完整信息

    Returns:
        格式化的文章列表，包含标题、作者、链接、更新时间等

    Examples:
        list_articles(offset=0, count=10, format="json", detail="concise")
        list_articles(offset=10, count=5, format="markdown", detail="detailed")

    Error Handling:
        - 超出范围：调整 offset 和 count 参数
        - API 限制：注意每日调用次数限制（10次/天）
        - 无内容：确认公众号已发布图文消息
        - 权限不足：确认公众号支持素材管理功能
    """
    try:
        # 获取文章列表
        articles = await wechat_client.list_articles(input.offset, input.count)
        
        if not articles:
            return "未找到文章。请确认：\n1. 公众号已发布图文消息\n2. offset 参数设置正确\n3. 公众号权限正常"
        
        # 格式化响应
        response = format_article_list(articles, input.format, input.detail)
        
        # 截断过长响应
        return truncate_response(response)
        
    except Exception as e:
        raise ToolError(f"""获取文章列表失败：{str(e)}

建议：
1. 检查 offset 和 count 参数是否合理
2. 确认公众号已发布图文消息
3. 注意 API 调用限制（素材管理：10次/天）
4. 如果是新发布的文章，请稍等片刻后重试

示例：list_articles(offset=0, count=10)""")


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_article_content(input: GetArticleContentInput) -> str:
    """
    根据 media_id 获取文章的详细内容。

    此工具用于获取具体文章的完整内容，包括正文、作者、发布时间等详细信息。
    media_id 可以从 list_articles 工具的返回结果中获取。

    Args:
        media_id: 文章的媒体ID，从 list_articles 获取
        format: 响应格式 - "json" 或 "markdown"（推荐）
        detail: 详细程度 - "concise" 或 "detailed"
        include_html: 是否包含原始HTML内容（仅 json 格式有效）

    Returns:
        格式化的文章内容，包含标题、作者、正文、统计信息等

    Examples:
        get_article_content(media_id="BM_Vc7h...", format="markdown", detail="detailed")
        get_article_content(media_id="BM_Vc7h...", format="json", include_html=True)

    Error Handling:
        - 无效 media_id：使用 list_articles 获取正确的 media_id
        - 内容过长：自动截断，建议使用 concise 模式
        - 权限不足：确认对该文章有访问权限
        - API 限制：注意每日调用次数限制
    """
    try:
        # 获取文章内容
        article = await wechat_client.get_article_content(input.media_id)
        
        # 格式化响应
        response = format_article_content(
            article, 
            input.format, 
            input.detail, 
            input.include_html
        )
        
        # 截断过长响应
        return truncate_response(response)
        
    except Exception as e:
        raise ToolError(f"""获取文章内容失败：{str(e)}

请检查：
1. media_id 是否正确（从 list_articles 获取）
2. 文章是否存在且有访问权限
3. API 调用是否超出限制

获取 media_id 的方法：
1. 先调用 list_articles 获取文章列表
2. 从返回结果中找到目标文章的 media_id
3. 使用该 media_id 调用此工具

示例：get_article_content(media_id="正确的media_id")""")


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def search_public_articles(input: SearchPublicArticlesInput) -> str:
    """
    通过搜狗微信搜索查找公开的微信文章。

    此工具用于搜索其他公众号发布的公开文章，不需要微信 API 权限。
    搜索结果来自搜狗微信搜索，可能受到反爬限制。

    Args:
        query: 搜索关键词，支持多个词语组合
        account_name: 指定公众号名称（可选），用于精确搜索
        limit: 返回结果数量，最多20条
        format: 响应格式 - "json" 或 "markdown"
        detail: 详细程度 - "concise" 或 "detailed"

    Returns:
        格式化的搜索结果，包含标题、公众号、发布时间、链接等

    Examples:
        search_public_articles(query="人工智能", limit=10)
        search_public_articles(query="ChatGPT", account_name="机器之心", limit=5)

    Error Handling:
        - 搜索限制：等待5-10分钟后重试，减少搜索频率
        - 验证码：等待10-30分钟后重试
        - 无结果：尝试更通用的关键词或检查拼写
        - 网络错误：检查网络连接
    """
    try:
        # 搜索文章
        results = await search_client.search_articles(
            input.query, 
            input.account_name, 
            input.limit
        )
        
        if not results:
            return f"""未找到相关文章。

建议：
1. 尝试更通用的关键词："{input.query}" → "AI" 或 "技术"
2. 检查关键词拼写是否正确
3. 去掉 account_name 限制扩大搜索范围
4. 稍后重试（可能是临时限制）

搜索提示：
- 使用简短、常见的关键词
- 避免过于具体的长句
- 可以尝试同义词或相关词汇"""
        
        # 格式化响应
        response = format_search_results(results, input.format, input.detail)
        
        # 截断过长响应
        return truncate_response(response)
        
    except Exception as e:
        raise ToolError(f"""搜索公开文章失败：{str(e)}

这通常是由于：
1. 搜索频率过快 - 等待 5-10 分钟后重试
2. 触发反爬机制 - 等待 10-30 分钟后重试
3. 网络连接问题 - 检查网络设置

建议：
1. 减少搜索频率，每次搜索间隔至少 30 秒
2. 使用更具体的关键词减少搜索次数
3. 优先使用官方 API 功能（get_account_info, list_articles）
4. 如果急需搜索，可以稍后重试

示例：search_public_articles(query="简短关键词", limit=5)""")


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": False,  # 可能触发反爬
        "openWorldHint": False
    }
)
async def get_public_article_content(input: GetPublicArticleContentInput) -> str:
    """
    获取公开微信文章的详细内容。

    此工具用于获取搜索到的公开文章的完整内容。由于微信的反爬机制，
    此功能可能不稳定，建议谨慎使用。

    Args:
        article_url: 文章URL地址，通常来自 search_public_articles 的结果
        format: 响应格式 - "json" 或 "markdown"（推荐）
        detail: 详细程度 - "concise" 或 "detailed"
        extract_images: 是否提取图片链接

    Returns:
        格式化的文章内容，包含标题、作者、正文、发布时间等

    Examples:
        get_public_article_content(article_url="https://mp.weixin.qq.com/s/xxx")
        get_public_article_content(article_url="https://mp.weixin.qq.com/s/xxx", extract_images=True)

    Error Handling:
        - 链接失效：使用 search_public_articles 重新搜索
        - 访问限制：等待10-30分钟后重试
        - 内容加载失败：可能是反爬限制，建议稍后重试
        - 无效URL：确认URL格式正确
    """
    try:
        # 获取文章内容
        article = await search_client.get_article_content(input.article_url)
        
        # 如果不需要图片，移除图片信息
        if not input.extract_images and "images" in article:
            del article["images"]
        
        # 格式化响应
        response = format_article_content(article, input.format, input.detail)
        
        # 截断过长响应
        return truncate_response(response)
        
    except Exception as e:
        raise ToolError(f"""获取公开文章内容失败：{str(e)}

这是高风险操作，可能遇到以下问题：
1. 微信反爬机制 - 等待 10-30 分钟后重试
2. 文章链接失效 - 使用 search_public_articles 重新搜索
3. 访问频率限制 - 减少使用频率

建议：
1. 优先使用官方 API 功能获取自有内容
2. 如果必须获取公开内容，请：
   - 确保 URL 格式正确：https://mp.weixin.qq.com/s/xxx
   - 等待足够时间间隔（至少 2-5 分钟）
   - 准备应对访问失败的情况

替代方案：
- 使用 search_public_articles 获取文章摘要
- 手动访问文章链接获取内容
- 联系文章作者获取授权""")


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def search_accounts(input: SearchAccountsInput) -> str:
    """
    搜索微信公众号。

    此工具用于搜索公众号信息，可以根据名称或关键词查找相关的公众号。
    搜索结果来自搜狗微信搜索。

    Args:
        query: 公众号名称或关键词
        limit: 返回结果数量，最多20条
        format: 响应格式 - "json" 或 "markdown"

    Returns:
        格式化的公众号列表，包含名称、描述、认证状态等

    Examples:
        search_accounts(query="机器之心", limit=5)
        search_accounts(query="AI", limit=10)

    Error Handling:
        - 搜索限制：等待5-10分钟后重试
        - 无结果：尝试更通用的关键词
        - 网络错误：检查网络连接
    """
    try:
        # 搜索公众号
        results = await search_client.search_accounts(input.query, input.limit)
        
        if not results:
            return f"""未找到相关公众号。

建议：
1. 尝试更通用的关键词："{input.query}" → 简化为核心词汇
2. 检查关键词拼写是否正确
3. 尝试使用公众号的部分名称
4. 稍后重试（可能是临时限制）

搜索提示：
- 使用公众号的核心关键词
- 避免使用过长的搜索词
- 可以尝试行业相关词汇"""
        
        # 格式化响应
        if input.format == "json":
            import json
            return json.dumps(results, ensure_ascii=False, indent=2)
        else:  # markdown
            lines = ["# 公众号搜索结果\n"]
            for i, result in enumerate(results, 1):
                name = result.get("name", "未知公众号")
                description = result.get("description", "")
                verified = result.get("verified", False)
                
                lines.append(f"## {i}. {name}")
                if verified:
                    lines.append("**认证状态**: ✅ 已认证")
                else:
                    lines.append("**认证状态**: ❌ 未认证")
                    
                if description:
                    lines.append(f"**描述**: {description}")
                    
                lines.append("")  # 空行分隔
                
            return "\n".join(lines)
        
    except Exception as e:
        raise ToolError(f"""搜索公众号失败：{str(e)}

建议：
1. 等待 5-10 分钟后重试
2. 使用更简单的关键词
3. 检查网络连接
4. 减少搜索频率

示例：search_accounts(query="简短关键词", limit=5)""")


def main():
    """主函数"""
    # 默认使用 STDIO 传输协议
    mcp.run()


if __name__ == "__main__":
    main()