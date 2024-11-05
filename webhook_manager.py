import json
import logging
import os
import requests
from typing import List, Dict
import aiohttp
import asyncio

class WebhookManager:
    def __init__(self, webhook_file: str = 'webhooks.json'):
        self.webhook_file = webhook_file
        self.webhooks = self._load_webhooks()

    def _load_webhooks(self) -> Dict[str, List[str]]:
        """Load webhooks from JSON file."""
        try:
            if os.path.exists(self.webhook_file):
                with open(self.webhook_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading webhooks: {e}")
            return {}

    def _save_webhooks(self) -> None:
        """Save webhooks to JSON file."""
        try:
            with open(self.webhook_file, 'w') as f:
                json.dump(self.webhooks, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving webhooks: {e}")

    def add_webhook(self, feed: str, url: str) -> bool:
        """Add a webhook URL for a specific feed."""
        try:
            if feed not in self.webhooks:
                self.webhooks[feed] = []
            if url not in self.webhooks[feed]:
                self.webhooks[feed].append(url)
                self._save_webhooks()
                return True
            return False
        except Exception as e:
            logging.error(f"Error adding webhook: {e}")
            return False

    def remove_webhook(self, feed: str, url: str) -> bool:
        """Remove a webhook URL for a specific feed."""
        try:
            if feed in self.webhooks and url in self.webhooks[feed]:
                self.webhooks[feed].remove(url)
                self._save_webhooks()
                return True
            return False
        except Exception as e:
            logging.error(f"Error removing webhook: {e}")
            return False

    async def notify_webhook(self, url: str, data: Dict) -> None:
        """Send notification to a single webhook URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        logging.error(f"Webhook notification failed for {url}: {response.status}")
        except Exception as e:
            logging.error(f"Error notifying webhook {url}: {e}")

    async def notify_feed_update(self, feed: str, new_items: List[Dict]) -> None:
        """Notify all webhooks for a specific feed about new items."""
        if feed not in self.webhooks or not self.webhooks[feed]:
            return

        tasks = []
        for url in self.webhooks[feed]:
            for item in new_items:
                data = {
                    'feed': feed,
                    'item': item
                }
                tasks.append(self.notify_webhook(url, data))

        await asyncio.gather(*tasks)

    def get_webhooks(self, feed: str) -> List[str]:
        """Get all webhook URLs for a specific feed."""
        return self.webhooks.get(feed, [])