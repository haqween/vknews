#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to generate and send multiple test messages to Telegram for format evaluation
"""
import sys
import os
import yaml

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.telegram_bot import TelegramBot

def load_config(config_path: str = "src/config/config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            print(f"请复制配置模板: cp src/config/config.yaml.example {config_path}")
            sys.exit(1)
            
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        print("配置文件加载成功")
        return config
        
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        sys.exit(1)

def test_message_format():
    """
    Generate test messages with various content combinations and send them to Telegram
    """
    # Load configuration
    config = load_config()
    
    # Get Telegram configuration
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token")
    chat_id = telegram_config.get("chat_id")
    
    if not bot_token or not chat_id:
        print("Telegram配置不完整，请在config.yaml中设置bot_token和chat_id")
        sys.exit(1)
    
    # Create a real bot instance
    bot = TelegramBot(bot_token, chat_id)
    
    # Generate test content with various combinations
    test_contents = [
        {
            "zh_summary": "这是一条测试内容的中文摘要",
            "ru_summary": "Это тестовый русскоязычный резюме",
            "url": "https://example.com/test1"
        },
        {
            "zh_summary": "这是只有中文摘要的测试内容",
            "ru_summary": "",
            "url": ""
        },
        {
            "zh_summary": "",
            "ru_summary": "Это тестовый русскоязычный резюме без китайского",
            "url": "https://example.com/test2"
        },
        {
            "zh_summary": "这是有中文摘要和URL但没有俄文摘要的测试",
            "ru_summary": "",
            "url": "https://example.com/test3"
        },
        {
            "zh_summary": "这是第五条测试内容的中文摘要，内容较长以便测试换行效果",
            "ru_summary": "Это более длинный тестовый русскоязычный текст, который предназначен для проверки того, как шаблон справляется с длинными предложениями и автоматическим переносом строк",
            "url": "https://example.com/test4"
        },
        {
            "zh_summary": "只有中文摘要的第六条测试内容，测试视觉效果",
            "ru_summary": "",
            "url": ""
        },
        {
            "zh_summary": "",
            "ru_summary": "只有俄文摘要和URL的测试内容",
            "url": "https://example.com/test5"
        }
    ]
    
    print("=== 测试消息格式预览 ===")
    print()
    
    # Send all test contents as a single message
    print(f"\n发送合并的测试消息...")
    
    if test_contents:
        # Send all test contents as a single message without header and footer
        success = bot.send_multiple_processed_content(test_contents)
        
        if success:
            print(f"✅ 合并的测试消息发送成功")
        else:
            print(f"❌ 合并的测试消息发送失败")
    else:
        print("没有测试内容可发送")
    
    print("\n=== 测试完成 ===")
    print("所有测试消息已发送到Telegram")
    print("请检查您的Telegram聊天以查看实际效果。")
    
    return True

if __name__ == "__main__":
    test_message_format()
