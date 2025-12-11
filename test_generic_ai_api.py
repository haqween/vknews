import os
import logging
from dotenv import load_dotenv
from src.ai_api import AIProcessor
from src.text_processor import TextProcessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

def test_deepseek_api():
    """测试DeepSeek API功能"""
    logger.info("\n=== 测试 DeepSeek API ===")
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("未设置 DEEPSEEK_API_KEY 环境变量，跳过DeepSeek API测试")
            return False
        
        ai_processor = AIProcessor(api_key=api_key, provider="deepseek", model="deepseek-chat")
        providers = [{"name": "deepseek", "api_key": api_key, "model": "deepseek-chat"}]
        
        # 测试摘要生成
        test_text = "俄罗斯政府计划在2035年前将可再生能源在总能源结构中的占比提高到30%，以减少对传统化石燃料的依赖并降低碳排放。"
        test_content = {"text": test_text}
        text_processor = TextProcessor(ai_providers=providers)
        processed_content = text_processor.process_content_batch([test_content], {"summary": {"max_length": 100}})[0]
        summary = processed_content.get('zh_summary')
        logger.info(f"中文摘要: {summary}")
        
        # 测试翻译
        translation = ai_processor.translate_text("Hello, this is a test message.", target_language="zh")
        logger.info(f"英文到中文翻译: {translation}")
        
        logger.info("DeepSeek API 测试完成！")
        return True
    except Exception as e:
        logger.error(f"DeepSeek API 测试失败: {str(e)}")
        return False

def test_openai_api():
    """测试OpenAI API功能"""
    logger.info("\n=== 测试 OpenAI API ===")
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("未设置 OPENAI_API_KEY 环境变量，跳过OpenAI API测试")
            return False
        
        ai_processor = AIProcessor(api_key=api_key, provider="openai", model="gpt-3.5-turbo")
        providers = [{"name": "openai", "api_key": api_key, "model": "gpt-3.5-turbo"}]
        
        # 测试摘要生成
        test_text = "俄罗斯政府计划在2035年前将可再生能源在总能源结构中的占比提高到30%，以减少对传统化石燃料的依赖并降低碳排放。"
        test_content = {"text": test_text}
        text_processor = TextProcessor(ai_providers=providers)
        processed_content = text_processor.process_content_batch([test_content], {"summary": {"max_length": 100}})[0]
        summary = processed_content.get('zh_summary')
        logger.info(f"中文摘要: {summary}")
        
        # 测试翻译
        translation = ai_processor.translate_text("Hello, this is a test message.", target_language="zh")
        logger.info(f"英文到中文翻译: {translation}")
        
        logger.info("OpenAI API 测试完成！")
        return True
    except Exception as e:
        logger.error(f"OpenAI API 测试失败: {str(e)}")
        return False

class MockAIProcessor:
    """模拟AI处理器，用于演示多提供商支持"""
    def __init__(self, provider="deepseek"):
        self.provider = provider
    
    def generate_summary(self, text, max_length=100, language="zh"):
        return f"[{self.provider.upper()}] 摘要: {text[:max_length]}..."
    
    def translate_text(self, text, target_language="zh"):
        return f"[{self.provider.upper()}] 翻译: {text} (to {target_language})"

def test_mock_api():
    """使用模拟数据测试多提供商支持"""
    logger.info("\n=== 模拟测试多提供商支持 ===")
    
    # 测试模拟的DeepSeek API
    deepseek_mock = MockAIProcessor(provider="deepseek")
    logger.info(f"DeepSeek 模拟摘要: {deepseek_mock.generate_summary('测试文本', max_length=50)}")
    logger.info(f"DeepSeek 模拟翻译: {deepseek_mock.translate_text('Hello', target_language='zh')}")
    
    # 测试模拟的OpenAI API
    openai_mock = MockAIProcessor(provider="openai")
    logger.info(f"OpenAI 模拟摘要: {openai_mock.generate_summary('测试文本', max_length=50)}")
    logger.info(f"OpenAI 模拟翻译: {openai_mock.translate_text('Hello', target_language='zh')}")
    
    logger.info("模拟多提供商测试完成！")
    return True

if __name__ == "__main__":
    logger.info("启动通用AI接口测试...")
    
    # 运行模拟测试
    test_mock_api()
    
    # 运行实际API测试
    test_deepseek_api()
    test_openai_api()
    
    logger.info("\n=== 所有测试完成！ ===")
    logger.info("请在实际使用时设置对应的环境变量:")
    logger.info("- DEEPSEEK_API_KEY: DeepSeek API密钥")
    logger.info("- OPENAI_API_KEY: OpenAI API密钥")
    logger.info("然后在配置文件中设置 provider 为 'deepseek' 或 'openai' 即可切换AI提供商。")