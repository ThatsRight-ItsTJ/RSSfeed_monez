import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class UnlockContentAPI:
    def __init__(self):
        self.base_url = "https://unlockcontent.net/api/v2"
        self.api_key = os.getenv('UNLOCK_CONTENT_API_KEY')
        if not self.api_key:
            raise ValueError("UNLOCK_CONTENT_API_KEY environment variable not set")
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        return {
            'Authorization': f'Bearer {self.api_key}'
        }

    async def get_offers(self, ip: str, user_agent: str, ctype: Optional[int] = None) -> Optional[List[Dict]]:
        """Fetch available offers."""
        try:
            # Build query parameters according to API docs
            params = {
                'ip': ip,
                'user_agent': user_agent
            }
            
            # Only add ctype if specified
            if ctype is not None:
                params['ctype'] = ctype

            self.logger.info(f"Fetching offers with params: {params}")
            self.logger.info(f"Using Authorization: Bearer {self.api_key[:5]}...")  # Log partial key for debugging
            
            async with self.session.get(
                self.base_url,
                headers=self.get_headers(),
                params=params,
                timeout=30
            ) as response:
                self.logger.info(f"API Response Status: {response.status}")
                response_text = await response.text()
                self.logger.info(f"API Response: {response_text[:200]}...")  # Log first 200 chars
                
                if response.status == 200:
                    data = json.loads(response_text)
                    if data.get('success'):
                        offers = data.get('offers', [])
                        self.logger.info(f"Successfully fetched {len(offers)} offers")
                        return offers
                    else:
                        self.logger.error(f"API Error: {data.get('error')}")
                        return None
                elif response.status == 401 or response.status == 403:
                    self.logger.error("Authentication failed - invalid API key")
                    return None
                
                self.logger.error(f"Failed to fetch offers: {response.status}, Response: {response_text}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching offers: {str(e)}")
            return None

async def get_public_ip() -> str:
    """Get a public IP address for testing."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.ipify.org') as response:
                return await response.text()
    except Exception as e:
        logging.error(f"Error getting public IP: {e}")
        return "8.8.8.8"  # Fallback to Google DNS IP

async def test_api_integration():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Get a real public IP for testing
    test_ip = await get_public_ip()
    test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    logger.info(f"Testing with IP: {test_ip}")
    logger.info("=== Testing API Connection ===")
    
    try:
        async with UnlockContentAPI() as api:
            # Test: Fetch Offers
            logger.info("\n=== Testing Offer Fetching ===")
            
            # Test with all offer types first
            logger.info("\nFetching all offer types...")
            all_offers = await api.get_offers(test_ip, test_user_agent)
            
            if all_offers:
                logger.info(f"Successfully fetched {len(all_offers)} offers")
                for i, offer in enumerate(all_offers[:3], 1):  # Show first 3 offers
                    logger.info(f"\nOffer {i}:")
                    logger.info(json.dumps(offer, indent=2))
            
            # Test with CPI offers only
            logger.info("\nFetching CPI offers only...")
            cpi_offers = await api.get_offers(test_ip, test_user_agent, ctype=1)
            
            if cpi_offers:
                logger.info(f"Successfully fetched {len(cpi_offers)} CPI offers")
                for i, offer in enumerate(cpi_offers[:3], 1):  # Show first 3 offers
                    logger.info(f"\nCPI Offer {i}:")
                    logger.info(json.dumps(offer, indent=2))
    except ValueError as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_api_integration())