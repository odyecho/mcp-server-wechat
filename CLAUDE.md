# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

微信公众号 MCP Server - 基于 FastMCP 2.0+ 框架，为 AI Agent 提供微信公众号文章访问能力。

## 常用命令

```bash
# 安装依赖
uv sync

# 开发调试（推荐，启动 MCP Inspector 可视化界面）
uv run fastmcp dev src/mcp_server_wechat/server.py
# 访问 http://127.0.0.1:6274 进行测试

# 直接运行服务器（STDIO 模式）
uv run python3 src/mcp_server_wechat/server.py

# 运行测试
uv run pytest

# 语法检查
python3 -m py_compile src/mcp_server_wechat/server.py

# 安装到 Claude Desktop
uv run fastmcp install claude-desktop src/mcp_server_wechat/server.py --env WECHAT_APPID=xxx --env WECHAT_SECRET=xxx

# 使用安装脚本
./scripts/install_to_claude.sh
./scripts/uninstall_from_claude.sh
```

## 架构

```
src/mcp_server_wechat/
├── server.py              # MCP Server 主文件，使用 @mcp.tool 装饰器注册工具
└── utils/
    ├── api_client.py      # WeChatAPIClient - 微信公众号官方 API 客户端
    ├── search_client.py   # SogouWeChatSearchClient - 搜狗微信搜索客户端
    ├── cache.py           # CacheManager - 内存+文件双层缓存
    ├── formatters.py      # 响应格式化（JSON/Markdown）
    └── errors.py          # 错误处理和可操作错误消息
```

### 双数据源设计

1. **微信公众号官方 API**：需要 WECHAT_APPID 和 WECHAT_SECRET，用于 `get_account_info`、`list_articles`、`get_article_content`
2. **搜狗微信搜索**：无需凭据，用于 `search_public_articles`、`get_public_article_content`、`search_accounts`

### 6 个核心工具

- `get_account_info` - 获取公众号基本信息
- `list_articles` - 列出公众号文章列表
- `get_article_content` - 获取文章详细内容
- `search_public_articles` - 搜索公开文章
- `get_public_article_content` - 获取公开文章内容
- `search_accounts` - 搜索公众号

## 开发规范

- 使用 Pydantic v2 进行输入验证
- 所有 I/O 操作使用 async/await
- 响应支持 `format`（json/markdown）和 `detail`（concise/detailed）参数
- 字符限制 25,000 tokens，超出自动截断
- 错误消息需包含具体解决建议

## 环境变量

```bash
# 微信公众号配置（官方 API 功能需要）
WECHAT_APPID=your_app_id
WECHAT_SECRET=your_app_secret

# 可选配置见 .env.example
```
