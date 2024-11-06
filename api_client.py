import aiohttp
import logging
import asyncio
from typing import Optional
import json

class AdCopyGenerator:
    BASE_URL = "https://api.airforce/chat/completions"
    RATE_LIMIT = 10  # requests per minute
    RATE_PERIOD = 60  # seconds
    
    def __init__(self):
        self.request_times = []
        
    async def _check_rate_limit(self):
        """Enforce rate limiting."""
        current_time = asyncio.get_event_loop().time()
        # Remove timestamps older than rate period
        self.request_times = [t for t in self.request_times 
                            if current_time - t < self.RATE_PERIOD]
        
        if len(self.request_times) >= self.RATE_LIMIT:
            oldest_request = min(self.request_times)
            sleep_time = self.RATE_PERIOD - (current_time - oldest_request)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(current_time)

    async def generate_ad_copy(self, prompt: str) -> Optional[str]:
        """Generate ad copy using the API."""
        try:
            await self._check_rate_limit()
            
            payload = {
                'model': 'claude-3-opus',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an advertising copywriter. Create compelling, concise ad copy.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 2048,
                'temperature': 0.7
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.BASE_URL, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        logging.error(f"API request failed with status {response.status}")
                        return None

        except Exception as e:
            logging.error(f"Error generating ad copy: {e}")
            return None