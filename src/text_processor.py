import logging
import random
from typing import List, Dict, Any, Optional

# Import AI processor modules
from src.ai_api import AIProviderFactory

# Configure logging
logger = logging.getLogger(__name__)

class TextProcessor:
    """Text processing utility class for translation and other text operations"""
    
    def __init__(self, ai_providers: Optional[List[Dict[str, Any]]] = None):
        """Initialize TextProcessor with AI providers
        
        Args:
            ai_providers: List of AI provider configurations
        """
        self.ai_providers = ai_providers or []
    
    def set_ai_providers(self, ai_providers: List[Dict[str, Any]]):
        """Set AI providers for translation
        
        Args:
            ai_providers: List of AI provider configurations
        """
        self.ai_providers = ai_providers
    
    def generate_summaries_batch(self, texts: List[str], max_length: int = 30, language: str = "zh") -> List[str]:
        """Generate summaries for multiple texts in a single API call to reduce QPS usage"""
        if not texts:
            return []
            
        if not self.ai_providers:
            logger.error("No AI providers configured for summary generation")
            return ["" for _ in texts]
            
        try:
            # Randomly select a provider
            selected_provider = random.choice(self.ai_providers)
            provider_name = selected_provider["name"]
            api_key = selected_provider["api_key"]
            model = selected_provider["model"]
            logger.info(f"generate summary using model: {provider_name} {model}")
            # Create provider instance on the fly
            provider_instance = AIProviderFactory.create_provider(provider_name, api_key, model)
            
            # Prepare the batch prompt
            batch_prompt = "请为以下每个文本分别生成中文摘要，限制在{max_length}字符以内，保留核心信息。\n\n"
            for i, text in enumerate(texts):
                batch_prompt += f"--- 文本 {i+1} ---\n"
                batch_prompt += f"{text}\n\n"
            
            batch_prompt += "--- 要求 ---\n"
            batch_prompt += f"1. 请严格按照文本顺序，为每个文本生成一个摘要\n"
            batch_prompt += f"2. 每个摘要限制在{max_length}字符以内\n"
            batch_prompt += "3. 输出格式：每行一个摘要，按顺序排列\n"
            batch_prompt += "4. Answer only with the final result, no explanations."
            
            messages = [
                {"role": "system", "content": "You are a professional text summarization assistant. You will receive multiple texts and must generate a summary for each one."},
                {"role": "user", "content": batch_prompt.format(max_length=max_length)}
            ]
            
            # Calculate appropriate max_tokens based on number of texts
            batch_max_tokens = max_length * len(texts) + 100  # Add buffer
            
            response = provider_instance._execute_with_retry(provider_instance._call_api, messages, max_tokens=batch_max_tokens, temperature=0.3)
            
            if not response:
                logger.error("Batch summarization failed, returning empty summaries")
                return ["" for _ in texts]
            
            # Parse the response
            summaries = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if line:
                    summaries.append(line)
            
            # Ensure we have the same number of summaries as texts
            # If not, fill missing summaries with empty strings
            while len(summaries) < len(texts):
                summaries.append("")
            
            # Truncate to match the number of texts if we got more
            summaries = summaries[:len(texts)]
            
            logger.info(f"Successfully generated {len(summaries)} summaries in batch using {provider_name}")
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to generate batch summaries: {str(e)}")
            return ["" for _ in texts]
    
    def process_content_batch(self, contents: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process multiple contents in batch to reduce API calls"""
        if not contents:
            return []
            
        # Separate valid contents from invalid ones
        valid_contents = []
        valid_indices = []
        
        for i, content in enumerate(contents):
            if content and "text" in content:
                valid_contents.append(content)
                valid_indices.append(i)
        
        if not valid_contents:
            return contents
        
        # Extract texts for batch processing
        texts = [content["text"] for content in valid_contents]
        
        # Get summary configuration
        summary_config = config.get("summary", {})
        # 中文摘要最长30个文字，俄语支持60个
        zh_max_length = summary_config.get("zh_max_length", 30)
        ru_max_length = summary_config.get("ru_max_length", 60)
        
        # Generate summaries in batch
        zh_summaries = self.generate_summaries_batch(texts, max_length=zh_max_length, language="zh")
        
        # Create result list with the same order as input
        results = contents.copy()
        
        # Process valid contents
        for i, (content, zh_summary) in enumerate(zip(valid_contents, zh_summaries)):
            original_text = content["text"]
            
            # Directly truncate original text for Russian summary (no AI generation)
            ru_summary = original_text[:ru_max_length] + "..." if len(original_text) > ru_max_length else original_text
            
            # Update the content in the results list
            results[valid_indices[i]] = {
                **content,
                "ru_summary": ru_summary,
                "zh_summary": zh_summary
            }
        
        return results
    
    async def translate_to_russian(self, text: str) -> str:
        """Translate text to Russian using AI processor
        
        Args:
            text: Text to translate
            
        Returns:
            Translated text in Russian
        """
        if not self.ai_providers:
            logger.error("No AI providers configured for translation")
            return ""
        
        try:
            # Randomly select an AI provider
            selected_provider = random.choice(self.ai_providers)
            provider_name = selected_provider["name"]
            api_key = selected_provider["api_key"]
            model = selected_provider["model"]
            
            # Create provider instance
            provider_instance = AIProviderFactory.create_provider(provider_name, api_key, model)
            
            # Prepare translation request
            messages = [
                {"role": "system", "content": "你是一个专业的翻译助手，请将用户输入的内容准确翻译成俄语，只返回翻译结果，不要添加任何额外说明。"},
                {"role": "user", "content": text}
            ]
            
            # Call API for translation
            translated_text = provider_instance._execute_with_retry(
                provider_instance._call_api, 
                messages, 
                max_tokens=50, 
                temperature=0.1
            )
            
            return translated_text.strip() if translated_text else ""
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return ""
    
    def is_activity(self, text: str) -> bool:
        """Check if the given text is an activity/event announcement
        
        Args:
            text: The text to check
            
        Returns:
            True if the text is an activity, False otherwise
        """
        if not self.ai_providers:
            logger.error("No AI providers configured for activity detection")
            return False
            
        try:
            # Randomly select a provider
            selected_provider = random.choice(self.ai_providers)
            provider_name = selected_provider["name"]
            api_key = selected_provider["api_key"]
            model = selected_provider["model"]
            
            # Create provider instance on the fly
            provider_instance = AIProviderFactory.create_provider(provider_name, api_key, model)
            
            # Prepare the prompt for activity detection
            messages = [
                {"role": "system", "content": "You are a professional content classifier. Please determine if the given text is an announcement for an activity or event. Return only 'YES' if it is an activity, otherwise return 'NO'. Do not provide any explanations."},
                {"role": "user", "content": text}
            ]
            
            # Call the AI API
            response = provider_instance._execute_with_retry(provider_instance._call_api, messages, max_tokens=10, temperature=0.1)
            
            if not response:
                logger.error("Activity detection failed, returning False")
                return False
            
            # Check the response
            return response.strip().upper() == "YES"
            
        except Exception as e:
            logger.error(f"Failed to detect activity: {str(e)}")
            return False
