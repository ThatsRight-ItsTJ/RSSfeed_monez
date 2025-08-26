require('dotenv').config();

// Validate required environment variables
const requiredEnvVars = [
  'OUO_API_TOKEN',
  'DISCORD_WEBHOOK_URL',
  'TURSO_DATABASE_URL',
  'TURSO_AUTH_TOKEN'
];

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    console.error(`❌ Missing required environment variable: ${envVar}`);
    process.exit(1);
  }
}

module.exports = {
  // ouo.io API Configuration
  ouo: {
    apiToken: process.env.OUO_API_TOKEN,
    apiUrl: process.env.OUO_API_URL || 'https://ouo.io/api/shorten',
    requestDelay: 2000, // 2 seconds between requests
    maxRetries: 3,
    rateLimitPerHour: parseInt(process.env.OUO_RATE_LIMIT_PER_HOUR) || 900
  },

  // Discord Webhook Configuration
  discord: {
    webhookUrl: process.env.DISCORD_WEBHOOK_URL,
    botName: process.env.DISCORD_BOT_NAME || 'RSS Feed Bot',
    avatarUrl: process.env.DISCORD_AVATAR_URL,
    rateLimitPerMinute: parseInt(process.env.DISCORD_RATE_LIMIT_PER_MINUTE) || 25,
    webhooks: {
      ivyLeague: process.env.WEBHOOK_IVY_LEAGUE,
      udemy: process.env.WEBHOOK_UDEMY,
      itchio: process.env.WEBHOOK_ITCHIO,
      videogame: process.env.WEBHOOK_VIDEOGAME,
      dlc: process.env.WEBHOOK_DLC
    },
    rateLimitDelay: 1000, // 1 second between webhook calls
    maxRetries: 3
  },

  // Database Configuration
  database: {
    url: process.env.TURSO_DATABASE_URL,
    authToken: process.env.TURSO_AUTH_TOKEN
  },

  // Application Settings
  app: {
    port: process.env.PORT || 3000,
    nodeEnv: process.env.NODE_ENV || 'development',
    logLevel: process.env.LOG_LEVEL || 'info',
    cacheTTL: parseInt(process.env.CACHE_TTL_HOURS) || 24,
    processingInterval: parseInt(process.env.PROCESSING_INTERVAL_MINUTES) || 15,
    baseUrl: process.env.BASE_URL || 'http://localhost:3000',
    webhookToken: process.env.RSS_PROCESSOR_TOKEN
  },

  // Feed Configuration
  feeds: {
    directory: './public/feeds',
    supportedFormats: ['.xml', '.rss']
  },

  // Cache Configuration
  cache: {
    ttlHours: parseInt(process.env.CACHE_TTL_HOURS) || 24,
    maxEntries: 10000,
    cleanupInterval: '0 2 * * *' // Daily at 2 AM
  },

  // Rate Limiting
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
  }
};