# RSS Feed Monetization & Discord Integration System

Transform RSS feeds into monetized content streams with automated Discord notifications and deploy effortlessly to Railway.

## 🚀 Features

- **RSS Feed Processing**: Automatically processes all RSS feeds from `/public/feeds/`
- **Link Monetization**: Converts external links using ouo.io API for revenue generation
- **Discord Integration**: Sends feed updates to specific Discord channels via webhooks
- **Intelligent Caching**: Caches monetized links to reduce API calls and improve performance
- **Rate Limiting**: Built-in rate limiting for ouo.io and Discord APIs
- **Automated Scheduling**: Processes feeds every 15 minutes (configurable)
- **Feed Integrity**: Maintains original RSS structure while adding monetization
- **Multi-Webhook Support**: Routes different feed types to appropriate Discord channels
- **One-Click Railway Deployment**: Deploy instantly with Railway's infrastructure

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
├── .env.example                  # Environment variables template
├── railway.toml                  # Railway deployment configuration
├── test-setup.js                 # System testing script
└── package.json                  # Node.js dependencies
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Node.js 16+ 
- npm or yarn
- ouo.io account & API token
- Discord webhook URLs
- Railway account (free tier available)

### 2. Quick Deployment to Railway

#### Option A: One-Click Deploy (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Fork this repository to your account
4. Configure environment variables (see Configuration section below)
5. Deploy automatically - Railway handles the rest!

#### Option B: Manual Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Clone and setup locally
git clone https://github.com/ThatsRight-ItsTJ/RSSfeed_monez.git
cd RSSfeed_monez
npm install

# Create Railway project and deploy
railway link
railway up
```

### 3. Local Development Setup (Optional)

```bash
# Clone the repository
git clone https://github.com/ThatsRight-ItsTJ/RSSfeed_monez.git
cd RSSfeed_monez

# Install dependencies
npm install

# Create required directories
mkdir -p logs cache

# Copy environment template
cp .env.example .env
# Edit .env with your API credentials
```

## 🔑 Configuration

### Required Environment Variables

Configure these in Railway's dashboard or use the CLI:

#### Railway Dashboard Method:
1. Go to your Railway project dashboard
2. Click "Variables" tab
3. Add each environment variable below

#### Railway CLI Method:
```bash
railway variables set OUO_API_TOKEN=your_ouo_token
railway variables set DISCORD_WEBHOOK_URL=your_main_webhook
# ... continue for all variables
```

#### Complete Environment Variables:

```env
# ouo.io API Configuration
OUO_API_TOKEN=your_ouo_api_token_here
OUO_API_URL=https://ouo.io/api/shorten
OUO_RATE_LIMIT_PER_HOUR=900

# Discord Webhook Configuration  
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_main_webhook
WEBHOOK_IVY_LEAGUE=https://discord.com/api/webhooks/your_ivy_webhook
WEBHOOK_UDEMY=https://discord.com/api/webhooks/your_udemy_webhook
WEBHOOK_ITCHIO=https://discord.com/api/webhooks/your_itchio_webhook
WEBHOOK_VIDEOGAME=https://discord.com/api/webhooks/your_game_webhook
WEBHOOK_DLC=https://discord.com/api/webhooks/your_dlc_webhook

# Application Settings
NODE_ENV=production
PROCESSING_INTERVAL_MINUTES=15
CACHE_TTL_HOURS=24
DISCORD_RATE_LIMIT_PER_MINUTE=25
LOG_LEVEL=info

# Railway will automatically set PORT
# BASE_URL will be your Railway app URL (e.g., https://your-app.railway.app)
```

### 4. Getting Your API Keys

#### ouo.io API Token:
1. Sign up at [ouo.io](https://ouo.io)
2. Navigate to "Tools & API" section
3. Copy your API Token

#### Discord Webhooks:
1. Go to your Discord server
2. Right-click on target channel → "Edit Channel"
3. Go to "Integrations" → "Webhooks" → "Create Webhook"
4. Copy webhook URL (format: `https://discord.com/api/webhooks/ID/TOKEN`)
5. Repeat for each feed type channel

## 🚀 Deployment Options

### Railway (Recommended)

**Cost**: ~$1-3/month with free $5 monthly credits

**Benefits**:
- Automatic deployments from GitHub
- Built-in cron job support
- Persistent storage
- Zero-config deployment
- Automatic HTTPS
- Global CDN

**Deployment Steps**:
1. Connect GitHub account to Railway
2. Select this repository
3. Add environment variables
4. Deploy automatically

### Alternative Hosting Options

