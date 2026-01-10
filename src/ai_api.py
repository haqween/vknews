import logging
import requests
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Base AI Provider Abstract Class
class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self.max_retries = 3
    
    @abstractmethod
    def _call_api(self, messages: List[Dict], max_tokens: int = 200, temperature: float = 0.3) -> str:
        """Call AI API and return the response content"""
        pass
    
    def _execute_with_retry(self, func, *args, **kwargs) -> str:
        """Execute API call with retry mechanism"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                logger.error(f"{self.__class__.__name__} API request failed: {str(e)}")
                
                # Check if it's a 429 Too Many Requests error
                if hasattr(e, 'response') and e.response and e.response.status_code == 429:
                    retry_count += 1
                    if retry_count < self.max_retries:
                        # Calculate exponential backoff with jitter
                        base_delay = 2 ** retry_count  # Exponential backoff
                        jitter = random.uniform(0, 1)  # Add random delay to prevent thundering herd
                        delay = base_delay + jitter
                        logger.info(f"Rate limited, retrying in {delay:.2f} seconds... (Attempt {retry_count}/{self.max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error("Max retries reached, giving up.")
                
                # Log detailed error information
                if hasattr(e, 'response') and e.response:
                    try:
                        error_detail = e.response.json()
                        logger.error(f"API Error Details: {error_detail}")
                    except ValueError:
                        logger.error(f"API Response Content: {e.response.text}")
                break
            except Exception as e:
                logger.error(f"Unexpected error when calling {self.__class__.__name__} API: {str(e)}")
                break
        
        # Return empty string if all retries failed
        return ""


# OpenRouter AI Provider
class OpenRouterAIProvider(BaseAIProvider):
    """OpenRouter AI provider implementation"""
    
    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _call_api(self, messages: List[Dict], max_tokens: int = 200, temperature: float = 0.3) -> str:
        """Call OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build the data dictionary, excluding model field if it's None (for OpenRouter)
        data = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add model field only if it's not None
        if self.model is not None:
            data["model"] = self.model
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"OPENROUTER API full response: {result}")
        return result["choices"][0]["message"]["content"].strip()

# SiliconFlow AI Provider
class SiliconFlowAIProvider(BaseAIProvider):
    """SiliconFlow AI provider implementation"""
    
    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key, model or "deepseek-chat")
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
    
    def _call_api(self, messages: List[Dict], max_tokens: int = 200, temperature: float = 0.3) -> str:
        """Call SiliconFlow API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"SILICONFLOW API full response: {result}")
        return result["choices"][0]["message"]["content"].strip()

# AI Provider Factory
class AIProviderFactory:
    """Factory class to create AI provider instances"""
    
    @staticmethod
    def create_provider(provider_type: str, api_key: str, model: str = None) -> BaseAIProvider:
        """Create and return an AI provider instance based on the provider type"""
        provider_type = provider_type.lower()
        
        if provider_type == "openrouter":
            return OpenRouterAIProvider(api_key, model)
        elif provider_type == "siliconflow":
            return SiliconFlowAIProvider(api_key, model)
        else:
            raise ValueError(f"Unsupported AI provider: {provider_type}")

# AI Processor Class
class AIProcessor:
    """Main AI processor class that uses AI provider instances"""
    
    def __init__(self, api_key: str = None, provider: str = "deepseek", model: str = None, providers: List[Dict] = None):
        """Initialize AIProcessor with multiple providers support
        
        Args:
            api_key: Single API key (for backward compatibility)
            provider: Single provider name (for backward compatibility)
            model: Single model name (for backward compatibility)
            providers: List of provider configurations with name, api_key, and model
        """
        # Validate and filter providers to ensure only configured ones are used
        valid_providers = []
        
        # Support for multiple providers
        if providers and len(providers) > 0:
            for p in providers:
                if p and isinstance(p, dict):
                    # Check if provider has required fields
                    if 'name' in p and 'api_key' in p and p['api_key']:
                        valid_providers.append(p)
                    else:
                        provider_name = p.get('name', 'Unknown')
                        logger.warning(f"Skipping invalid provider {provider_name}: missing name or api_key")
        
        # If no valid providers from the list, use backward compatibility with single provider
        if not valid_providers:
            if api_key:
                valid_providers = [{"name": provider, "api_key": api_key, "model": model}]
                self.use_multiple_providers = False
                logger.info(f"Initialized AIProcessor with single provider: {provider}")
            else:
                raise ValueError("No valid AI providers configured. Please provide at least one provider with api_key.")
        else:
            self.use_multiple_providers = True
            logger.info(f"Initialized AIProcessor with {len(valid_providers)} valid providers: {[p['name'] for p in valid_providers]}")
        
        self.providers = valid_providers
    


