#!/bin/bash

# Claude Desktop MCP 配置安装脚本
# 自动将微信公众号 MCP Server 配置添加到 Claude Desktop

set -e

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Claude Desktop 配置文件路径
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# 检查 Claude Desktop 是否安装
check_claude_desktop() {
    log_info "检查 Claude Desktop 安装状态..."
    
    if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
        log_error "Claude Desktop 未安装或配置目录不存在"
        log_info "请先安装 Claude Desktop: https://claude.ai/download"
        exit 1
    fi
    
    log_success "Claude Desktop 配置目录存在"
}

# 检查环境变量
check_env() {
    log_info "检查环境变量配置..."
    
    if [ ! -f ".env" ]; then
        log_error ".env 文件不存在，请先运行 ./scripts/start_server.sh 进行初始化"
        exit 1
    fi
    
    # 加载环境变量
    export $(grep -v '^#' .env | xargs)
    
    # 检查必需的环境变量
    if [ -z "$WECHAT_APP_ID" ] || [ "$WECHAT_APP_ID" = "your_wechat_app_id_here" ]; then
        log_error "请在 .env 文件中设置正确的 WECHAT_APP_ID"
        exit 1
    fi
    
    if [ -z "$WECHAT_APP_SECRET" ] || [ "$WECHAT_APP_SECRET" = "your_wechat_app_secret_here" ]; then
        log_error "请在 .env 文件中设置正确的 WECHAT_APP_SECRET"
        exit 1
    fi
    
    log_success "环境变量检查完成"
}

# 备份现有配置
backup_config() {
    if [ -f "$CLAUDE_CONFIG_FILE" ]; then
        local backup_file="${CLAUDE_CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        log_info "备份现有配置到: $backup_file"
        cp "$CLAUDE_CONFIG_FILE" "$backup_file"
        log_success "配置备份完成"
    fi
}

# 生成 MCP 配置
generate_mcp_config() {
    log_info "生成 MCP 配置..."
    
    cat > /tmp/wechat_mcp_config.json << EOF
{
  "wechat": {
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "$PROJECT_ROOT",
      "python3",
      "-m",
      "mcp_server_wechat.server"
    ],
    "env": {
      "WECHAT_APP_ID": "$WECHAT_APP_ID",
      "WECHAT_APP_SECRET": "$WECHAT_APP_SECRET",
      "CACHE_ENABLED": "${CACHE_ENABLED:-true}",
      "CACHE_TTL": "${CACHE_TTL:-3600}",
      "LOG_LEVEL": "${LOG_LEVEL:-INFO}"
    }
  }
}
EOF
    
    log_success "MCP 配置生成完成"
}

# 更新 Claude Desktop 配置
update_claude_config() {
    log_info "更新 Claude Desktop 配置..."
    
    # 创建配置目录（如果不存在）
    mkdir -p "$CLAUDE_CONFIG_DIR"
    
    if [ ! -f "$CLAUDE_CONFIG_FILE" ]; then
        # 创建新的配置文件
        log_info "创建新的 Claude Desktop 配置文件"
        cat > "$CLAUDE_CONFIG_FILE" << EOF
{
  "mcpServers": $(cat /tmp/wechat_mcp_config.json)
}
EOF
    else
        # 更新现有配置文件
        log_info "更新现有 Claude Desktop 配置文件"
        
        # 使用 Python 来合并 JSON 配置
        python3 << EOF
import json
import sys

# 读取现有配置
try:
    with open('$CLAUDE_CONFIG_FILE', 'r') as f:
        existing_config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    existing_config = {}

# 读取新的 MCP 配置
with open('/tmp/wechat_mcp_config.json', 'r') as f:
    new_mcp_config = json.load(f)

# 确保 mcpServers 键存在
if 'mcpServers' not in existing_config:
    existing_config['mcpServers'] = {}

# 添加或更新 wechat 配置
existing_config['mcpServers'].update(new_mcp_config)

# 写回配置文件
with open('$CLAUDE_CONFIG_FILE', 'w') as f:
    json.dump(existing_config, f, indent=2)

print("配置更新成功")
EOF
    fi
    
    # 清理临时文件
    rm -f /tmp/wechat_mcp_config.json
    
    log_success "Claude Desktop 配置更新完成"
}

# 验证配置
verify_config() {
    log_info "验证配置文件..."
    
    if python3 -c "import json; json.load(open('$CLAUDE_CONFIG_FILE'))" 2>/dev/null; then
        log_success "配置文件格式正确"
    else
        log_error "配置文件格式错误，请检查 JSON 语法"
        exit 1
    fi
}

# 显示完成信息
show_completion_info() {
    echo ""
    log_success "安装完成！"
    echo ""
    echo "接下来的步骤："
    echo "1. 重启 Claude Desktop 应用"
    echo "2. 在 Claude Desktop 中测试微信公众号功能"
    echo ""
    echo "可用的工具："
    echo "  - get_account_info: 获取公众号基本信息"
    echo "  - list_articles: 列出公众号文章"
    echo "  - get_article_content: 获取文章详细内容"
    echo "  - search_public_articles: 搜索公开文章"
    echo "  - get_public_article_content: 获取公开文章内容"
    echo "  - search_accounts: 搜索公众号"
    echo ""
    echo "配置文件位置: $CLAUDE_CONFIG_FILE"
    echo ""
    log_info "如需卸载，请运行: ./scripts/uninstall_from_claude.sh"
}

# 显示帮助信息
show_help() {
    echo "Claude Desktop MCP 配置安装脚本"
    echo ""
    echo "此脚本将自动配置 Claude Desktop 以使用微信公众号 MCP Server"
    echo ""
    echo "使用方法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help    显示此帮助信息"
    echo "  -f, --force   强制安装（跳过确认）"
    echo ""
    echo "注意事项:"
    echo "  - 请确保已正确配置 .env 文件"
    echo "  - 安装前会自动备份现有配置"
    echo "  - 安装后需要重启 Claude Desktop"
}

# 主函数
main() {
    local force_install=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                force_install=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "开始安装微信公众号 MCP Server 到 Claude Desktop"
    echo ""
    
    # 执行安装步骤
    check_claude_desktop
    check_env
    
    # 确认安装
    if [ "$force_install" = false ]; then
        echo ""
        log_warning "此操作将修改 Claude Desktop 配置文件"
        read -p "是否继续？(y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "安装已取消"
            exit 0
        fi
    fi
    
    backup_config
    generate_mcp_config
    update_claude_config
    verify_config
    show_completion_info
}

# 运行主函数
main "$@"