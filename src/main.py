import yaml
import logging
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import modules
from src.vk_api import VKAPI
from src.ai_api import AIProcessor
from src.text_processor import TextProcessor
from src.telegram_bot import TelegramBot

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
        self.telegram_bot = None
        self.cache = set()  # 用于存储已处理的内容ID
        
        # 初始化模块
        self._initialize_modules()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration file and resolve environment variables"""
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Config file not found: {self.config_path}")
                logger.info(f"Please copy config template: cp src/config/config.yaml.example {self.config_path}")
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
            
            # Check if webhook_url is configured (required for webhook mode)
            webhook_url = telegram_config.get("webhook_url")
            if not webhook_url:
                raise ValueError("webhook_url is required in telegram config for webhook mode")
            
            self.telegram_bot = TelegramBot(
                bot_token=telegram_config.get("bot_token"),
                webhook_url=webhook_url,
                port=telegram_config.get("webhook_port", 8443)
            )
            self.telegram_bot.vk_api = self.vk_api
            self.telegram_bot.set_ai_processor(self.ai_processor)
            
            # Create and set text processor
            self.text_processor = TextProcessor(
                ai_providers=self.config.get("ai", {}).get("providers", [])
            )
            self.telegram_bot.set_text_processor(self.text_processor)
            
            # Register content fetch callback function
            self.telegram_bot.register_fetch_callback(self._fetch_and_process_content)
            
            logger.info("Telegram bot module initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize modules: {str(e)}")
            raise
    
    async def _fetch_and_process_content(self, chat_id: str = None, keyword: str = None) -> Dict[str, Any]:
        """Fetch content, process and send
        
        Args:
            chat_id: Optional, Telegram chat ID to send the content to
            keyword: Optional, Search keyword for VK API
        """
        try:
            logger.info("Starting VK content fetch...")
            
            # Get configuration
            ai_config = self.config.get("ai", {})
            system_config = self.config.get("system", {})
            
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
            processed_contents = self.text_processor.process_content_batch(content_list, ai_config)
            
            processed_count = len(processed_contents)
            
            # Send all processed contents as a single message if there are any
            if processed_contents:
                success = self.telegram_bot.send_multiple_processed_content(processed_contents, chat_id=chat_id)
                if not success:
                    logger.error("Failed to send multiple processed contents")
                    return {"success": False, "message": "发送内容失败"}
            
            logger.info(f"Successfully processed and sent {processed_count} items")
            return {"success": True, "count": processed_count}
            
        except Exception as e:
            logger.error(f"Failed to fetch and process content: {str(e)}")
            return {"success": False, "message": str(e)}
    

    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("Starting VK to Telegram News Summary & Translation Bot...")
            
            # Start Telegram bot
            self.telegram_bot.start()
            logger.info("Telegram bot started successfully")
            
            # 使用webhook模式
            logger.info("Starting bot in webhook mode...")
            self.telegram_bot.run_webhook()
            
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