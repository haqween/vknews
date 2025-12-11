#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter API 配置测试脚本
直接从配置文件读取设置并测试 API 调用
"""

import os
import yaml
import logging
import requests
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), 'src', 'config', 'config.yaml')
    logger.info(f"加载配置文件: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def test_openrouter_api(config: Dict[str, Any]):
    """测试 OpenRouter API 调用"""
    logger.info("=== OpenRouter API 配置测试 ===")
    
    # 获取 AI 配置
    ai_config = config.get('ai', {})
    provider = ai_config.get('provider', '')
    api_key = ai_config.get('api_key', '')
    model = ai_config.get('model', '')
    
    logger.info(f"AI 配置信息:")
    logger.info(f"  - Provider: {provider}")
    logger.info(f"  - Model: {model}")
    logger.info(f"  - API Key: {api_key[:10]}...{api_key[-10:]}" if api_key else "  - API Key: 未设置")
    
    if provider != 'openrouter':
        logger.error(f"❌ 配置错误: provider 不是 openrouter，当前为: {provider}")
        return False
    
    if not api_key:
        logger.error("❌ 配置错误: API Key 未设置")
        return False
    
    # 构建 API 请求
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    logger.info(f"API URL: {api_url}")
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建请求数据
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请用中文总结：俄罗斯总统普京与乌克兰总统泽连斯基在巴黎举行了和平谈判，双方就停火协议达成了初步共识。国际社会对此表示欢迎，希望双方能够继续保持对话，推动和平进程。"}
    ]
    
    data = {
        "messages": messages,
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    # 添加模型字段（如果有）
    if model:
        data["model"] = model
    
    logger.info(f"请求数据: {data}")
    
    try:
        logger.info("发送 API 请求...")
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"].strip()
                logger.info(f"✅ API 调用成功！")
                logger.info(f"   响应内容: {content}")
                return True
            else:
                logger.error(f"❌ API 响应格式错误")
                return False
        else:
            logger.error(f"❌ API 请求失败，状态码: {response.status_code}")
            try:
                error_detail = response.json()
                logger.error(f"   错误详情: {error_detail}")
            except ValueError:
                logger.error(f"   错误内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"❌ API 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ API 连接错误")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API 请求异常: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ 未知错误: {str(e)}")
        return False


if __name__ == "__main__":
    try:
        config = load_config()
        success = test_openrouter_api(config)
        
        if success:
            logger.info("\n🎉 OpenRouter API 测试通过！")
            exit(0)
        else:
            logger.error("\n❌ OpenRouter API 测试失败！")
            exit(1)
            
    except Exception as e:
        logger.error(f"❌ 测试脚本执行失败: {str(e)}")
        exit(1)