import requests
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VKAPI:
    def __init__(self, access_token: str, api_version: str = "5.131"):
        self.access_token = access_token  # 服务令牌
        self.api_version = api_version
        self.base_url = "https://api.vk.com/method"
        self.rate_limit_delay = 0.34  # VK API rate limit: 3 requests per second
    
    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送VK API请求并处理响应
        
        Args:
            method: VK API方法名
            params: 请求参数
        """
        params.update({
            "access_token": self.access_token,
            "v": self.api_version
        })
        
        try:
            response = requests.get(f"{self.base_url}/{method}", params=params)
            time.sleep(self.rate_limit_delay)
            
            if response.status_code != 200:
                logger.error(f"VK API请求失败，状态码: {response.status_code}")
                return {}
            
            data = response.json()
            if "error" in data:
                logger.error(f"VK API错误: {data['error']['error_msg']}")
                return {}
            
            return data.get("response", {})
            
        except Exception as e:
            logger.error(f"VK API request exception: {str(e)}")
            return {}
    
    def resolve_screen_name(self, screen_name: str) -> str:
        """Resolve a screen name to its corresponding object ID"""
        params = {
            "screen_name": screen_name
        }
        
        response = self._make_request("utils.resolveScreenName", params)
        if not response:
            logger.error(f"Failed to resolve screen name: {screen_name}")
            return ""
        
        # VK API returns different types of objects, we need to handle them differently
        object_type = response.get("type")
        object_id = response.get("object_id")
        
        if not object_type or not object_id:
            logger.error(f"Invalid response for screen name: {screen_name}")
            return ""
        
        # For groups and public pages, we need to add a minus sign
        if object_type in ["group", "public"]:
            return f"-{object_id}"
        else:
            return str(object_id)
    
    def get_wall_content(self, owner_identifier: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get wall content from user or public page
        
        Args:
            owner_identifier: Either an ID (string) or a screen name
            count: Number of posts to retrieve
            
        Returns:
            List of wall posts
        """
        # Check if it's a screen name (doesn't start with digit or minus)
        if owner_identifier and not (owner_identifier[0].isdigit() or owner_identifier.startswith("-")):
            owner_id = self.resolve_screen_name(owner_identifier)
            if not owner_id:
                logger.error(f"Failed to get wall content: Could not resolve screen name {owner_identifier}")
                return []
        else:
            owner_id = owner_identifier
        
        params = {
            "owner_id": owner_id,
            "count": count
        }
        
        response = self._make_request("wall.get", params)
        return response.get("items", [])
    
    def get_newsfeed(self, count: int = 10, start_time: int = None, end_time: int = None, keyword: str = "новости", start_from: str = None) -> List[Dict[str, Any]]:
        """Get newsfeed content using VK newsfeed.search API
        
        Args:
            count: Number of news items to retrieve
            start_time: Earliest timestamp (in Unix time) of a news item to return
            end_time: Latest timestamp (in Unix time) of a news item to return
            keyword: Search keyword for newsfeed search
            start_from: Start parameter for pagination
            
        Returns:
            Tuple containing list of newsfeed items and next page token
        """
        params = {
            "q": keyword,  # 搜索关键词
            "count": count
        }
        
        # Add optional parameters if provided
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if start_from:
            params["start_from"] = start_from
        
        response = self._make_request("newsfeed.search", params)
        items = response.get("items", [])
        next_page = response.get("next_from")
        return items, next_page

    def get_community_content(self, communities: List[Dict[str, Any]], community_name: str, max_content_per_fetch: int = 20) -> List[Dict[str, Any]]:
        """Get content from a specific community"""
        for community in communities:
            if community.get("name") == community_name:
                try:
                    source = community.get("source", {})
                    if source:
                        content = self.get_wall_content(source["id"], max_content_per_fetch)
                        # 为内容添加社群标识
                        for item in content:
                            item["community_name"] = community.get("name", "")
                            item["community_display_name"] = community.get("display_name", "")
                        logger.info(f"Retrieved {len(content)} items from community {community_name}")
                        return content
                except Exception as e:
                    logger.error(f"Failed to retrieve content from community {community_name}: {str(e)}")
        
        logger.warning(f"Community {community_name} not found or no source configured")
        return []

    def format_content(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format VK content to unified structure"""
        if not item:
            return {}
        
        # 获取内容类型
        if "post_type" in item:
            content_type = item["post_type"]
        else:
            content_type = "post"
        
        # 获取内容文本
        text = item.get("text", "")
        
        # 获取作者信息
        if "owner_id" in item:
            author = item["owner_id"]
        else:
            author = "unknown"
        
        # 获取发布时间
        date = item.get("date", 0)
        
        # 获取内容链接
        if "owner_id" in item and "id" in item:
            url = f"https://vk.com/wall{item['owner_id']}_{item['id']}"
        else:
            url = ""
        
        return {
            "id": item.get("id", ""),
            "type": content_type,
            "text": text,
            "author": author,
            "date": date,
            "url": url,
            "raw": item
        }