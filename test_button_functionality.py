#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Telegram bot button functionality
"""

import sys
import os
import yaml
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.telegram_bot import TelegramBot

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path: str = "src/config/config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        if not os.path.exists(config_path):
            logger.error(f"配置文件不存在: {config_path}")
            logger.error(f"请复制配置模板: cp src/config/config.yaml.example {config_path}")
            sys.exit(1)
            
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        logger.info("配置文件加载成功")
        return config
        
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

async def mock_fetch_latest():
    """Mock fetch latest content"""
    logger.info("模拟获取最新消息")
    return {"success": True, "count": 2}

async def mock_fetch_news():
    """Mock fetch news content"""
    logger.info("模拟获取новости社群消息")
    return {"success": True, "count": 3}

def test_telegram_bot_buttons():
    """Test Telegram bot button functionality"""
    logger.info("=== 测试Telegram Bot按钮功能 ===")
    
    # 加载配置
    config = load_config()
    
    # 获取Telegram配置
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token")
    chat_id = telegram_config.get("chat_id")
    
    if not bot_token or not chat_id:
        logger.error("Telegram配置不完整，请在config.yaml中设置bot_token和chat_id")
        return
    
    # 创建TelegramBot实例
    telegram_bot = TelegramBot(bot_token, chat_id)
    
    # 注册回调函数
    telegram_bot.register_fetch_callback(mock_fetch_latest)
    telegram_bot.register_fetch_news_callback(mock_fetch_news)
    
    # 启动bot
    try:
        telegram_bot.start()
        logger.info("Telegram Bot已启动")
        logger.info("请在Telegram中发送/start命令来测试按钮功能")
        logger.info("测试完成后，按Ctrl+C停止脚本")
        
        # 运行轮询
        telegram_bot.run_polling()
        
    except KeyboardInterrupt:
        logger.info("\n测试已停止")
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_telegram_bot_buttons()
