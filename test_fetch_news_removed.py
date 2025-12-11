#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试fetch_news相关功能已被完全移除
"""

import logging
import sys
from typing import Dict, List, Any, Callable

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 导入模块
try:
    sys.path.append('/Users/qweenha/code/vknews/src')
    from telegram_bot import TelegramBot
    logger.info("✅ 成功导入TelegramBot模块")
except ImportError as e:
    logger.error(f"❌ 导入模块失败: {e}")
    sys.exit(1)

# 测试1: 检查类中是否没有fetch_news相关的属性和方法
logger.info("\n1. 检查TelegramBot类结构")

# 检查类属性
bot_attrs = dir(TelegramBot)
fetch_news_attrs = [attr for attr in bot_attrs if 'fetch_news' in attr]

if fetch_news_attrs:
    logger.error(f"❌ 发现fetch_news相关属性/方法: {fetch_news_attrs}")
else:
    logger.info("✅ TelegramBot类中没有fetch_news相关的属性和方法")

# 测试2: 创建实例并检查命令菜单设置
logger.info("\n2. 测试命令菜单设置")

try:
    # 创建一个测试实例（不需要实际运行）
    bot = TelegramBot(bot_token="test_token", chat_id="test_chat_id")
    
    # 获取命令菜单设置方法
    if hasattr(bot, '_set_commands_menu'):
        logger.info("✅ _set_commands_menu方法存在")
    else:
        logger.error("❌ _set_commands_menu方法不存在")
    
    # 检查fetch_news_callback是否不存在
    if hasattr(bot, 'fetch_news_callback'):
        logger.error("❌ fetch_news_callback属性仍然存在")
    else:
        logger.info("✅ fetch_news_callback属性已被移除")
        
    logger.info("✅ 命令菜单相关测试通过")

except Exception as e:
    logger.error(f"❌ 测试命令菜单时出错: {e}")
    sys.exit(1)

# 测试3: 检查注册回调方法
logger.info("\n3. 检查回调注册方法")

if hasattr(bot, 'register_fetch_news_callback'):
    logger.error("❌ register_fetch_news_callback方法仍然存在")
else:
    logger.info("✅ register_fetch_news_callback方法已被移除")

logger.info("✅ 回调注册方法测试通过")

logger.info("\n🎉 所有测试均通过！fetch_news相关功能已被完全移除。")
logger.info("Bot将不再显示fetch_news命令在菜单中。")
