import logging
import yaml
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.telegram_bot import TelegramBot

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_telegram_bot():
    # 加载配置文件
    config_path = 'src/config/config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    telegram_config = config.get('telegram', {})
    bot_token = telegram_config.get('bot_token')
    chat_id = telegram_config.get('chat_id')
    
    if not bot_token or not chat_id:
        logger.error("Telegram配置不完整，请检查config.yaml文件")
        return False
    
    try:
        # 创建TelegramBot实例
        bot = TelegramBot(bot_token=bot_token, chat_id=chat_id)
        
        # 准备测试数据
        test_content = {
            'title': '测试消息标题',
            'ru_summary': '这是一个俄语摘要测试。这个功能现在可以正常工作了。',
            'zh_summary': '这是一个中文摘要测试。这个功能现在可以正常工作了。',
            'url': 'https://example.com/test'
        }
        
        logger.info("开始测试Telegram消息发送...")
        # 发送测试消息
        success = bot.send_multiple_processed_content([test_content])
        
        if success:
            logger.info("测试成功！消息已发送到Telegram")
            return True
        else:
            logger.error("测试失败！消息发送失败")
            return False
    
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    test_telegram_bot()
