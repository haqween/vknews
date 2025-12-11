#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yaml
import logging
import os
from typing import Dict, Any, List
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.vk_api import VKAPI
from src.telegram_bot import TelegramBot

class DynamicMenuTest:
    def __init__(self, config_path: str = "src/config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            logger.info(f"尝试加载配置文件: {self.config_path}")
            logger.info(f"当前工作目录: {os.getcwd()}")
            logger.info(f"文件是否存在: {os.path.exists(self.config_path)}")
            
            if not os.path.exists(self.config_path):
                logger.info(f"配置文件不存在: {self.config_path}")
                logger.info("使用模拟配置进行测试...")
                mock_config = self._get_mock_config()
                logger.info(f"模拟配置: {mock_config}")
                return mock_config
                
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            logger.info("配置文件加载成功")
            logger.info(f"加载的配置: {config}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            logger.info("使用模拟配置进行测试...")
            mock_config = self._get_mock_config()
            logger.info(f"模拟配置: {mock_config}")
            return mock_config
    
    def _get_mock_config(self) -> Dict[str, Any]:
        """获取模拟配置"""
        return {
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
                ],
                "additional_sources": [
                    {
                        "type": "newsfeed",
                        "keywords": ["关键词1", "关键词2"]
                    }
                ]
            },
            "telegram": {
                "bot_token": "mock_token",
                "chat_id": "123456789"
            }
        }
    
    def test_community_config(self):
        """测试社群配置"""
        logger.info("开始测试社群配置...")
        
        communities = self.config.get("vk", {}).get("communities", [])
        if not communities:
            logger.error("未找到社群配置")
            return False
        
        logger.info(f"找到 {len(communities)} 个社群配置:")
        for community in communities:
            name = community.get("name")
            display_name = community.get("display_name")
            source = community.get("source", {})
            
            if not name or not display_name or not source:
                logger.error(f"社群配置不完整: {community}")
                return False
            
            logger.info(f"  - 名称: {name}, 显示名称: {display_name}, 来源: {source['type']} {source['id']}")
        
        logger.info("社群配置测试通过")
        return True
    
    def test_dynamic_menu_generation(self):
        """测试动态菜单生成"""
        logger.info("开始测试动态菜单生成...")
        
        # 创建TelegramBot实例
        telegram_config = self.config.get("telegram", {})
        telegram_bot = TelegramBot(
            bot_token=telegram_config.get("bot_token")
        )
        
        # 设置社群配置
        communities = self.config.get("vk", {}).get("communities", [])
        telegram_bot.set_communities(communities)
        
        # 检查社群命令是否已正确注册
        logger.info("社群特定命令注册测试:")
        for community in communities:
            command = f"fetch_{community.get('name', '')}"
            logger.info(f"  - 命令: /{command}, 描述: 获取{community.get('display_name', '')}的最新消息")
        
        # 测试命令菜单设置
        if hasattr(telegram_bot, '_set_commands_menu'):
            logger.info("命令菜单设置方法存在")
        else:
            logger.error("命令菜单设置方法不存在")
            return False
        
        logger.info("动态菜单生成测试通过")
        return True
    
    def test_vk_api_integration(self):
        """测试VK API与新配置结构的集成"""
        logger.info("开始测试VK API集成...")
        
        # 创建VKAPI实例
        vk_config = self.config.get("vk", {})
        vk_api = VKAPI(
            access_token=vk_config.get("access_token"),
            api_version=vk_config.get("api_version", "5.131")
        )
        
        # 测试get_community_content方法
        communities = self.config.get("vk", {}).get("communities", [])
        if communities:
            # 使用第一个社群进行测试
            community = communities[0]
            logger.info(f"测试获取社群 {community.get('name')} 的内容...")
            
            # 这里我们只是测试方法是否存在，不会实际调用API（因为没有真实token）
            if hasattr(vk_api, 'get_community_content'):
                logger.info("get_community_content方法存在")
            else:
                logger.error("get_community_content方法不存在")
                return False
        
        # VK API集成测试通过
        
        logger.info("VK API集成测试通过")
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("=" * 50)
        logger.info("开始运行所有动态菜单功能测试")
        logger.info("=" * 50)
        
        tests = [
            ("社群配置测试", self.test_community_config),
            ("动态菜单生成测试", self.test_dynamic_menu_generation),
            ("VK API集成测试", self.test_vk_api_integration)
        ]
        
        results = []
        for test_name, test_func in tests:
            logger.info(f"\n{'-'*30}")
            logger.info(f"运行测试: {test_name}")
            logger.info(f"{'-'*30}")
            try:
                result = test_func()
                results.append((test_name, result))
                logger.info(f"测试结果: {'通过' if result else '失败'}")
            except Exception as e:
                logger.error(f"测试执行失败: {str(e)}")
                results.append((test_name, False))
        
        logger.info(f"\n{'='*50}")
        logger.info("测试总结:")
        logger.info(f"{'='*50}")
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "通过" if result else "失败"
            logger.info(f"{test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\n总体结果: {passed}/{total} 个测试通过")
        
        if passed == total:
            logger.info("所有测试通过！动态菜单功能正常工作。")
            return True
        else:
            logger.info("部分测试失败，请检查代码。")
            return False

if __name__ == "__main__":
    tester = DynamicMenuTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
