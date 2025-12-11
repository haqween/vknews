import logging
import yaml
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.vk_api import VKAPI
from src.telegram_bot import TelegramBot

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_integration(community_name="rt_russian", message_count=2):
    """
    联合测试：从VK社群获取消息并发送到Telegram
    
    Args:
        community_name: 要测试的VK社群名
        message_count: 要获取和发送的消息数量
        
    Returns:
        bool: 测试是否成功
    """
    logger.info("开始VK-Telegram联合测试...")
    
    try:
        # 1. 加载配置文件
        config_path = 'src/config/config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        vk_config = config.get('vk', {})
        tg_config = config.get('telegram', {})
        
        # 验证配置完整性
        required_vk = ['access_token']
        required_tg = ['bot_token', 'chat_id']
        
        for key in required_vk:
            if not vk_config.get(key):
                logger.error(f"VK配置不完整，缺少: {key}")
                return False
        
        for key in required_tg:
            if not tg_config.get(key):
                logger.error(f"Telegram配置不完整，缺少: {key}")
                return False
        
        # 2. 创建VKAPI实例
        logger.info("\n创建VKAPI实例...")
        vk_api = VKAPI(access_token=vk_config.get('access_token'), api_version="5.131")
        
        # 3. 获取rt_russian社群内容
        logger.info(f"\n从{community_name}获取最新{message_count}条消息...")
        wall_posts = vk_api.get_wall_content(community_name, count=message_count)
        
        if not wall_posts:
            logger.error(f"未从{community_name}获取到任何消息")
            return False
        
        logger.info(f"成功获取到 {len(wall_posts)} 条消息")
        
        # 4. 创建TelegramBot实例
        logger.info("\n创建TelegramBot实例...")
        telegram_bot = TelegramBot(tg_config.get('bot_token'), tg_config.get('chat_id'))
        
        # 5. 发送消息到Telegram
        logger.info("\n开始发送消息到Telegram...")
        
        for i, post in enumerate(wall_posts[:message_count], 1):
            # 格式化消息
            formatted_post = vk_api.format_content(post)
            
            # 准备发送的内容
            message_parts = []
            message_parts.append(f"📱 来自 {community_name} 的消息 #{i}")
            message_parts.append(f"\n🔗 链接: {formatted_post.get('url')}")
            message_parts.append(f"\n📅 发布时间: {formatted_post.get('date')}")
            message_parts.append(f"\n📝 内容:")
            message_parts.append(f"{formatted_post.get('text')[:400]}...")  # 限制消息长度
            
            full_message = "\n".join(message_parts)
            
            logger.info(f"\n发送第{i}条消息:")
            logger.info(f"消息预览: {full_message[:100]}...")
            
            try:
                success = telegram_bot.send_message(full_message)
                if success:
                    logger.info(f"✅ 第{i}条消息发送成功")
                else:
                    logger.error(f"❌ 第{i}条消息发送失败")
                    return False
            except Exception as e:
                logger.error(f"❌ 发送第{i}条消息时发生错误: {str(e)}")
                return False
        
        logger.info("\n✅ 所有消息发送完成")
        
        # 6. 测试发送带有摘要的消息（如果AI配置可用）
        if config.get('ai', {}).get('openai_api_key'):
            logger.info("\n=== 测试AI摘要功能 ===")
            
            try:
                from src.ai_api import AIProcessor
                from src.text_processor import TextProcessor
                
                logger.info("创建AIProcessor实例...")
                ai_processor = AIProcessor(config.get('ai'))
                
                # 创建TextProcessor实例
                ai_config = config.get('ai', {})
                providers = ai_config.get('providers', [])
                text_processor = TextProcessor(ai_providers=providers)
                
                # 获取一条消息并生成摘要
                if wall_posts:
                    sample_post = wall_posts[0]
                    formatted_post = vk_api.format_content(sample_post)
                    
                    logger.info("生成消息摘要...")
                    # 使用批量处理方法替代单独的摘要生成
                    processed_content = text_processor.process_content_batch([formatted_post], config.get('ai', {}))[0]
                    summary = processed_content.get('zh_summary')
                    
                    if summary:
                        logger.info(f"✅ 生成摘要成功: {summary[:100]}...")
                        
                        # 发送带摘要的消息
                        summary_message = [
                            "🤖 AI摘要测试",
                            f"\n🔗 原文链接: {formatted_post.get('url')}",
                            f"\n📅 发布时间: {formatted_post.get('date')}",
                            f"\n📝 原始内容预览: {formatted_post.get('text')[:100]}...",
                            f"\n🤖 AI摘要:",
                            f"{summary}"
                        ]
                        
                        success = telegram_bot.send_message("\n".join(summary_message))
                        if success:
                            logger.info("✅ 带摘要的消息发送成功")
                        else:
                            logger.warning("⚠️ 带摘要的消息发送失败")
            except Exception as e:
                logger.warning(f"⚠️ AI摘要功能测试失败: {str(e)}")
        
        logger.info("\n🎉 联合测试完成！")
        logger.info(f"\n📊 测试统计:")
        logger.info(f"   - 从 {community_name} 获取消息: {len(wall_posts)} 条")
        logger.info(f"   - 发送到Telegram: {message_count} 条")
        logger.info(f"   - 测试状态: 成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 联合测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_integration(community_name="rt_russian", message_count=2)
