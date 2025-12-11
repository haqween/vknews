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
        
        # 初始化模块
        self._initialize_modules()
    
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
    

    

    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("Starting VK to Telegram News Summary & Translation Bot...")
            
            # Start Telegram bot
            self.telegram_api.start(self.vknew_bot)
            logger.info("Telegram bot started successfully")
        
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