# RSS Feed Monetization & Discord Integration System

Transform RSS feeds into monetized content streams with automated Discord notifications.

## 🚀 Features

- **RSS Feed Processing**: Automatically processes all RSS feeds from `/public/feeds/`
- **Link Monetization**: Converts external links using ouo.io API for revenue generation
- **Discord Integration**: Sends feed updates to specific Discord channels via webhooks
- **Intelligent Caching**: Caches monetized links to reduce API calls and improve performance
- **Rate Limiting**: Built-in rate limiting for ouo.io and Discord APIs
- **Automated Scheduling**: Processes feeds every 15 minutes (configurable)
- **Feed Integrity**: Maintains original RSS structure while adding monetization
- **Multi-Webhook Support**: Routes different feed types to appropriate Discord channels

## 📁 Project Structure

```
RSSfeed_monez/
├── src/
│   ├── services/
│   │   ├── rssProcessor.js       # RSS feed processing & monetization
│   │   ├── linkMonetizer.js      # ouo.io API integration
│   │   ├── discordWebhook.js     # Discord webhook notifications
│   │   └── cacheManager.js       # Monetized link caching
│   ├── utils/
│   │   ├── logger.js             # Logging utility
│   │   └── rateLimiter.js        # API rate limiting
│   ├── config/
│   │   └── settings.js           # Configuration management
│   └── server.js                 # Main application server
├── public/
│   └── feeds/                    # RSS feed files (XML)
├── logs/                         # Application logs
├── cache/                        # Monetized link cache
├── .env                          # Environment variables
├── test-setup.js                 # System testing script
└── package.json                  # Node.js dependencies
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Node.js 16+ 
- npm or yarn
- ouo.io account & API token
- Discord webhook URLs

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/ThatsRight-ItsTJ/RSSfeed_monez.git
cd RSSfeed_monez

# Install dependencies
npm install

# Create required directories
mkdir -p logs cache
```

### 3. Configuration

Update `.env` file with your API credentials:

```env
# ouo.io API Configuration
OUO_API_TOKEN=your_ouo_api_token_here
OUO_API_URL=https://ouo.io/api/shorten

# Discord Webhook Configuration  
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_main_webhook
WEBHOOK_IVY_LEAGUE=https://discord.com/api/webhooks/your_ivy_webhook
WEBHOOK_UDEMY=https://discord.com/api/webhooks/your_udemy_webhook
WEBHOOK_ITCHIO=https://discord.com/api/webhooks/your_itchio_webhook
WEBHOOK_VIDEOGAME=https://discord.com/api/webhooks/your_game_webhook
WEBHOOK_DLC=https://discord.com/api/webhooks/your_dlc_webhook

# Application Settings
PORT=3000
NODE_ENV=production
PROCESSING_INTERVAL_MINUTES=15
CACHE_TTL_HOURS=24
```

### 4. Testing

```bash
# Test system configuration
node test-setup.js

# Test RSS processing
npm run test-processing

# Test link monetization
npm run test-monetization
```

### 5. Running the Application

```bash
# Development mode
npm run dev

# Production mode
npm start

# Using PM2 (recommended for production)
npm install -g pm2
pm2 start src/server.js --name "rss-monetizer"
pm2 save
pm2 startup
```

## 🔧 API Endpoints

- `GET /health` - Health check
- `GET /stats` - System statistics
- `POST /trigger-processing` - Manual feed processing
- `GET /cache/stats` - Cache statistics
- `POST /cache/cleanup` - Manual cache cleanup

## 📊 Monitoring & Maintenance

### Logs
- Application logs: `./logs/app-YYYY-MM-DD.log`
- Console output with timestamps and log levels
- Automatic log rotation (7 days retention)

### Cache Management
- Automatic cleanup of expired entries (daily at 2 AM)
- Manual cleanup via API endpoint
- TTL-based expiration (24 hours default)

### Discord Notifications
- Feed updates sent to appropriate channels
- Weekly system status reports (Mondays at 9 AM)
- Rate limiting prevents API quota exhaustion

### Performance Optimization
- Configurable processing intervals
- Intelligent caching reduces API calls
- Rate limiting prevents service overload
- Small delays between operations for stability

## 🛠️ Feed Processing Logic

1. **Discovery**: Scans `/public/feeds/` for XML/RSS files
2. **Change Detection**: Only processes feeds with new content
3. **Link Extraction**: Finds all URLs in feed items and content
4. **Monetization**: Converts URLs using ouo.io API with caching
5. **Feed Generation**: Creates monetized RSS feeds
6. **Discord Notification**: Sends updates to appropriate channels
7. **Caching**: Stores monetized URLs for future use

## 🔄 Automated Features

- **Every 15 minutes**: RSS feed processing
- **Daily at 2 AM**: Cache cleanup
- **Weekly on Monday at 9 AM**: System status report
- **On shutdown**: Graceful cache saving

## 📈 Revenue Generation

- All external links monetized through ouo.io
- Cached links reduce API costs
- Feed integrity maintained for user experience
- Revenue tracking through ouo.io dashboard

## 🚨 Error Handling

- Comprehensive logging for debugging
- Fallback to original URLs if monetization fails
- Rate limit protection with automatic backoff
- Graceful degradation on service failures

## 🔗 Legacy Integration

Maintains compatibility with existing RSS feeds while adding monetization layer. Original Python components have been replaced with Node.js equivalents for better performance and maintainability.

---

**Note**: This system has been transformed from a Python-based RSS generator to a Node.js monetization platform as per the implementation plan. All original feed processing capabilities are preserved while adding revenue generation features.