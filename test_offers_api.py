import aiohttp
import asyncio
import logging
import os
from typing import List, Dict

class OffersAPITester:
    def __init__(self):
        self.api_key = os.getenv('OFFERS_API_KEY', 'test_key')
        self.base_url = 'https://api.offersapi.net/v1'  # Replace with actual API URL
        self.logging = logging.getLogger(__name__)

    async def fetch_offers(self) -> List[Dict]:
        """Fetch offers from the API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/offers",
                    headers={
                        'X-API-Key': self.api_key,
                        'Content-Type': 'application/json'
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logging.info(f"Successfully fetched {len(data.get('offers', []))} offers")
                        return data.get('offers', [])
                    else:
                        self.logging.error(f"Failed to fetch offers: {response.status}")
                        return []
        except Exception as e:
            self.logging.error(f"Error fetching offers: {e}")
            return []

    async def test_offer_completion(self, offer_id: str) -> bool:
        """Test completing an offer."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/offers/{offer_id}/complete",
                    headers={
                        'X-API-Key': self.api_key,
                        'Content-Type': 'application/json'
                    }
                ) as response:
                    if response.status == 200:
                        self.logging.info(f"Successfully completed offer {offer_id}")
                        return True
                    else:
                        self.logging.error(f"Failed to complete offer: {response.status}")
                        return False
        except Exception as e:
            self.logging.error(f"Error completing offer: {e}")
            return False

    async def verify_completion_status(self, offer_id: str) -> bool:
        """Verify if an offer was completed."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/offers/{offer_id}/status",
                    headers={
                        'X-API-Key': self.api_key,
                        'Content-Type': 'application/json'
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        is_completed = data.get('completed', False)
                        self.logging.info(f"Offer {offer_id} completion status: {is_completed}")
                        return is_completed
                    else:
                        self.logging.error(f"Failed to verify offer status: {response.status}")
                        return False
        except Exception as e:
            self.logging.error(f"Error verifying offer status: {e}")
            return False

async def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    tester = OffersAPITester()
    
    # Test 1: Fetch available offers
    logging.info("\n=== Testing Offer Fetching ===")
    offers = await tester.fetch_offers()
    if offers:
        logging.info("Available offers:")
        for offer in offers:
            logging.info(f"- {offer.get('name')} (ID: {offer.get('id')})")
    
    if not offers:
        logging.error("No offers available to test completion")
        return

    # Test 2: Test offer completion flow
    logging.info("\n=== Testing Offer Completion ===")
    test_offer = offers[0]
    offer_id = test_offer['id']
    
    # Try completing the offer
    completed = await tester.test_offer_completion(offer_id)
    if completed:
        logging.info(f"Successfully completed offer {offer_id}")
    else:
        logging.error(f"Failed to complete offer {offer_id}")
    
    # Verify completion status
    logging.info("\n=== Verifying Completion Status ===")
    status = await tester.verify_completion_status(offer_id)
    if status:
        logging.info(f"Offer {offer_id} verified as completed")
    else:
        logging.info(f"Offer {offer_id} not completed")

if __name__ == "__main__":
    asyncio.run(main())