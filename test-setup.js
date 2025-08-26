const config = require('./src/config/settings');
const logger = require('./src/utils/logger');

async function runSystemTests() {
  logger.info('Starting system tests...');
  
  // Test 1: Configuration validation
  console.log('1. Testing configuration...');
  if (!config.ouo.apiToken) {
    throw new Error('OUO_API_TOKEN not configured');
  }
  if (!config.discord.webhookUrl) {
    throw new Error('DISCORD_WEBHOOK_URL not configured');
  }
  
  // Test 2: RSS feed discovery
  console.log('2. Testing RSS feed discovery...');
  const rssProcessor = require('./src/services/rssProcessor');
  const feeds = await rssProcessor.getAllFeeds();
  console.log(`Found ${feeds.length} RSS feeds`);
  
  // Test 3: Link monetization
  console.log('3. Testing link monetization...');
  const linkMonetizer = require('./src/services/linkMonetizer');
  const testUrl = 'https://example.com';
  const monetized = await linkMonetizer.monetizeUrl(testUrl);
  console.log(`Test monetization: ${testUrl} -> ${monetized}`);
  
  // Test 4: Cache functionality
  console.log('4. Testing cache functionality...');
  const cacheManager = require('./src/services/cacheManager');
  const cacheStats = cacheManager.getStats();
  console.log('Cache stats:', cacheStats);
  
  logger.info('All system tests completed successfully');
}

runSystemTests().catch(console.error);