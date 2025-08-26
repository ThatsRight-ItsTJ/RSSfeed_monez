const express = require('express');
const helmet = require('helmet');
const cron = require('node-cron');
const config = require('./config/settings');
const logger = require('./utils/logger');
const rssProcessor = require('./services/rssProcessor');
const discordWebhook = require('./services/discordWebhook');
const cacheManager = require('./services/cacheManager');

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
      logger.info('Starting RSS feed processing cycle');

      const processedFeeds = await rssProcessor.processAllFeeds();
      
      if (processedFeeds.length > 0) {
        logger.info(`Processing completed, sending ${processedFeeds.length} updates to Discord`);
        await discordWebhook.sendBulkUpdate(processedFeeds);
      } else {
        logger.info('No feed updates found');
      }

      const duration = Date.now() - startTime;
      logger.info(`RSS processing cycle completed in ${duration}ms`, {
        processedFeeds: processedFeeds.length,
        duration
      });

      return {
        processedFeeds: processedFeeds.length,
        duration,
        timestamp: new Date().toISOString()
      };

    } catch (error) {
      logger.error('Error in feed processing cycle', { 
        error: error.message,
        stack: error.stack 
      });
      throw error;
    }
  }

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