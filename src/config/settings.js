require('dotenv').config();

module.exports = {
  ouo: {
    apiToken: process.env.OUO_API_TOKEN,
    apiUrl: process.env.OUO_API_URL,
    rateLimitPerHour: parseInt(process.env.OUO_RATE_LIMIT_PER_HOUR) || 900
  },
  discord: {
    webhookUrl: process.env.DISCORD_WEBHOOK_URL,
    botName: process.env.DISCORD_BOT_NAME || 'RSS Feed Bot',
    avatarUrl: process.env.DISCORD_AVATAR_URL,
    rateLimitPerMinute: parseInt(process.env.DISCORD_RATE_LIMIT_PER_MINUTE) || 25,
    // Additional webhooks for specific feed types
    webhooks: {
      ivyLeague: process.env.WEBHOOK_IVY_LEAGUE,
      udemy: process.env.WEBHOOK_UDEMY,
      itchio: process.env.WEBHOOK_ITCHIO,
      videogame: process.env.WEBHOOK_VIDEOGAME,
      dlc: process.env.WEBHOOK_DLC
    }
  },
  app: {
    port: process.env.PORT || 3000,
    nodeEnv: process.env.NODE_ENV || 'development',
    logLevel: process.env.LOG_LEVEL || 'info',
    cacheTTL: parseInt(process.env.CACHE_TTL_HOURS) || 24,
    processingInterval: parseInt(process.env.PROCESSING_INTERVAL_MINUTES) || 15
  },
  feeds: {
    directory: './public/feeds',
    supportedFormats: ['.xml', '.rss']
  }
};