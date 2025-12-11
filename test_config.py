#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import logging
import os

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_config_loading():
    """测试配置加载"""
    config_path = "src/config/config.yaml"
    logger.info(f"测试配置文件路径: {config_path}")
    logger.info(f"当前工作目录: {os.getcwd()}")
    logger.info(f"文件是否存在: {os.path.exists(config_path)}")
    
    # 尝试加载示例配置文件
    example_config_path = "src/config/config.yaml.example"
    logger.info(f"示例配置文件路径: {example_config_path}")
    logger.info(f"示例文件是否存在: {os.path.exists(example_config_path)}")
    
    if os.path.exists(example_config_path):
        try:
            with open(example_config_path, "r", encoding="utf-8") as f:
                example_config = yaml.safe_load(f)
            logger.info(f"示例配置加载成功: {example_config}")
            logger.info(f"VK配置: {example_config.get('vk', {})}")
            logger.info(f"社群配置: {example_config.get('vk', {}).get('communities', [])}")
        except Exception as e:
            logger.error(f"加载示例配置失败: {e}")
    
    # 使用模拟配置测试
    mock_config = {
        "vk": {
            "access_token": "mock_token",
            "api_version": "5.131",
            "communities": [
                {
                    "name": "news",
                    "display_name": "новости社群",
                    "source": {"type": "wall", "id": "-123456789"}
                },
                {
                    "name": "tech",
                    "display_name": "科技资讯",
                    "source": {"type": "wall", "id": "techcommunity"}
                }
            ]
        }
    }
    
    logger.info("\n--- 模拟配置测试 ---")
    logger.info(f"模拟配置: {mock_config}")
    communities = mock_config.get("vk", {}).get("communities", [])
    logger.info(f"从模拟配置获取的社群: {communities}")
    logger.info(f"社群数量: {len(communities)}")

if __name__ == "__main__":
    test_config_loading()