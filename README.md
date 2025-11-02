# WeChat Official Account MCP Server

一个用于访问微信公众号文章和内容的 MCP (Model Context Protocol) 服务器，支持通过配置文件方式集成到 Claude Desktop 等 MCP 客户端中。

## 快速开始

### 开发环境设置

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

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填入你的微信公众号 AppID 和 AppSecret
   ```

### 方法一：自动安装到 Claude Desktop（推荐）

1. **自动安装到 Claude Desktop**
   ```bash
   ./scripts/install_to_claude.sh
   ```

2. **重启 Claude Desktop**，即可使用微信公众号相关功能

### 方法二：手动配置

详细的手动配置步骤请参考 [安装配置指南](INSTALLATION_GUIDE.md)

### 开发和测试

```bash
# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 运行测试
uv run pytest

# 启动开发服务器
uv run python -m mcp_server_wechat.server
```

## 配置文件使用

一个为 AI Agent 提供微信公众号文章访问和管理能力的 MCP Server。

## 项目状态

✅ **已完成**：
- 完整的 FastMCP 2.0+ 框架实现
- 6 个核心工具的完整实现
- 微信公众号 API 客户端
- 搜狗微信搜索客户端
- 缓存管理系统
- 错误处理和格式化工具
- 通过 `fastmcp dev` 测试验证

🔧 **当前状态**：
- 服务器可以正常启动和运行
- 所有工具都有完整的文档和类型提示
- 支持 JSON 和 Markdown 两种响应格式
- 支持 concise 和 detailed 两种详细级别
- 实现了可操作的错误处理

⚠️ **注意事项**：
- 需要配置微信公众号 API 凭据才能使用官方 API 功能
- 搜索功能可以在没有凭据的情况下使用（基于搜狗微信搜索）
- 建议使用 `fastmcp dev` 进行开发和调试

## 功能特性

### 核心工具

1. **get_account_info** - 获取公众号基本信息
2. **list_articles** - 列出公众号文章列表
3. **get_article_content** - 获取文章详细内容
4. **search_public_articles** - 搜索公开文章
5. **get_public_article_content** - 获取公开文章内容
6. **search_accounts** - 搜索公众号

### 技术特性

- 🚀 基于 **FastMCP 2.0+** 框架
- 📝 完整的 **Pydantic v2** 输入验证
- 🔄 **异步 I/O** 操作（async/await）
- 📊 支持 **JSON** 和 **Markdown** 响应格式
- 🎯 支持 **concise** 和 **detailed** 详细级别
- 🛡️ 完整的**错误处理**和可操作的错误消息
- 💾 **智能缓存**系统
- 🔍 **搜狗微信搜索**集成
- 🌐 支持 **STDIO** 和 **HTTP** 传输协议

### 官方 API 功能（需要公众号权限）
- 🏢 **获取公众号信息** - 验证配置并获取基本信息
- 📝 **文章列表管理** - 获取已发布的图文消息列表
- 📖 **文章内容获取** - 获取完整的文章内容和统计信息

### 公开搜索功能（无需权限）
- 🔍 **文章搜索** - 通过搜狗微信搜索查找公开文章
- 📄 **内容获取** - 获取搜索到的文章详细内容
- 🏪 **公众号搜索** - 搜索和发现相关公众号

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
cd mcp-server-wechat
uv sync

# 或使用 pip
pip install -e .
```

### 2. 环境配置

创建 `.env` 文件或设置环境变量：

```bash
# 微信公众号配置（可选，仅官方 API 功能需要）
export WECHAT_APPID=your_app_id
export WECHAT_SECRET=your_app_secret
```

**获取微信公众号配置：**
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "基本配置"
3. 获取 AppID 和 AppSecret
4. 将服务器 IP 添加到白名单

### 3. 运行服务器

#### 开发调试（推荐）
```bash
# 使用 MCP Inspector 进行可视化调试
uv run fastmcp dev src/mcp_server_wechat/server.py

# 访问 MCP Inspector 界面（通常在 http://127.0.0.1:6274）
# 可以在界面中测试所有工具功能
```
```

#### 直接运行
```bash
# STDIO 模式（默认）
uv run python3 src/mcp_server_wechat/server.py

# HTTP 模式（可选）
# 修改 server.py 中的 main() 函数启用 HTTP 模式
```

### 4. 安装到客户端

```bash
# 安装到 Claude Desktop
uv run fastmcp install claude-desktop src/mcp_server_wechat/server.py --env WECHAT_APPID=xxx --env WECHAT_SECRET=xxx

