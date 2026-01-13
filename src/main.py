import yaml
import logging
import asyncio
import os
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import modules
from src.vk_api import VKAPI
from src.ai_api import AIProcessor
from src.text_processor import TextProcessor
from src.telegram_api import TelegramAPI
from src.vknew_bot import VKNewBot

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VKTelegramBot:
    def __init__(self, config_path: str = None):
        # 加载环境变量
        load_dotenv()
        
        # 自动检测配置文件路径
        if config_path is None:
            # 检查当前目录是否有config/config.yaml
            if os.path.exists("config/config.yaml"):
                self.config_path = "config/config.yaml"
            # 检查上级目录是否有src/config/config.yaml
            elif os.path.exists("../src/config/config.yaml"):
                self.config_path = "../src/config/config.yaml"
            # 默认使用src/config/config.yaml
            else:
                self.config_path = "src/config/config.yaml"
        else:
            self.config_path = config_path
        
        self.config = self._load_config()
        self.vk_api = None
        self.ai_processor = None
        self.telegram_api = None
        self.text_processor = None
        self.vknew_bot = None
        
        # 初始化活动帖子缓存
        self.activity_cache = {}  # 缓存格式：{cache_key: (is_activity, timestamp)}
        
        # 初始化模块
        self._initialize_modules()
        
    def _is_cached(self, url: str) -> bool:
        """检查帖子是否已缓存且未过期"""
        # 使用帖子url作为缓存key
        cache_key = url
        if cache_key in self.activity_cache:
            is_activity, timestamp = self.activity_cache[cache_key]
            # 根据是否为活动设置不同的缓存时间
            if is_activity:
                # 活动帖子缓存5小时
                if time.time() - timestamp < 18000:  # 5小时 = 18000秒
                    return True
            else:
                # 非活动帖子缓存10分钟
                if time.time() - timestamp < 600:  # 10分钟 = 600秒
                    return True
            # 缓存过期，删除
            del self.activity_cache[cache_key]
        return False
    
    def _get_cached_result(self, url: str) -> bool:
        """获取缓存结果"""
        # 使用帖子url作为缓存key
        cache_key = url
        if cache_key in self.activity_cache:
            is_activity, timestamp = self.activity_cache[cache_key]
            return is_activity
        return False
    
    def _cache_result(self, url: str, is_activity: bool):
        """缓存判断结果"""
        # 使用帖子url作为缓存key
        cache_key = url
        self.activity_cache[cache_key] = (is_activity, time.time())
        # 清理过期缓存
        self._clean_expired_cache()
    
    def _clean_expired_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        for key, (is_activity, timestamp) in self.activity_cache.items():
            if is_activity:
                # 活动帖子缓存5小时
                if current_time - timestamp >= 18000:  # 5小时 = 18000秒
                    expired_keys.append(key)
            else:
                # 非活动帖子缓存10分钟
                if current_time - timestamp >= 600:  # 10分钟 = 600秒
                    expired_keys.append(key)
        
        # 删除过期缓存
        for key in expired_keys:
            del self.activity_cache[key]
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration file and resolve environment variables"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Config file not found: {self.config_path}")
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
                
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_content = f.read()
            
            # 解析环境变量占位符
            def resolve_env_vars(content):
                import re
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, content)
                for match in matches:
                    env_value = os.getenv(match, f"${{{match}}}")
                    # 打印获取到的环境变量的前5位
                    if not env_value.startswith('${'):
                        print(f"Environment variable '{match}' value (first 5 chars): {env_value[:5]}...")
                    content = content.replace(f"${{{match}}}", env_value)
                return content
            
            resolved_content = resolve_env_vars(config_content)
            config = yaml.safe_load(resolved_content)
            
            logger.info("Config file loaded and environment variables resolved successfully")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config file: {str(e)}")
            raise
    
    def _initialize_modules(self):
        """Initialize all modules"""
        try:
            # Initialize VK API module
            vk_config = self.config.get("vk", {})
            self.vk_api = VKAPI(
                access_token=vk_config.get("access_token"),
                api_version=vk_config.get("api_version", "5.131")
            )
            logger.info("VK API module initialized successfully")
            
            # Initialize AI processing module
            ai_config = self.config.get("ai", {})
            providers = ai_config.get("providers", [])
            
            self.ai_processor = AIProcessor(
                providers=providers
            )
            logger.info("AI processing module initialized successfully")
            
            # Initialize Telegram bot module
            telegram_config = self.config.get("telegram", {})
            self.telegram_api = TelegramAPI(
                bot_token=telegram_config.get("bot_token"),
                webhook_url=telegram_config.get("webhook_url"),
                port=telegram_config.get("webhook_port", 8443)
            )
            logger.info("Telegram API module initialized successfully")
            
            # Create and set text processor
            self.text_processor = TextProcessor(
                ai_providers=self.config.get("ai", {}).get("providers", [])
            )
            logger.info("Text processor module initialized successfully")
            
            # Initialize VKNewBot
            self.vknew_bot = VKNewBot()
            self.vknew_bot.set_telegram_api(self.telegram_api)
            self.vknew_bot.set_vk_api(self.vk_api)
            self.vknew_bot.set_ai_processor(self.ai_processor)
            self.vknew_bot.set_text_processor(self.text_processor)
            self.vknew_bot.set_config(self.config)
            logger.info("VKNewBot module initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize modules: {str(e)}")
            raise
    

    

    
    async def _scheduled_task(self):
        """定时任务：每分钟从VK获取最新帖子，判断是否为活动并推送给用户"""
        import asyncio
        import random
        logger.info("Starting scheduled task")
        
        # 关键词列表
        keywords = ["афиша СПб", "выставка", "экскурсия", "вечер", "лекция"]
        
        while True:
            try:
                logger.info("Running scheduled task: checking for new activities")
                
                # 随机选择一个关键词
                keyword = random.choice(keywords)
                logger.info(f"Using keyword: {keyword}")
                
                # 从VK获取最新帖子，使用选择的关键词作为过滤条件，分页获取，每次取20条，取5页
                all_raw_content = []
                max_pages = 5
                current_page = 0
                start_from = None
                
                while current_page < max_pages:
                    # 分页获取帖子
                    raw_content, start_from = self.vk_api.get_newsfeed(count=20, keyword=keyword, start_from=start_from)
                    logger.info(f"Fetched {len(raw_content)} posts from VK (page {current_page + 1}/{max_pages}) with keyword: {keyword}")
                    
                    # 添加到总列表
                    all_raw_content.extend(raw_content)
                    
                    # 如果没有更多页，退出循环
                    if not start_from:
                        logger.info("No more pages available, exiting pagination loop")
                        break
                    
                    # 增加页码
                    current_page += 1
                
                logger.info(f"Total posts fetched: {len(all_raw_content)}")
                
                # 处理每个帖子
                for raw_content in all_raw_content:
                    # 格式化帖子内容
                    content = self.vk_api.format_content(raw_content)
                    
                    # 获取帖子URL
                    post_url = content.get("url", "")
                    if not post_url:
                        continue
                    
                    # 检查是否有文本内容
                    text = content.get("text", "")
                    if not text:
                        continue
                    
                    # 检查是否已缓存
                    if self._is_cached(post_url):
                        logger.info(f"Post already processed, skipping: {post_url}")
                        continue
                    
                    # 调用AI判断是否为活动
                    is_activity = self.text_processor.is_activity(text)
                    
                    # 缓存结果
                    self._cache_result(post_url, is_activity)
                    
                    # 如果是活动，推送给用户
                    if is_activity:
                        logger.info(f"Detected activity: {post_url}")
                        
                        # 直接创建包含链接的消息
                        message = f"🔗 <a href='{post_url}'>Обнаружено мероприятие: </a>"
                        
                        # 发送给所有注册用户
                        if self.vknew_bot.user_chat_ids:
                            for chat_id in self.vknew_bot.user_chat_ids:
                                try:
                                    # 使用Telegram API发送消息
                                    self.telegram_api.updater.bot.send_message(
                                        chat_id=chat_id,
                                        text=message,
                                        parse_mode='HTML'
                                    )
                                    logger.info(f"Sent activity to user {chat_id}")
                                except Exception as e:
                                    logger.error(f"Failed to send activity to user {chat_id}: {str(e)}")
            
            except Exception as e:
                logger.error(f"Error in scheduled task: {str(e)}")
            
            # 等待1分钟
            await asyncio.sleep(60)
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("Starting VK to Telegram News Summary & Translation Bot...")
            
            # 启动Telegram bot
            import threading
            threading.Thread(target=self.telegram_api.start, args=(self.vknew_bot,), daemon=True).start()
            logger.info("Telegram bot started successfully")
            
            # 启动定时任务
            import asyncio
            asyncio.create_task(self._scheduled_task())
            logger.info("Scheduled task started successfully")
            
            # 保持主程序运行
            while True:
                await asyncio.sleep(3600)  # 每小时检查一次
        
        except KeyboardInterrupt:
            logger.info("Bot stopped")
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        try:
            logger.info("Bot stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop bot: {str(e)}")

async def main():
    """Main function"""
    try:
        bot = VKTelegramBot()
        await bot.start()
    except Exception as e:
        logger.error(f"Program exited with exception: {str(e)}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())