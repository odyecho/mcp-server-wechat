"""
微信 API 客户端

提供微信公众号 API 的封装和调用功能。
"""

import os
import time
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from fastmcp.exceptions import ToolError

from .errors import handle_wechat_api_error, handle_environment_error
from .cache import cache_manager


class WeChatAPIClient:
    """微信公众号 API 客户端"""
    
    def __init__(self):
        self.app_id = os.getenv("WECHAT_APPID")
        self.app_secret = os.getenv("WECHAT_SECRET")
        self.configured = bool(self.app_id and self.app_secret)
        
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
        self.access_token = None
        self.token_expires_at = None
        
    def _check_configuration(self):
        """检查配置是否完整"""
        if not self.configured:
            handle_environment_error()
        
    async def get_access_token(self) -> str:
        """获取或刷新 access_token"""
        self._check_configuration()
        
        # 检查缓存的 token
        cached_token = cache_manager.get("access_token")
        if cached_token:
            return cached_token
            
        # 获取新的 token
        url = f"{self.base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "access_token" in data:
                    access_token = data["access_token"]
                    expires_in = data.get("expires_in", 7200)
                    
                    # 缓存 token，提前 5 分钟过期
                    cache_manager.set("access_token", access_token, ttl=expires_in - 300)
                    return access_token
                else:
                    error_code = data.get("errcode", 0)
                    error_msg = data.get("errmsg", "未知错误")
                    handle_wechat_api_error(error_code, error_msg)
                    
            except httpx.RequestError as e:
                raise ToolError(f"网络请求失败：{str(e)}")
    
    async def make_request(self, endpoint: str, params: Optional[Dict] = None, method: str = "POST") -> Dict[str, Any]:
        """通用 API 请求方法"""
        access_token = await self.get_access_token()
        url = f"{self.base_url}/{endpoint}"
        
        if params is None:
            params = {}
        params["access_token"] = access_token
        
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, params=params)
                    else:
                        response = await client.post(url, json=params)
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    error_code = data.get("errcode", 0)
                    if error_code != 0:
                        error_msg = data.get("errmsg", "未知错误")
                        
                        # 如果是 token 过期，清除缓存并重试
                        if error_code == 42001 and attempt < max_retries - 1:
                            cache_manager.set("access_token", None, ttl=0)  # 清除缓存
                            await asyncio.sleep(1)  # 等待 1 秒后重试
                            continue
                            
                        handle_wechat_api_error(error_code, error_msg)
                        
                    return data
                    
            except httpx.RequestError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise ToolError(f"网络请求失败：{str(e)}")
        
        raise ToolError("API 请求重试次数超限")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """获取公众号基本信息"""
        # 检查缓存
        cached_info = cache_manager.get("account_info")
        if cached_info:
            return cached_info
        
        # 获取基本信息（通过获取素材总数来验证权限）
        try:
            material_count = await self.make_request("material/get_materialcount")
            
            account_info = {
                "name": "当前公众号",  # 无法通过 API 直接获取名称
                "type": "公众号",
                "verified": True,  # 能调用 API 说明已认证
                "status": "正常",
                "stats": {
                    "图片素材": material_count.get("image_count", 0),
                    "语音素材": material_count.get("voice_count", 0),
                    "视频素材": material_count.get("video_count", 0),
                    "图文素材": material_count.get("news_count", 0)
                },
                "api_quota": {
                    "access_token获取": "2000次/天",
                    "素材管理": "10次/天"
                }
            }
            
            # 缓存 30 分钟
            cache_manager.set("account_info", account_info, ttl=1800)
            return account_info
            
        except Exception as e:
            raise ToolError(f"获取公众号信息失败：{str(e)}")
    
    async def list_articles(self, offset: int = 0, count: int = 10) -> List[Dict[str, Any]]:
        """获取图文素材列表"""
        # 检查缓存
        cache_key = f"articles_list_{offset}_{count}"
        cached_articles = cache_manager.get("articles_list", offset=offset, count=count)
        if cached_articles:
            return cached_articles
        
        params = {
            "type": "news",  # 图文消息
            "offset": offset,
            "count": min(count, 20)  # 最多 20 条
        }
        
        try:
            response = await self.make_request("material/batchget_material", params)
            
            articles = []
            items = response.get("item", [])
            
            for item in items:
                media_id = item.get("media_id", "")
                update_time = item.get("update_time", 0)
                
                # 获取图文消息内容
                content = item.get("content", {})
                news_items = content.get("news_item", [])
                
                for news_item in news_items:
                    article = {
                        "media_id": media_id,
                        "title": news_item.get("title", ""),
                        "author": news_item.get("author", ""),
                        "digest": news_item.get("digest", ""),
                        "url": news_item.get("url", ""),
                        "content_source_url": news_item.get("content_source_url", ""),
                        "thumb_media_id": news_item.get("thumb_media_id", ""),
                        "show_cover_pic": news_item.get("show_cover_pic", 0),
                        "update_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(update_time))
                    }
                    articles.append(article)
            
            # 缓存 30 分钟
            cache_manager.set("articles_list", articles, ttl=1800, offset=offset, count=count)
            return articles
            
        except Exception as e:
            raise ToolError(f"获取文章列表失败：{str(e)}")
    
    async def get_article_content(self, media_id: str) -> Dict[str, Any]:
        """获取文章详细内容"""
        # 检查缓存
        cached_content = cache_manager.get("article_content", media_id=media_id)
        if cached_content:
            return cached_content
        
        params = {
            "media_id": media_id
        }
        
        try:
            response = await self.make_request("material/get_material", params)
            
            # 解析响应
            news_items = response.get("news_item", [])
            if not news_items:
                raise ToolError(f"未找到 media_id 为 {media_id} 的文章")
            
            # 取第一篇文章（通常图文消息只有一篇）
            news_item = news_items[0]
            
            article = {
                "media_id": media_id,
                "title": news_item.get("title", ""),
                "author": news_item.get("author", ""),
                "digest": news_item.get("digest", ""),
                "content": news_item.get("content", ""),
                "content_source_url": news_item.get("content_source_url", ""),
                "url": news_item.get("url", ""),
                "thumb_media_id": news_item.get("thumb_media_id", ""),
                "show_cover_pic": news_item.get("show_cover_pic", 0),
                "need_open_comment": news_item.get("need_open_comment", 0),
                "only_fans_can_comment": news_item.get("only_fans_can_comment", 0)
            }
            
            # 估算字数和阅读时间
            content = article.get("content", "")
            word_count = len(content)
            read_time_minutes = max(1, word_count // 300)  # 按每分钟 300 字计算
            
            article["word_count"] = word_count
            article["read_time_minutes"] = read_time_minutes
            
            # 缓存 24 小时
            cache_manager.set("article_content", article, ttl=86400, media_id=media_id)
            return article
            
        except Exception as e:
            raise ToolError(f"获取文章内容失败：{str(e)}")


# 全局客户端实例
wechat_client = WeChatAPIClient()