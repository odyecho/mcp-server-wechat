# WeChat Official Account MCP Server

一个用于访问微信公众号文章和内容的 MCP (Model Context Protocol) 服务器，支持通过配置文件方式集成到 Claude Desktop 等 MCP 客户端中。

## 快速开始

### 环境准备

本项目使用 [uv](https://docs.astral.sh/uv/) 进行依赖管理，确保环境一致性和快速安装。

1. **安装 uv**（如果还没有安装）
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **克隆项目并设置环境**
   ```bash
   git clone <repository-url>
   cd mcp-server-wechat

   # 一键创建虚拟环境并安装所有依赖
   uv sync
   ```

3. **配置环境变量**（可选）
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的微信公众号 AppID 和 AppSecret
   ```

### 配置方式

#### 方式一：自动安装到 Claude Desktop（推荐）

```bash
./scripts/install_to_claude.sh
```

重启 Claude Desktop 后即可使用微信公众号相关功能。

#### 方式二：在 Claude Code 中配置

如果您使用 Claude Code（claude.ai/code），可以按以下步骤配置：

1. **在 Claude Code 设置中添加 MCP 服务器配置**：
   ```json
   {
     "name": "wechat-mcp",
     "command": "uvx",
     "args": [
       "--from",
       "/path/to/your/mcp-server-wechat",
       "mcp-server-wechat"
     ],
     "env": {
       "WECHAT_APPID": "your_app_id_here",
       "WECHAT_SECRET": "your_app_secret_here"
     }
   }
   ```

2. **备选配置方案**（使用 uv run）：
   ```json
   {
     "name": "wechat-mcp",
     "command": "uv",
     "args": [
       "run",
       "--directory",
       "/path/to/your/mcp-server-wechat",
       "python",
       "src/mcp_server_wechat/server.py"
     ],
     "env": {
       "WECHAT_APPID": "your_app_id_here",
       "WECHAT_SECRET": "your_app_secret_here"
     }
   }
   ```

**注意**：
- 将路径替换为您的实际项目路径
- 如果没有微信凭据，可以省略 `env` 部分（仍可使用搜索功能）

#### 方式三：手动配置

详细的手动配置步骤请参考 [安装配置指南](INSTALLATION_GUIDE.md)

### 开发和测试

```bash
# 开发调试（推荐，启动 MCP Inspector 可视化界面）
uv run fastmcp dev src/mcp_server_wechat/server.py
# 访问 http://127.0.0.1:6274 进行测试

# 直接运行服务器（STDIO 模式）
uv run python3 src/mcp_server_wechat/server.py

# 运行测试
uv run pytest
```

## 功能说明

### 双数据源设计

1. **微信公众号官方 API**：需要 WECHAT_APPID 和 WECHAT_SECRET，用于管理自己的公众号
2. **搜狗微信搜索**：无需凭据，用于搜索和获取公开文章内容

### 6 个核心工具

- `get_account_info` - 获取公众号基本信息
- `list_articles` - 列出公众号文章列表
- `get_article_content` - 获取文章详细内容
- `search_public_articles` - 搜索公开文章
- `get_public_article_content` - 获取公开文章内容
- `search_accounts` - 搜索公众号

### 使用示例

配置完成后，您可以在 Claude Code 中这样使用：

**搜索公开文章**（无需凭据）：
```
请帮我搜索关于"ChatGPT"的微信公众号文章，找到最新的5篇
```

**获取文章内容**：
```
请帮我获取这篇文章的详细内容：https://mp.weixin.qq.com/s/xxxxx
```

**搜索公众号**：
```
请帮我搜索"机器之心"相关的公众号
```

**管理自己的公众号**（需要凭据）：
```
请帮我获取我的公众号基本信息
请列出我公众号最近发布的10篇文章
```

### 微信公众号凭据获取

如果您有微信公众号的开发权限：

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "基本配置"
3. 复制 AppID 和 AppSecret
4. 填入配置文件或环境变量

**重要提示**：即使没有微信公众号凭据，您仍可以使用搜索功能获取公开文章！

## 常见问题解决

### 1. 命令找不到
```bash
# 确保 uv 在 PATH 中
echo $PATH
which uv
```

### 2. 权限问题
```bash
# 给脚本执行权限
chmod +x src/mcp_server_wechat/server.py
```

### 3. 依赖安装失败
```bash
# 重新安装依赖
uv sync --reinstall
```

### 4. 配置不生效
- 检查 JSON 配置格式是否正确
- 确认路径是否正确
- 重启 Claude Code

## 功能限制说明

### 搜索功能（无需凭据）
- ✅ 搜索任何公开发布的微信文章
- ✅ 获取文章完整内容
- ✅ 搜索公众号信息
- ⚠️ 受搜狗微信搜索反爬限制，建议适度使用

### 官方 API 功能（需要凭据）
- ✅ 获取自己公众号的完整信息
- ✅ 管理和查看自己发布的文章
- ✅ 获取文章统计数据
- ⚠️ 需要已认证的公众号
- ⚠️ 有 API 调用次数限制

一个为 AI Agent 提供微信公众号文章访问和管理能力的 MCP Server。

## 技术特性

- 🚀 基于 **FastMCP 2.0+** 框架
- 📝 完整的 **Pydantic v2** 输入验证
- 🔄 **异步 I/O** 操作（async/await）
- 📊 支持 **JSON** 和 **Markdown** 响应格式
- 🎯 支持 **concise** 和 **detailed** 详细级别
- 🛡️ 完整的**错误处理**和可操作的错误消息
- 💾 **智能缓存**系统
- 🔍 **搜狗微信搜索**集成
- 🌐 支持 **STDIO** 和 **HTTP** 传输协议

## 工具使用指南

### 获取公众号信息
```python
# 验证配置并获取基本信息
get_account_info(format="json", detail="concise")
```

### 浏览文章列表
```python
# 获取最新的 10 篇文章
list_articles(offset=0, count=10, format="markdown", detail="concise")
```

### 获取文章内容
```python
# 使用从 list_articles 获取的 media_id
get_article_content(
    media_id="BM_Vc7hGvWUiRSqbROjwQ-qGHisVjia6tVPwl2r1NjqzjJFbkCBsZtDvSMJY8bL",
    format="markdown",
    detail="detailed"
)
```

### 搜索公开文章
```python
# 搜索相关文章
search_public_articles(query="人工智能", limit=10, format="json")

# 在特定公众号中搜索
search_public_articles(
    query="ChatGPT",
    account_name="机器之心",
    limit=5,
    format="markdown"
)
```

### 获取公开文章内容
```python
# 获取搜索到的文章内容
get_public_article_content(
    article_url="https://mp.weixin.qq.com/s/xxx",
    format="markdown",
    detail="detailed",
    extract_images=True
)
```

### 搜索公众号
```python
# 搜索相关公众号
search_accounts(query="机器之心", limit=5, format="json")
```

## 环境变量配置

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `WECHAT_APPID` | 可选 | 微信公众号 AppID（官方 API 功能需要） |
| `WECHAT_SECRET` | 可选 | 微信公众号 AppSecret（官方 API 功能需要） |

## 项目结构

```
mcp-server-wechat/
├── src/mcp_server_wechat/
│   ├── server.py           # 主服务器文件
│   └── utils/              # 工具模块
│       ├── api_client.py   # 微信 API 客户端
│       ├── search_client.py # 搜索客户端
│       ├── formatters.py   # 响应格式化
│       ├── errors.py       # 错误处理
│       └── cache.py        # 缓存管理
├── tests/                  # 测试文件
├── scripts/                # 安装脚本
├── docs/                   # 文档目录
├── pyproject.toml         # 项目配置
└── README.md              # 项目文档
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 支持

如果遇到问题，请：
1. 查看本文档的错误处理部分
2. 检查环境配置是否正确
3. 使用 `fastmcp dev` 进行调试
4. 提交 Issue 描述具体问题
