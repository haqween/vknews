import logging
import datetime
from typing import Callable, Dict, Any, List
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

# Default keyword for searching news in Russian
DEFAULT_KEYWORD = "новости"

class VKNewBot:
    def __init__(self):
        self.user_chat_ids = set()  # 存储从用户消息中获取的聊天ID
        self.user_input_cache = {}  # 存储用户上一次的输入，格式：{chat_id: last_input}
        self.fetch_callback = None
        self.telegram_api = None
        self.vk_api = None
        self.ai_processor = None
        self.text_processor = None
        self.config = {}

    def set_telegram_api(self, telegram_api):
        """设置Telegram API实例"""
        self.telegram_api = telegram_api

    def set_vk_api(self, vk_api):
        """设置VK API实例"""
        self.vk_api = vk_api

    def set_ai_processor(self, ai_processor):
        """设置AI处理器实例"""
        self.ai_processor = ai_processor

    def set_text_processor(self, text_processor):
        """设置文本处理器实例"""
        self.text_processor = text_processor
    
    def set_config(self, config):
        """设置配置参数"""
        self.config = config

    def register_fetch_callback(self, callback: Callable):
        """注册内容获取回调函数"""
        self.fetch_callback = callback

    def start_handler(self, update: Update, context: CallbackContext):
        """处理/start命令"""
        # 存储用户的chat_id
        chat_id = update.message.chat_id
        self.user_chat_ids.add(chat_id)
        logger.info(f"New user registered with chat_id: {chat_id}")
        
        # 创建Reply Keyboard
        keyboard = [[KeyboardButton("刷一下")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        update.message.reply_text(
            "欢迎使用VK信息摘要翻译机器人！点击下方按钮刷新最新消息。",
            reply_markup=reply_markup
        )

    def keyboard_handler(self, update: Update, context: CallbackContext):
        """处理文本消息事件"""
        keyword = update.message.text
        chat_id = update.message.chat_id

        update.message.reply_text("正在获取最新消息...")
        if keyword == "刷一下":
            # 使用上一次的输入作为关键字，如果没有则使用默认的"новости"
            keyword = self.user_input_cache.get(chat_id, DEFAULT_KEYWORD)
            
        else:
            # 不是"刷一下"
            # 缓存用户输入
            self.user_input_cache[chat_id] = keyword
        
        self._execute_refresh(update, chat_id, keyword)

    def _execute_refresh(self, update, chat_id, keyword):
        """执行刷新操作"""
        try:
            import asyncio
            # 调用内部的内容获取和处理方法
            result = asyncio.run(self.fetch_and_process_content(chat_id=chat_id, keyword=keyword))
            if result and "success" in result and result["success"]:
                update.message.reply_text(result["message"])
                logger.info(f"Successfully fetched and sent {result['count']} newsfeed items with keyword: {keyword}")
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            update.message.reply_text("处理请求时出错，请稍后重试")
    
    def generate_multiple_processed_content(self, contents: List[Dict[str, Any]], chat_id=None):
        """Send multiple processed contents as a single message"""
        message = ""
        
        for i, content in enumerate(contents, 1):
            # Get content fields
            zh_summary = content.get("zh_summary", "")
            ru_summary = content.get("ru_summary", "")
            url = content.get("url", "")
            date_timestamp = content.get("date", 0)
            
            # Convert timestamp to readable time
            if date_timestamp:
                try:
                    publish_time = datetime.datetime.fromtimestamp(date_timestamp).strftime("%Y-%m-%d %H:%M")
                except Exception as e:
                    logger.error(f"Failed to convert timestamp {date_timestamp}: {e}")
                    publish_time = ""
            else:
                publish_time = ""
            
            # Format with publish time outside link
            message += f"🔗 <a href='{url}'><strong>{zh_summary}</strong></a>\n"
            message += f"<code>{ru_summary}（{publish_time}）</code>"
            
            # Consistent spacing at the end
            message += "\n"
        
        # Remove trailing newlines
        message = message.rstrip("\n")

        return message
        

    async def fetch_and_process_content(self, chat_id: str = None, keyword: str = None) -> Dict[str, Any]:
        """Fetch content, process and send
        
        Args:
            chat_id: Optional, Telegram chat ID to send the content to
            keyword: Optional, Search keyword for VK API
        """
        try:
            logger.info("Starting VK content fetch...")
            
            # Fetch newsfeed content
            raw_content_list = self.vk_api.get_newsfeed(keyword=keyword)

            logger.info(f"Fetched {len(raw_content_list)} VK items")
            
            # Process all fetched content regardless of whether it's been processed before
            content_list = []
            for raw_content in raw_content_list:
                content = self.vk_api.format_content(raw_content)
                content_list.append(content)
            
            if not content_list:
                logger.info("No content to process")
                return {"success": True, "count": 0}
            
            # Process content in batch
            ai_config = self.config.get("ai", {})
            processed_contents = self.text_processor.process_content_batch(content_list, ai_config)
            
            # Send all processed contents as a single message if there are any
            if processed_contents:
                # Filter contents to ensure we only send messages with all required fields
                filtered_contents = [
                    content for content in processed_contents
                    if content.get("zh_summary", "") and content.get("ru_summary", "") and content.get("url", "")
                ]
                
                if not filtered_contents:
                    logger.info("No valid content to send (missing zh_summary, ru_summary, or url)")
                    return {"success": False, "message": "获取消息失败"}
                message = self.generate_multiple_processed_content(filtered_contents, chat_id=chat_id)
                if not message:
                    logger.error("Failed to send multiple processed contents")
                    return {"success": False, "message": "发送内容失败"}
            
            return {"success": True, "message": message}
            
        except Exception as e:
            logger.error(f"Failed to fetch and process content: {str(e)}")
            return {"success": False, "message": str(e)}
