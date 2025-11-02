"""
错误处理工具

定义自定义异常类型和错误处理函数。
"""

from fastmcp.exceptions import ToolError
from typing import Optional


class WeChatAPIError(ToolError):
    """微信 API 错误"""
    pass


class RateLimitError(ToolError):
    """频率限制错误"""
    pass


class AuthenticationError(ToolError):
    """认证错误"""
    pass


def handle_wechat_api_error(error_code: int, error_msg: str) -> None:
    """处理微信 API 错误"""
    error_messages = {
        40001: """AppSecret 错误或者 AppSecret 不属于这个公众号

解决方案：
1. 检查 WECHAT_SECRET 环境变量
2. 确认 AppSecret 与 AppID 匹配
3. 在微信公众平台重新生成 AppSecret

配置示例：
export WECHAT_APPID=your_app_id
export WECHAT_SECRET=your_app_secret""",

        40013: """不合法的 AppID

解决方案：
1. 检查 WECHAT_APPID 环境变量
2. 确认 AppID 格式正确
3. 确认公众号已认证""",

        42001: """access_token 超时

解决方案：
1. 系统会自动刷新 token
2. 请稍后重试
3. 如果问题持续，请检查系统时间""",

        45009: """接口调用超过限制

当前限制：
- access_token 获取：2000次/天
- 素材管理：10次/天

建议：
1. 减少 API 调用频率
2. 使用缓存避免重复请求
3. 明天重试""",

        48001: """api 功能未授权

解决方案：
1. 确认公众号类型支持此功能
2. 检查公众号认证状态
3. 联系微信客服开通权限"""
    }
    
    if error_code in error_messages:
        raise WeChatAPIError(error_messages[error_code])
    else:
        raise WeChatAPIError(f"微信 API 错误 ({error_code}): {error_msg}")


def handle_search_error(status_code: int, response_text: str) -> None:
    """处理搜索错误"""
    if status_code == 429:
        raise RateLimitError("""搜索请求被限制

可能原因：
1. 请求频率过快
2. 触发验证码验证
3. IP 被临时封禁

建议：
1. 等待 5-10 分钟后重试
2. 减少搜索频率
3. 使用更具体的搜索关键词

如果问题持续，请稍后再试。""")
    
    elif "验证码" in response_text or "captcha" in response_text.lower():
        raise ToolError("""触发验证码验证

这是正常的反爬保护机制。

建议：
1. 等待 10-30 分钟后重试
2. 减少搜索频率
3. 优先使用官方 API 功能

验证码无法自动处理，请稍后重试。""")
    
    else:
        raise ToolError(f"搜索请求失败 (HTTP {status_code})")


def handle_environment_error() -> None:
    """处理环境配置错误"""
    raise AuthenticationError("""微信公众号配置缺失

请设置以下环境变量：
export WECHAT_APPID=your_app_id
export WECHAT_SECRET=your_app_secret

获取方式：
1. 登录微信公众平台 (mp.weixin.qq.com)
2. 进入"开发" -> "基本配置"
3. 获取 AppID 和生成 AppSecret
4. 将服务器 IP 添加到白名单

注意：需要已认证的公众号才能使用 API 功能。""")