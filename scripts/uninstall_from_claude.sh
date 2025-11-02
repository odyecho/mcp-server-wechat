#!/bin/bash

# Claude Desktop MCP 配置卸载脚本
# 从 Claude Desktop 配置中移除微信公众号 MCP Server

set -e

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

# 检查配置文件是否存在
check_config_exists() {
    log_info "检查 Claude Desktop 配置文件..."
    
    if [ ! -f "$CLAUDE_CONFIG_FILE" ]; then
        log_warning "Claude Desktop 配置文件不存在，无需卸载"
        exit 0
    fi
    
    log_success "找到 Claude Desktop 配置文件"
}

# 备份现有配置
backup_config() {
    local backup_file="${CLAUDE_CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    log_info "备份现有配置到: $backup_file"
    cp "$CLAUDE_CONFIG_FILE" "$backup_file"
    log_success "配置备份完成"
}

# 从配置中移除 wechat MCP server
remove_wechat_config() {
    log_info "从 Claude Desktop 配置中移除微信公众号 MCP Server..."
    
    # 使用 Python 来处理 JSON 配置
    python3 << EOF
import json
import sys

# 读取现有配置
try:
    with open('$CLAUDE_CONFIG_FILE', 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"读取配置文件失败: {e}")
    sys.exit(1)

# 检查是否存在 mcpServers 和 wechat 配置
if 'mcpServers' not in config:
    print("配置中没有找到 mcpServers 部分")
    sys.exit(0)

if 'wechat' not in config['mcpServers']:
    print("配置中没有找到 wechat MCP server")
    sys.exit(0)

# 移除 wechat 配置
del config['mcpServers']['wechat']
print("已移除 wechat MCP server 配置")

# 如果 mcpServers 为空，也可以选择移除整个部分
if not config['mcpServers']:
    del config['mcpServers']
    print("mcpServers 部分为空，已移除")

# 写回配置文件
with open('$CLAUDE_CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)

print("配置更新成功")
EOF
    
    if [ $? -eq 0 ]; then
        log_success "微信公众号 MCP Server 配置已移除"
    else
        log_error "移除配置失败"
        exit 1
    fi
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
    log_success "卸载完成！"
    echo ""
    echo "接下来的步骤："
    echo "1. 重启 Claude Desktop 应用"
    echo "2. 微信公众号 MCP 功能将不再可用"
    echo ""
    echo "如需重新安装，请运行: ./scripts/install_to_claude.sh"
    echo ""
    log_info "配置备份文件保存在 Claude 配置目录中，以 .backup 结尾"
}

# 显示帮助信息
show_help() {
    echo "Claude Desktop MCP 配置卸载脚本"
    echo ""
    echo "此脚本将从 Claude Desktop 配置中移除微信公众号 MCP Server"
    echo ""
    echo "使用方法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help    显示此帮助信息"
    echo "  -f, --force   强制卸载（跳过确认）"
    echo ""
    echo "注意事项:"
    echo "  - 卸载前会自动备份现有配置"
    echo "  - 卸载后需要重启 Claude Desktop"
    echo "  - 不会删除项目文件，只是移除 Claude Desktop 配置"
}

# 主函数
main() {
    local force_uninstall=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                force_uninstall=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    log_info "开始从 Claude Desktop 卸载微信公众号 MCP Server"
    echo ""
    
    # 执行卸载步骤
    check_config_exists
    
    # 确认卸载
    if [ "$force_uninstall" = false ]; then
        echo ""
        log_warning "此操作将从 Claude Desktop 配置中移除微信公众号 MCP Server"
        read -p "是否继续？(y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "卸载已取消"
            exit 0
        fi
    fi
    
    backup_config
    remove_wechat_config
    verify_config
    show_completion_info
}

# 运行主函数
main "$@"