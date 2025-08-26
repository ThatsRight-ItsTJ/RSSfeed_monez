const express = require('express');
const helmet = require('helmet');
const cron = require('node-cron');
const config = require('./config/settings');
const logger = require('./utils/logger');
const rssProcessor = require('./services/rssProcessor');
const discordWebhook = require('./services/discordWebhook');
const cacheManager = require('./services/cacheManager');
const advancedFeedGenerator = require('./services/advancedFeedGenerator');
const databaseManager = require('./services/databaseManager');

class RSSMonetizationServer {
  constructor() {
    this.app = express();
    this.setupMiddleware();
    this.setupRoutes();
    this.setupScheduler();
  }

  setupMiddleware() {
    this.app.use(helmet());
    this.app.use(express.json());
    this.app.use(express.static('public'));
  }

  setupRoutes() {
    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
      });
    });

    // Manual trigger endpoint
    this.app.post('/trigger-processing', async (req, res) => {
      try {
        logger.info('Manual processing triggered');
        const results = await this.processFeeds();
        res.json({
          success: true,
          results,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        logger.error('Manual processing failed', { error: error.message });
        res.status(500).json({
          success: false,
          error: error.message
        });
      }
    });

    // Statistics endpoint
    this.app.get('/stats', async (req, res) => {
      try {
        const stats = await this.getSystemStats();
        res.json(stats);
      } catch (error) {
        logger.error('Error getting stats', { error: error.message });
        res.status(500).json({ error: 'Failed to get stats' });
      }
    });

    // Cache management endpoints
    this.app.post('/cache/cleanup', (req, res) => {
      cacheManager.cleanup();
      res.json({ success: true, message: 'Cache cleanup completed' });
    });

    this.app.get('/cache/stats', (req, res) => {
      res.json(cacheManager.getStats());
    });

    // Database endpoints
    this.app.get('/database/stats', async (req, res) => {
      try {
        const stats = await databaseManager.getFeedItems();
        const byType = {};
        stats.forEach(item => {
          byType[item.feed_type] = (byType[item.feed_type] || 0) + 1;
        });
        
        res.json({
          totalItems: stats.length,
          itemsByType: byType,
          lastUpdated: stats[0]?.created_at || null
        });
      } catch (error) {
        res.status(500).json({ error: 'Failed to get database stats' });
      }
    });

    // Item lookup by hash
    this.app.get('/item/:hash', async (req, res) => {
      try {
        const item = await databaseManager.getItemByHash(req.params.hash);
        if (item) {
          // Redirect to original link
          res.redirect(item.link);
        } else {
          res.status(404).json({ error: 'Item not found' });
        }
      } catch (error) {
        res.status(500).json({ error: 'Failed to lookup item' });
      }
    });

    // Feed management endpoints
    this.app.get('/api/feeds', async (req, res) => {
      try {
        const feedSources = require('./config/feed-sources');
        // Return configured feeds from your feed-sources.js or database
        const feeds = Object.values(feedSources).flat().map(feed => ({
          id: feed.id,
          name: feed.name,
          rss_url: feed.rss_url,
          feed_type: feed.feed_type,
          discord_webhook: feed.discord_webhook || null,
          updated_at: new Date().toISOString()
        }));
        
        res.json(feeds);
      } catch (error) {
        res.status(500).json({ error: 'Failed to get feeds' });
      }
    });

    this.app.post('/api/feeds', async (req, res) => {
      try {
        const { name, rss_url, discord_webhook, feed_type } = req.body;
        
        // Save to database or update configuration
        // This depends on how you want to store dynamic feeds
        
        res.json({ success: true, id: Date.now() });
      } catch (error) {
        res.status(500).json({ error: 'Failed to create feed' });
      }
    });

    this.app.delete('/api/feeds/:id', async (req, res) => {
      try {
        const feedId = req.params.id;
        // Remove feed from configuration
        
        res.json({ success: true });
      } catch (error) {
        res.status(500).json({ error: 'Failed to delete feed' });
      }
    });

    // Test feed endpoint
    this.app.get('/api/test-feed/:id', async (req, res) => {
      try {
        const feedId = req.params.id;
        // Test the RSS feed and return results
        
        res.json({ success: true, items: [] });
      } catch (error) {
        res.status(500).json({ error: 'Feed test failed' });
      }
    });
  }

  setupScheduler() {
    const intervalExpression = `*/${config.app.processingInterval} * * * *`;
    
    cron.schedule(intervalExpression, async () => {
      logger.info('Scheduled RSS processing started');
      await this.processFeeds();
    });

    // Daily cache cleanup
    cron.schedule('0 2 * * *', () => {
      logger.info('Scheduled cache cleanup started');
      cacheManager.cleanup();
    });

    // Weekly system status report
    cron.schedule('0 9 * * 1', async () => {
      logger.info('Sending weekly system status');
      const stats = await this.getSystemStats();
      await discordWebhook.sendSystemStatus(stats);
    });

    logger.info(`Scheduler initialized with ${intervalExpression} processing interval`);
  }

  async processFeeds() {
    try {
      const startTime = Date.now();
      logger.info('Starting RSS generation and processing cycle');

      // Step 1: Generate fresh RSS feeds (this now handles database storage)
      const generationResults = await advancedFeedGenerator.generateAllFeeds();
      
      // Step 2: Process and monetize the generated feeds  
      const processedFeeds = await rssProcessor.processAllFeeds();
      
      // Step 3: Send updates to Discord
      if (processedFeeds.length > 0) {
        logger.info(`Sending ${processedFeeds.length} updates to Discord`);
        await discordWebhook.sendBulkUpdate(processedFeeds);
      }

      const duration = Date.now() - startTime;
      logger.info(`Complete cycle finished in ${duration}ms`, {
        newItems: generationResults.totalNewItems,
        processed: processedFeeds.length,
        duration
      });

      return {
        newItems: generationResults.totalNewItems,
        processed: processedFeeds.length,
        duration,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      logger.error('Error in complete processing cycle', { 
        error: error.message,
        stack: error.stack 
      });
      throw error;
    }
  }</to_replace>
</Editor.edit_file_by_replace>

<Editor.edit_file_by_replace>
<file_name>src/server.js</file_name>
<to_replace>    // Weekly system status report
    cron.schedule('0 9 * * 1', async () => {
      logger.info('Sending weekly system status');
      const stats = await this.getSystemStats();
      await discordWebhook.sendSystemStatus(stats);
    });</to_replace>
<new_content>    // Weekly system status report
    cron.schedule('0 9 * * 1', async () => {
      logger.info('Sending weekly system status');
      const stats = await this.getSystemStats();
      await discordWebhook.sendSystemStatus(stats);
    });

    // Daily database cleanup
    cron.schedule('0 3 * * *', async () => {
      logger.info('Starting database cleanup');
      await databaseManager.cleanup();
    });

  async getSystemStats() {
    const cacheStats = cacheManager.getStats();
    const processingStats = rssProcessor.getProcessingStats();
    
    return {
      system: {
        uptime: process.uptime(),
        nodeVersion: process.version,
        environment: config.app.nodeEnv,
        timestamp: new Date().toISOString()
      },
      cache: cacheStats,
      processing: processingStats,
      config: {
        processingInterval: config.app.processingInterval,
        cacheTTL: config.app.cacheTTL,
        ouoRateLimit: config.ouo.rateLimitPerHour,
        discordRateLimit: config.discord.rateLimitPerMinute
      }
    };
  }

  start() {
    this.app.listen(config.app.port, () => {
      logger.info(`RSS Monetization Server started on port ${config.app.port}`);
      logger.info('System configuration:', {
        processingInterval: config.app.processingInterval,
        cacheTTL: config.app.cacheTTL,
        nodeEnv: config.app.nodeEnv
      });
    });
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  logger.info('Received SIGINT, saving cache and shutting down gracefully');
  cacheManager.saveCache();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Received SIGTERM, saving cache and shutting down gracefully');
  cacheManager.saveCache();
  process.exit(0);
});

// Start the server
const server = new RSSMonetizationServer();
server.start();