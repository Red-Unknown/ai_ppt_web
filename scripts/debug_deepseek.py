import os
import time
import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI, APIError, APITimeoutError, RateLimitError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat" # V3 is deepseek-chat

# Scenario Configuration
SCENARIO_CONFIG = {
    "chat": {
        "max_tokens": 2048,
        "temperature": 0.7,
        "system_prompt": "You are a helpful assistant."
    },
    "summary": {
        "max_tokens": 4096,
        "temperature": 0.3,
        "system_prompt": "You are a professional summarizer. Please summarize the content concisely."
    },
    "translation": {
        "max_tokens": 4096,
        "temperature": 0.1,
        "system_prompt": "You are a professional translator. Translate the following text accurately."
    }
}

class DeepSeekClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set.")
        self.client = OpenAI(api_key=api_key, base_url=BASE_URL)

    def generate(self, prompt: str, scenario: str = "chat", retries: int = 3) -> Optional[str]:
        """
        Generate text using DeepSeek API with retry mechanism.
        """
        config = SCENARIO_CONFIG.get(scenario, SCENARIO_CONFIG["chat"])
        messages = [
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": prompt}
        ]
        
        logger.info(f"Generating for scenario '{scenario}' with config: {config}")

        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    max_tokens=config["max_tokens"],
                    temperature=config["temperature"],
                    stream=False
                )
                return response.choices[0].message.content
            except (RateLimitError, APITimeoutError) as e:
                wait_time = 2 ** attempt # Exponential backoff
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            except APIError as e:
                logger.error(f"DeepSeek API Error: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                break
        
        return None

if __name__ == "__main__":
    # Ensure API Key is set for testing
    if not API_KEY:
        print("Please set DEEPSEEK_API_KEY environment variable.")
        # For demonstration, you can uncomment below line if you have a key, 
        # but better to pass via env var
        # os.environ["DEEPSEEK_API_KEY"] = "sk-..." 
        # API_KEY = os.environ.get("DEEPSEEK_API_KEY")
    
    try:
        # Example Usage
        # NOTE: You need to set DEEPSEEK_API_KEY in your environment before running this script
        # e.g., export DEEPSEEK_API_KEY="sk-..."
        
        if API_KEY:
            client = DeepSeekClient(API_KEY)
            
            # 1. Chat Scenario
            print("\n--- Testing Chat Scenario ---")
            response = client.generate("Hello, who are you?", scenario="chat")
            print(f"Response: {response}\n")

            # 2. Summary Scenario
            print("\n--- Testing Summary Scenario ---")
            text_to_summarize = "DeepSeek-V3 is a powerful mixture-of-experts language model..."
            response = client.generate(f"Summarize this: {text_to_summarize}", scenario="summary")
            print(f"Response: {response}\n")
        else:
             print("Skipping execution because DEEPSEEK_API_KEY is missing.")

    except ValueError as e:
        print(f"Initialization Error: {e}")