#### Render
- Free tier with 750 hours/month
- Apps sleep after inactivity
- Good for testing

#### Fly.io
- 3 shared VMs free
- More complex setup
- Better for high-performance needs

#### DigitalOcean App Platform
- $5/month minimum
- Very reliable
- Good for production

## 🧪 Testing & Validation

### Environment Validation
```bash
# Test configuration (locally or via Railway logs)
node test-setup.js
```

### API Endpoint Testing
```bash
# Health check
curl https://your-app.railway.app/health

# System statistics
curl https://your-app.railway.app/stats

# Manual processing trigger
curl -X POST https://your-app.railway.app/trigger-processing
```

### Railway-Specific Testing
```bash
# View live logs
railway logs

# Check deployment status
railway status

# Open your deployed app
railway open
```

## 📊 API Endpoints

- `GET /health` - Health check & uptime
- `GET /stats` - System statistics & performance metrics
- `POST /trigger-processing` - Manual feed processing
- `GET /cache/stats` - Cache statistics & efficiency
- `POST /cache/cleanup` - Manual cache cleanup
- `GET /database/stats` - Database statistics (if using database version)

## 📈 Railway-Specific Features

### Automatic Scaling
Railway automatically scales your application based on traffic and resource usage.

### Built-in Monitoring
- View real-time logs in Railway dashboard
- Monitor CPU, memory, and network usage
- Set up alerts for errors or performance issues

### Environment Management
- Easy environment variable management
- Separate staging and production environments
- Rollback capabilities

### Custom Domains
```bash
# Add custom domain (Railway Pro plan)
railway domain add your-domain.com
```

## 🔧 Monitoring & Maintenance

### Railway Dashboard Monitoring
- **Deployments**: Track deployment history and status
- **Metrics**: CPU, memory, and request metrics
- **Logs**: Real-time application logs
- **Variables**: Manage environment variables

### Application Logs
```bash
# View logs via Railway CLI
railway logs --tail

# View logs in Railway dashboard
# Go to Project → Deployments → View Logs
```

### Scheduled Maintenance
- **Every 15 minutes**: RSS feed processing
- **Daily at 2 AM**: Cache cleanup  
- **Weekly on Monday at 9 AM**: System status report
- **On Railway deployment**: Automatic cache restoration

## 💰 Cost Optimization on Railway

### Typical Usage Costs
- **RSS processing every 15 minutes**: ~$1-2/month
- **24/7 uptime**: ~$2-3/month
- **Database operations**: ~$0.50/month
- **Total**: Usually under the $5 monthly credit

### Cost-Saving Tips
1. **Optimize processing intervals**: Consider 30-minute intervals instead of 15
2. **Implement smart caching**: Reduce redundant API calls
3. **Monitor usage**: Use Railway's metrics to track resource consumption
4. **Use webhooks**: Only process when feeds actually update

## 🚨 Troubleshooting

### Common Railway Issues

#### Environment Variables Not Set
```bash
# Check variables are set
railway variables

# Set missing variables
railway variables set VARIABLE_NAME=value
```

#### Application Not Starting
```bash
# Check logs for errors
railway logs

# Verify package.json start script
# Should be: "start": "node src/server.js"
```

#### Out of Memory
```bash
# Monitor memory usage in Railway dashboard
# Consider upgrading to paid plan if needed
```

### Getting Help
- **Railway Community**: [Railway Discord](https://discord.gg/railway)
- **Documentation**: [Railway Docs](https://docs.railway.app)
- **GitHub Issues**: Report issues in this repository

## 🔄 Updates & Deployments

### Automatic Deployments
Railway automatically deploys when you push to your connected GitHub branch.

### Manual Deployments
```bash
# Deploy latest changes
railway up

# Deploy specific commit
railway up --commit abc1234
```

### Rollbacks
```bash
# Rollback to previous deployment
railway rollback
```

## 📞 Support & Community

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/ThatsRight-ItsTJ/RSSfeed_monez/issues)
- **Railway Community**: [Join Railway Discord](https://discord.gg/railway)
- **Documentation**: [Railway Documentation](https://docs.railway.app)

---

## 🎯 Quick Start Summary

1. **Click**: Deploy to Railway button above
2. **Configure**: Add your API keys and Discord webhooks
3. **Deploy**: Railway handles everything automatically
4. **Monitor**: Check logs and metrics in Railway dashboard
5. **Earn**: Start monetizing your RSS feeds immediately

**Total setup time**: 5-10 minutes  
**Monthly cost**: Usually free with Railway's $5 credit  
**Maintenance**: Fully automated

Transform your RSS feeds into revenue streams today! 🚀
