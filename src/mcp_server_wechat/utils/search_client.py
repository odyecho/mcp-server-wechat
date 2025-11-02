"""
搜狗微信搜索客户端

提供搜狗微信搜索功能，用于访问公开的微信文章。
"""

import re
import httpx
import asyncio
import random
from typing import List, Dict, Any, Optional
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
from fastmcp.exceptions import ToolError

from .errors import handle_search_error
from .cache import cache_manager


class SogouWeChatSearchClient:
    """搜狗微信搜索客户端"""
    
    def __init__(self):
        self.base_url = "https://weixin.sogou.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
    async def search_articles(
        self, 
        query: str, 
        account_name: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """搜索微信文章"""
        # 检查缓存
        cache_key = f"search_{query}_{account_name}_{limit}"
        cached_results = cache_manager.get("search_results", query=query, account_name=account_name, limit=limit)
        if cached_results:
            return cached_results
        
        # 随机延迟避免反爬
        await asyncio.sleep(random.uniform(1, 3))
        
        search_url = f"{self.base_url}/weixin"
        params = {
            "query": query,
            "type": 2,  # 文章搜索
            "page": 1,
            "ie": "utf8"
        }
        
        if account_name:
            params["account"] = account_name
            
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                response = await client.get(search_url, params=params)
                
                if response.status_code != 200:
                    handle_search_error(response.status_code, response.text)
                
                # 解析搜索结果
                results = self._parse_search_results(response.text, limit)
                
                # 缓存 1 小时
                cache_manager.set("search_results", results, ttl=3600, query=query, account_name=account_name, limit=limit)
                return results
                
        except httpx.RequestError as e:
            raise ToolError(f"搜索请求失败：{str(e)}")
    
    def _parse_search_results(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """解析搜索结果HTML"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            results = []
            
            # 查找文章结果
            result_items = soup.find_all('div', class_='news-box')
            
            for item in result_items[:limit]:
                try:
                    # 提取标题和链接
                    title_elem = item.find('h3')
                    if not title_elem:
                        continue
                        
                    title_link = title_elem.find('a')
                    if not title_link:
                        continue
                        
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # 提取公众号名称
                    account_elem = item.find('a', class_='account')
                    account = account_elem.get_text(strip=True) if account_elem else "未知公众号"
                    
                    # 提取摘要
                    digest_elem = item.find('p', class_='txt-info')
                    digest = digest_elem.get_text(strip=True) if digest_elem else ""
                    
                    # 提取发布时间
                    time_elem = item.find('span', class_='s2')
                    publish_time = time_elem.get_text(strip=True) if time_elem else ""
                    
                    # 清理时间格式
                    if publish_time:
                        publish_time = re.sub(r'[^\d\-\s:]', '', publish_time).strip()
                    
                    result = {
                        "title": title,
                        "account": account,
                        "url": url,
                        "digest": digest,
                        "publish_time": publish_time
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    # 单个结果解析失败不影响其他结果
                    continue
            
            return results
            
        except Exception as e:
            raise ToolError(f"解析搜索结果失败：{str(e)}")
    
    async def search_accounts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索公众号"""
        # 检查缓存
        cached_results = cache_manager.get("account_search", query=query, limit=limit)
        if cached_results:
            return cached_results
        
        # 随机延迟避免反爬
        await asyncio.sleep(random.uniform(1, 3))
        
        search_url = f"{self.base_url}/weixin"
        params = {
            "query": query,
            "type": 1,  # 公众号搜索
            "page": 1,
            "ie": "utf8"
        }
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
                response = await client.get(search_url, params=params)
                
                if response.status_code != 200:
                    handle_search_error(response.status_code, response.text)
                
                # 解析搜索结果
                results = self._parse_account_results(response.text, limit)
                
                # 缓存 1 小时
                cache_manager.set("account_search", results, ttl=3600, query=query, limit=limit)
                return results
                
        except httpx.RequestError as e:
            raise ToolError(f"搜索请求失败：{str(e)}")
    
    def _parse_account_results(self, html: str, limit: int) -> List[Dict[str, Any]]:
        """解析公众号搜索结果"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            results = []
            
            # 查找公众号结果
            result_items = soup.find_all('div', class_='results')
            
            for item in result_items[:limit]:
                try:
                    # 提取公众号名称
                    name_elem = item.find('h3')
                    if not name_elem:
                        continue
                        
                    name_link = name_elem.find('a')
                    if not name_link:
                        continue
                        
                    name = name_link.get_text(strip=True)
                    
                    # 提取描述
                    desc_elem = item.find('dd')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # 提取认证信息
                    auth_elem = item.find('span', class_='sp-ico')
                    verified = bool(auth_elem)
                    
                    result = {
                        "name": name,
                        "description": description,
                        "verified": verified
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    # 单个结果解析失败不影响其他结果
                    continue
            
            return results
            
        except Exception as e:
            raise ToolError(f"解析公众号搜索结果失败：{str(e)}")
    
    async def get_article_content(self, article_url: str) -> Dict[str, Any]:
        """获取文章内容"""
        # 检查缓存
        cached_content = cache_manager.get("public_article", url=article_url)
        if cached_content:
            return cached_content
        
        # 验证 URL 格式
        if not article_url.startswith("https://mp.weixin.qq.com/s/"):
            raise ToolError("无效的微信文章链接格式")
        
        # 随机延迟避免反爬
        await asyncio.sleep(random.uniform(2, 5))
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
                response = await client.get(article_url)
                
                if response.status_code != 200:
                    handle_search_error(response.status_code, response.text)
                
                # 解析文章内容
                content = self._parse_article_content(response.text, article_url)
                
                # 缓存 24 小时
                cache_manager.set("public_article", content, ttl=86400, url=article_url)
                return content
                
        except httpx.RequestError as e:
            raise ToolError(f"获取文章内容失败：{str(e)}")
    
    def _parse_article_content(self, html: str, url: str) -> Dict[str, Any]:
        """解析文章内容"""
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # 提取标题
            title_elem = soup.find('h1', class_='rich_media_title')
            title = title_elem.get_text(strip=True) if title_elem else "无标题"
            
            # 提取作者
            author_elem = soup.find('a', class_='rich_media_meta_link')
            author = author_elem.get_text(strip=True) if author_elem else "未知作者"
            
            # 提取发布时间
            time_elem = soup.find('em', id='publish_time')
            publish_time = time_elem.get_text(strip=True) if time_elem else ""
            
            # 提取正文内容
            content_elem = soup.find('div', class_='rich_media_content')
            if content_elem:
                # 移除脚本和样式
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # 获取纯文本内容
                content = content_elem.get_text(separator='\n', strip=True)
                
                # 提取图片链接
                images = []
                img_tags = content_elem.find_all('img')
                for img in img_tags:
                    src = img.get('data-src') or img.get('src')
                    if src:
                        images.append(src)
            else:
                content = "无法获取文章内容"
                images = []
            
            # 估算字数和阅读时间
            word_count = len(content)
            read_time_minutes = max(1, word_count // 300)
            
            article = {
                "title": title,
                "author": author,
                "publish_time": publish_time,
                "content": content,
                "url": url,
                "images": images,
                "word_count": word_count,
                "read_time_minutes": read_time_minutes
            }
            
            return article
            
        except Exception as e:
            raise ToolError(f"解析文章内容失败：{str(e)}")


# 全局搜索客户端实例
search_client = SogouWeChatSearchClient()