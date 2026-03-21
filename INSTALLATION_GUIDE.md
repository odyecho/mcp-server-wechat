# 微信公众号 MCP Server 安装和配置指南

## 概述

本指南将帮助你在 macOS 系统上配置和使用微信公众号 MCP Server，支持通过配置文件的方式集成到 Claude Desktop 等 MCP 客户端中。

## 前置要求

- macOS 系统
- Python 3.10 或更高版本
- uv 包管理器
- 微信公众号开发者账号

## 安装步骤

### 1. 项目准备

确保项目已经正确安装依赖：

```bash
cd /path/to/your/mcp-server-wechat
uv sync
```

### 2. 环境变量配置

复制环境变量模板文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的微信公众号信息：

```bash
# 微信公众号基本信息
WECHAT_APP_ID=你的微信公众号AppID
WECHAT_APP_SECRET=你的微信公众号AppSecret

# 其他配置保持默认即可
CACHE_ENABLED=true
CACHE_TTL=3600
LOG_LEVEL=INFO
```

### 3. 获取微信公众号凭据

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" -> "基本配置"
3. 获取 AppID 和 AppSecret
4. 将这些信息填入 `.env` 文件

## 配置 Claude Desktop

### 方法一：使用提供的配置文件

1. 复制项目中的 `claude_desktop_config.json` 文件内容
2. 打开 Claude Desktop 配置文件：
   ```bash
   # macOS 位置
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```
3. 将配置添加到 `mcpServers` 部分

### 方法二：手动配置

在 Claude Desktop 配置文件中添加以下配置：

```json
{
  "mcpServers": {
    "wechat": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/mcp-server-wechat",
        "python3",
        "-m",
        "mcp_server_wechat.server"
      ],
      "env": {
        "WECHAT_APP_ID": "你的微信公众号AppID",
        "WECHAT_APP_SECRET": "你的微信公众号AppSecret",
        "CACHE_ENABLED": "true",
        "CACHE_TTL": "3600",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**重要提示**：请将配置中的路径 `/path/to/your/mcp-server-wechat` 替换为你的实际项目路径。

## 配置其他 MCP 客户端

### Cursor 配置

使用 fastmcp 工具安装到 Cursor：

```bash
cd /path/to/your/mcp-server-wechat
uv run fastmcp install cursor src/mcp_server_wechat/server.py --env WECHAT_APP_ID=你的AppID --env WECHAT_APP_SECRET=你的AppSecret
```

### 通用 MCP 客户端配置

对于支持 MCP 协议的其他客户端，使用以下命令启动服务器：

```bash
cd /path/to/your/mcp-server-wechat
uv run python3 -m mcp_server_wechat.server
```

## 验证安装

### 1. 测试服务器启动

```bash
cd /path/to/your/mcp-server-wechat
uv run fastmcp dev src/mcp_server_wechat/server.py
```

如果看到类似以下输出，说明服务器启动成功：

```
Starting MCP inspector...
⚙️ Proxy server listening on port 6277
🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀
```

### 2. 使用 MCP Inspector 测试

1. 打开浏览器访问 `http://127.0.0.1:6274`
2. 在 MCP Inspector 中测试各个工具
3. 尝试调用 `get_account_info` 工具验证配置

### 3. 在 Claude Desktop 中测试

1. 重启 Claude Desktop
2. 在对话中询问关于微信公众号的问题
3. 观察是否能正确调用 MCP 工具

## 可用工具

配置完成后，你可以使用以下工具：

1. **get_account_info** - 获取公众号基本信息
2. **list_articles** - 列出公众号文章
3. **get_article_content** - 获取文章详细内容
4. **search_public_articles** - 搜索公开文章
5. **get_public_article_content** - 获取公开文章内容

## 故障排除

### 常见问题

1. **权限错误**
   ```bash
   chmod +x /path/to/your/mcp-server-wechat/src/mcp_server_wechat/server.py
   ```

2. **依赖问题**
   ```bash
cd /path/to/your/mcp-server-wechat
   uv sync --reinstall
   ```

3. **环境变量未生效**
   - 检查 `.env` 文件是否在正确位置
   - 确认环境变量名称拼写正确
   - 重启 Claude Desktop

### 日志查看

查看服务器日志：

```bash
tail -f logs/mcp_server.log
```

### 调试模式

启用详细日志：

```bash
export LOG_LEVEL=DEBUG
uv run python3 -m mcp_server_wechat.server
```

## 安全注意事项

1. **保护敏感信息**
   - 不要将 `.env` 文件提交到版本控制
   - 定期更换 AppSecret
   - 使用最小权限原则

2. **网络安全**
   - 确保 HTTPS 连接
   - 监控 API 调用频率
   - 设置合理的超时时间

## 更新和维护

### 更新项目

```bash
cd /path/to/your/mcp-server-wechat
git pull
uv sync
```

### 清理缓存

```bash
rm -rf .cache/*
```

### 重置配置

```bash
cp .env.example .env
# 重新编辑 .env 文件
```

## 支持

如果遇到问题，请：

1. 查看项目 README.md
2. 检查日志文件
3. 使用 MCP Inspector 进行调试
4. 提交 Issue 到项目仓库

---

**配置完成后，你就可以在 Claude Desktop 或其他 MCP 客户端中使用微信公众号相关功能了！**