# 安装到其他客户端
uv run fastmcp install cursor src/mcp_server_wechat/server.py
```

## 工具使用指南

### 1. 获取公众号信息
```python
# 验证配置并获取基本信息
get_account_info(format="json", detail="concise")
```

### 2. 浏览文章列表
```python
# 获取最新的 10 篇文章
list_articles(offset=0, count=10, format="markdown", detail="concise")

# 获取更多文章（分页）
list_articles(offset=10, count=10, format="json", detail="detailed")
```

### 3. 获取文章内容
```python
# 使用从 list_articles 获取的 media_id
get_article_content(
    media_id="BM_Vc7hGvWUiRSqbROjwQ-qGHisVjia6tVPwl2r1NjqzjJFbkCBsZtDvSMJY8bL",
    format="markdown",
    detail="detailed"
)
```

### 4. 搜索公开文章
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

### 5. 获取公开文章内容
```python
# 获取搜索到的文章内容
get_public_article_content(
    article_url="https://mp.weixin.qq.com/s/xxx",
    format="markdown",
    detail="detailed",
    extract_images=True
)
```

### 6. 搜索公众号
```python
# 搜索相关公众号
search_accounts(query="机器之心", limit=5, format="json")
```

## 配置说明

### 传输协议

#### STDIO（默认，推荐）
- 适用于本地开发和 Claude Desktop 集成
- 更安全，无需网络配置
- 客户端管理服务器生命周期

#### HTTP（可选）
- 适用于远程访问和多客户端场景
- 需要修改 `server.py` 中的 `main()` 函数：

```python
def main():
    # HTTP 模式
    mcp.run(transport="http", host="127.0.0.1", port=8000)
```

### 环境变量

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `WECHAT_APPID` | 可选 | 微信公众号 AppID（官方 API 功能需要） |
| `WECHAT_SECRET` | 可选 | 微信公众号 AppSecret（官方 API 功能需要） |

## 功能限制

### 官方 API 限制
- **认证要求**：需要已认证的公众号
- **调用限制**：素材管理 API 每日限制 10 次
- **权限范围**：只能访问自己的公众号内容
- **IP 白名单**：需要将服务器 IP 添加到微信白名单

### 搜索功能限制
- **反爬机制**：搜狗微信搜索有反爬限制
- **频率限制**：建议每次搜索间隔 30 秒以上
- **稳定性**：可能遇到验证码或临时封禁
- **内容限制**：只能获取公开发布的文章

## 错误处理

### 常见错误及解决方案

#### 1. 配置错误
```
错误：获取公众号信息失败：Invalid AppID or AppSecret
解决：检查 WECHAT_APPID 和 WECHAT_SECRET 是否正确
```

#### 2. 权限不足
```
错误：API 功能未开启
解决：确认公众号已认证并开启开发者模式
```

#### 3. IP 限制
```
错误：IP not in whitelist
解决：在微信公众平台添加服务器 IP 到白名单
```

#### 4. 搜索限制
```
错误：搜索频率过快
解决：等待 5-10 分钟后重试，减少搜索频率
```

#### 5. 反爬限制
```
错误：触发反爬机制
解决：等待 10-30 分钟后重试，使用更保守的策略
```

## 最佳实践

### 1. 使用策略
- **优先使用官方 API**：稳定可靠，推荐用于生产环境
- **谨慎使用搜索功能**：作为补充手段，注意频率控制
- **合理缓存**：避免重复请求，提高响应速度

### 2. 错误处理
- **检查配置**：使用前先调用 `get_account_info` 验证配置
- **处理限制**：准备应对 API 限制和反爬机制
- **优雅降级**：搜索失败时提供替代方案

### 3. 性能优化
- **分页获取**：大量数据使用分页避免超时
- **格式选择**：根据需要选择 JSON 或 Markdown 格式
- **详细程度**：使用 concise 模式减少响应大小

## 开发指南

### 项目结构
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
├── pyproject.toml         # 项目配置
└── README.md              # 项目文档
```

### 调试技巧
1. **使用 MCP Inspector**：`fastmcp dev` 提供可视化调试界面
2. **查看日志**：注意错误信息中的具体建议
3. **测试配置**：先测试 `get_account_info` 确认配置正确
4. **分步调试**：从简单功能开始，逐步测试复杂功能

### 扩展开发
- **添加新工具**：在 `server.py` 中使用 `@mcp.tool` 装饰器
- **自定义格式化**：修改 `formatters.py` 中的格式化函数
- **增强错误处理**：在 `errors.py` 中添加新的错误类型
- **优化缓存策略**：调整 `cache.py` 中的缓存时间

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