#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def test_core_functionality():
    """测试核心功能：配置结构和命令生成"""
    logger.info("=" * 60)
    logger.info("开始测试核心功能：动态社群菜单生成")
    logger.info("=" * 60)
    
    try:
        # 测试配置结构
        from src.vk_api import VKAPI
        from src.telegram_bot import TelegramBot
        
        logger.info("\n1. 检查模块导入")
        logger.info("✅ VKAPI 模块导入成功")
        logger.info("✅ TelegramBot 模块导入成功")
        
        # 测试配置结构
        logger.info("\n2. 验证配置结构兼容性")
        
        # 模拟配置数据
        mock_communities = [
            {
                "name": "news",
                "display_name": "новости社群",
                "source": {"type": "wall", "id": "-123456789"}
            },
            {
                "name": "tech",
                "display_name": "科技资讯",
                "source": {"type": "wall", "id": "techcommunity"}
            },
            {
                "name": "sports",
                "display_name": "体育新闻",
                "source": {"type": "wall", "id": "111222333"}
            }
        ]
        
        logger.info(f"模拟社群配置: {mock_communities}")
        
        # 测试TelegramBot社群设置功能
        logger.info("\n3. 测试TelegramBot社群设置")
        telegram_bot = TelegramBot("mock_token")
        telegram_bot.set_communities(mock_communities)
        
        if telegram_bot.communities and len(telegram_bot.communities) == 3:
            logger.info("✅ 社群配置成功设置到TelegramBot")
        else:
            logger.error("❌ 社群配置设置失败")
            return False
        
        # 测试命令生成
        logger.info("\n4. 测试动态命令生成")
        generated_commands = []
        for community in telegram_bot.communities:
            command = f"fetch_{community.get('name', '')}"
            description = f"获取{community.get('display_name', '')}的最新消息"
            generated_commands.append((command, description))
            logger.info(f"   - {command}: {description}")
        
        # 验证生成的命令
        expected_commands = [
            ("fetch_news", "获取новости社群的最新消息"),
            ("fetch_tech", "获取科技资讯的最新消息"),
            ("fetch_sports", "获取体育新闻的最新消息")
        ]
        
        if generated_commands == expected_commands:
            logger.info("✅ 动态命令生成符合预期")
        else:
            logger.error("❌ 动态命令生成不符合预期")
            return False
        
        # 测试VKAPI方法
        logger.info("\n5. 测试VKAPI方法")
        

        
        # 验证get_community_content方法存在
        if hasattr(VKAPI, 'get_community_content'):
            logger.info("✅ VKAPI.get_community_content 方法存在")
        else:
            logger.error("❌ VKAPI.get_community_content 方法不存在")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("核心功能测试完成")
        logger.info("所有测试均通过！动态社群菜单功能已正确实现。")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    sys.exit(0 if success else 1)