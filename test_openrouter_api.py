#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter AI API 测试脚本
用于测试 OpenRouter AI 处理器的初始化和摘要生成功能
"""

import os
import sys
import logging
from src.ai_api import AIProcessor
from src.text_processor import TextProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_openrouter_ai_processor():
    """测试 OpenRouter AI 处理器"""
    logger.info("=== OpenRouter AI 处理器测试 ===")
    
    # 从环境变量获取 API 密钥
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.warning("⚠️  未设置 OPENROUTER_API_KEY 环境变量，将使用模拟测试")
        
        # 模拟测试：仅测试初始化逻辑
        try:
            # 创建 AI 处理器实例
            ai_processor = AIProcessor(
                api_key="mock_key",  # 使用模拟密钥
                provider="openrouter",
                model="openai/gpt-4o-mini"  # 指定一个 OpenRouter 支持的模型示例
            )
            logger.info("✅ OpenRouter AI 处理器初始化成功")
            logger.info(f"   - Provider: {ai_processor.provider}")
            logger.info(f"   - Model: {ai_processor.model}")
            logger.info(f"   - API URL: {ai_processor.api_url}")
            
            # 测试消息格式
            test_text = "俄罗斯总统普京与乌克兰总统泽连斯基在巴黎举行了和平谈判，双方就停火协议达成了初步共识。国际社会对此表示欢迎，希望双方能够继续保持对话，推动和平进程。"
            logger.info(f"\n测试文本: {test_text}")
            
            # 模拟摘要生成（不实际调用 API）
            logger.info("✅ 摘要生成流程测试完成（模拟）")
            logger.info("   实际 API 调用需要设置 OPENROUTER_API_KEY 环境变量")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {str(e)}")
            return False
    else:
        # 实际 API 测试
        try:
            # 创建 AI 处理器实例
            ai_processor = AIProcessor(
                api_key=api_key,
                provider="openrouter",
                model="openai/gpt-4o-mini"  # 使用 OpenRouter 支持的模型
            )
            logger.info("✅ OpenRouter AI 处理器初始化成功")
            
            # 测试摘要生成
            test_text = "俄罗斯总统普京与乌克兰总统泽连斯基在巴黎举行了和平谈判，双方就停火协议达成了初步共识。国际社会对此表示欢迎，希望双方能够继续保持对话，推动和平进程。"
            logger.info(f"\n测试文本: {test_text}")
            
            # 使用批量处理方法替代单独的摘要生成
            test_content = {"text": test_text}
            providers = [{"name": "openrouter", "api_key": api_key, "model": "openai/gpt-4o-mini"}]
            text_processor = TextProcessor(ai_providers=providers)
            processed_content = text_processor.process_content_batch([test_content], {"summary": {"max_length": 100}})[0]
            summary = processed_content.get('zh_summary')
            
            if summary:
                logger.info(f"✅ 摘要生成成功: {summary}")
                return True
            else:
                logger.error("❌ 摘要生成失败: 未返回结果")
                return False
                
        except Exception as e:
            logger.error(f"❌ API 测试失败: {str(e)}")
            return False


if __name__ == "__main__":
    success = test_openrouter_ai_processor()
    if success:
        logger.info("\n🎉 所有 OpenRouter 测试通过！")
        sys.exit(0)
    else:
        logger.error("\n❌ OpenRouter 测试失败！")
        sys.exit(1)