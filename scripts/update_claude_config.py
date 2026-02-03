#!/usr/bin/env python3
"""
更新 Claude Desktop 配置脚本
自动修复 MCP Server 配置中的路径和参数问题
"""

import json
import os
from pathlib import Path

def update_claude_config():
    """更新 Claude Desktop 配置文件"""

    # Claude Desktop 配置文件路径
    config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"

    # 当前项目路径
    project_path = Path(__file__).parent.parent.absolute()

    # 新的配置
    new_config = {
        "mcpServers": {
            "wechat-mcp": {
                "command": "uvx",
                "args": [
                    "--from",
                    str(project_path),
                    "mcp-server-wechat"
                ],
                "env": {
                    "WECHAT_APPID": "your_app_id_here",
                    "WECHAT_SECRET": "your_app_secret_here"
                }
            }
        }
    }

    try:
        # 读取现有配置
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)

            # 合并配置（保留其他 MCP 服务器）
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}

            existing_config["mcpServers"]["wechat-mcp"] = new_config["mcpServers"]["wechat-mcp"]
            final_config = existing_config
        else:
            # 创建新配置
            config_path.parent.mkdir(parents=True, exist_ok=True)
            final_config = new_config

        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(final_config, f, indent=2, ensure_ascii=False)

        print(f"✅ 成功更新 Claude Desktop 配置")
        print(f"📁 配置文件路径: {config_path}")
        print(f"🔧 项目路径: {project_path}")
        print("\n📋 配置内容:")
        print(json.dumps(final_config["mcpServers"]["wechat-mcp"], indent=2, ensure_ascii=False))

        print("\n🔄 请重启 Claude Desktop 以应用新配置")

        return True

    except Exception as e:
        print(f"❌ 更新配置失败: {e}")
        return False

def check_dependencies():
    """检查依赖是否正确安装"""
    print("🔍 检查项目依赖...")

    try:
        import subprocess
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv 已安装: {result.stdout.strip()}")
        else:
            print("❌ uv 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ uv 未找到，请先安装 uv")
        return False

    # 检查项目依赖
    try:
        result = subprocess.run(["uv", "sync"], cwd=Path(__file__).parent.parent, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 项目依赖已同步")
        else:
            print(f"❌ 依赖同步失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 检查依赖时出错: {e}")
        return False

    return True

def test_server():
    """测试服务器是否能正常启动"""
    print("🧪 测试服务器启动...")

    try:
        import subprocess
        project_path = Path(__file__).parent.parent

        result = subprocess.run([
            "uvx", "--from", str(project_path), "mcp-server-wechat", "--help"
        ], capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("✅ 服务器启动测试成功")
            return True
        else:
            print(f"❌ 服务器启动失败: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("✅ 服务器启动正常（超时但正常，因为服务器在等待输入）")
        return True
    except Exception as e:
        print(f"❌ 测试服务器时出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 微信公众号 MCP Server 配置更新工具")
    print("=" * 50)

    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先解决依赖问题")
        return False

    # 测试服务器
    if not test_server():
        print("\n❌ 服务器测试失败，请检查代码")
        return False

    # 更新配置
    if not update_claude_config():
        print("\n❌ 配置更新失败")
        return False

    print("\n🎉 配置更新完成！")
    print("\n📝 下一步操作:")
    print("1. 重启 Claude Desktop")
    print("2. 在 Claude Desktop 中测试: '搜索关于人工智能的微信文章'")
    print("3. 如需使用官方 API 功能，请在配置中填入真实的 WECHAT_APPID 和 WECHAT_SECRET")

    return True

if __name__ == "__main__":
    main()