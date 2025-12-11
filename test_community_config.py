#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.vk_api import VKAPI
from src.telegram_bot import TelegramBot

def test_community_config_standalone():
    """独立测试社群配置"""
    logger.info("=" * 50)
    logger.info("开始独立测试社群配置")
    logger.info("=" * 50)
    
    # 创建模拟配置
    mock_config = {
        "vk": {
            "access_token": "mock_token",
            "api_version": "5.131",
            "communities": [
                {
                    "name": "news",
                    "display_name": "новости社群",
                    "source": {
                        "type": "wall",
                        "id": "-123456789"
                    }
                },
                {
                    "name": "tech",
                    "display_name": "科技资讯",
                    "source": {
                        "type": "wall",
                        "id": "techcommunity"
                    }
                },
                {
                    "name": "sports",
                    "display_name": "体育新闻",
                    "source": {
                        "type": "wall",
                        "id": "111222333"
                    }
                }
            ]
        },
        "telegram": {
            "bot_token": "mock_token",
            "chat_id": "123456789"
        }
    }
    
    logger.info("1. 测试模拟配置结构")
    communities = mock_config.get("vk", {}).get("communities", [])
    logger.info(f"   社群数量: {len(communities)}")
    logger.info(f"   社群列表: {communities}")
    
    if len(communities) > 0:
        logger.info("   ✅ 模拟配置包含社群信息")
    else:
        logger.info("   ❌ 模拟配置不包含社群信息")
        return False
    
    # 测试TelegramBot的社群设置功能
    logger.info("\n2. 测试TelegramBot的社群设置功能")
    telegram_bot = TelegramBot(
        mock_config.get("telegram", {}).get("bot_token", ""),
        mock_config.get("telegram", {}).get("chat_id", "")
    )
    telegram_bot.set_communities(communities)
    
    logger.info(f"   设置的社群数量: {len(telegram_bot.communities)}")
    logger.info(f"   设置的社群列表: {telegram_bot.communities}")
    
    if len(telegram_bot.communities) > 0:
        logger.info("   ✅ TelegramBot成功设置社群")
    else:
        logger.info("   ❌ TelegramBot设置社群失败")
        return False
    
    # 测试命令生成功能
    logger.info("\n3. 测试社群命令生成")
    for community in telegram_bot.communities:
        command = f"fetch_{community.get('name', '')}"
        logger.info(f"   - {command}: 获取{community.get('display_name', '')}的最新消息")
    
    logger.info("\n" + "=" * 50)
    logger.info("社群配置独立测试完成")
    logger.info("=" * 50)
    return True

if __name__ == "__main__":
    success = test_community_config_standalone()
    sys.exit(0 if success else 1)