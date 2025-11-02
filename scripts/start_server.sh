#!/bin/bash

# 微信公众号 MCP Server 启动脚本
# 使用方法: ./scripts/start_server.sh [mode]
# mode: dev (开发模式) 或 prod (生产模式，默认)

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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v uv &> /dev/null; then
        log_error "uv 未安装，请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 未安装"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 检查环境变量
check_env() {
    log_info "检查环境变量..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，从模板创建..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_warning "请编辑 .env 文件并填入正确的微信公众号配置"
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
    
    # 加载环境变量
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
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

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p .cache
    
    log_success "目录创建完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装/更新依赖..."
    
    uv sync
    
    log_success "依赖安装完成"
}

# 启动开发模式
start_dev() {
    log_info "启动开发模式 (MCP Inspector)..."
    log_info "MCP Inspector 将在浏览器中打开，用于调试和测试"
    
    uv run fastmcp dev src/mcp_server_wechat/server.py
}

# 启动生产模式
start_prod() {
    log_info "启动生产模式..."
    log_info "服务器将以 STDIO 模式运行，等待 MCP 客户端连接"
    
    uv run python3 -m mcp_server_wechat.server
}

# 显示帮助信息
show_help() {
    echo "微信公众号 MCP Server 启动脚本"
    echo ""
    echo "使用方法:"
    echo "  $0 [mode]"
    echo ""
    echo "模式:"
    echo "  dev   - 开发模式，启动 MCP Inspector 进行调试"
    echo "  prod  - 生产模式，启动 STDIO MCP 服务器 (默认)"
    echo "  help  - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev    # 启动开发模式"
    echo "  $0 prod   # 启动生产模式"
    echo "  $0        # 启动生产模式 (默认)"
}

# 主函数
main() {
    local mode="${1:-prod}"
    
    case "$mode" in
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        "dev")
            log_info "启动微信公众号 MCP Server (开发模式)"
            ;;
        "prod")
            log_info "启动微信公众号 MCP Server (生产模式)"
            ;;
        *)
            log_error "未知模式: $mode"
            show_help
            exit 1
            ;;
    esac
    
    # 执行检查和准备步骤
    check_dependencies
    check_env
    create_directories
    install_dependencies
    
    echo ""
    log_success "准备工作完成，启动服务器..."
    echo ""
    
    # 根据模式启动服务器
    case "$mode" in
        "dev")
            start_dev
            ;;
        "prod")
            start_prod
            ;;
    esac
}

# 捕获中断信号
trap 'log_info "收到中断信号，正在关闭服务器..."; exit 0' INT TERM

# 运行主函数
main "$@"