const axios = require('axios');
const config = require('../config/settings');
const logger = require('../utils/logger');
const rateLimiter = require('../utils/rateLimiter');

class DiscordWebhook {
  constructor() {
    this.webhookUrl = config.discord.webhookUrl;
    this.botName = config.discord.botName;
    this.avatarUrl = config.discord.avatarUrl;
    this.specificWebhooks = config.discord.webhooks;
  }

  getWebhookForFeedType(feedName) {
    // Determine appropriate webhook based on feed name/type
    const feedLower = feedName.toLowerCase();
    
    if (feedLower.includes('ivy') || feedLower.includes('league')) {
      return this.specificWebhooks.ivyLeague;
    } else if (feedLower.includes('udemy') || feedLower.includes('course')) {
      return this.specificWebhooks.udemy;
    } else if (feedLower.includes('itch')) {
      return this.specificWebhooks.itchio;
    } else if (feedLower.includes('game') && !feedLower.includes('loot')) {
      return this.specificWebhooks.videogame;
    } else if (feedLower.includes('loot') || feedLower.includes('dlc')) {
      return this.specificWebhooks.dlc;
    }
    
    // Default to main webhook
    return this.webhookUrl;
  }

  async sendFeedUpdate(processedFeed) {
    const canSend = await rateLimiter.checkDiscordLimit();
    if (!canSend) {
      logger.warn('Discord rate limit exceeded, skipping webhook', { 
        feed: processedFeed.feedName 
      });
      return false;
    }

    try {
      const embed = this.createFeedUpdateEmbed(processedFeed);
      const webhookUrl = this.getWebhookForFeedType(processedFeed.feedName);
      
      const payload = {
        username: this.botName,
        avatar_url: this.avatarUrl,
        embeds: [embed]
      };

      const response = await axios.post(webhookUrl, payload, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      });

      logger.info('Successfully sent Discord webhook', { 
        feed: processedFeed.feedName,
        items: processedFeed.stats.totalItems,
        monetizedLinks: processedFeed.stats.monetizedLinks,
        webhook: webhookUrl
      });

      return true;
    } catch (error) {
      logger.error('Error sending Discord webhook', { 
        feed: processedFeed.feedName,
        error: error.message,
        status: error.response?.status,
        data: error.response?.data
      });
      return false;
    }
  }

  createFeedUpdateEmbed(processedFeed) {
    const { feed, stats, monetizedUrls } = processedFeed;
    
    // Get first few items for preview
    const previewItems = feed.items.slice(0, 3).map(item => 
      `• [${item.title}](${item.link})`
    ).join('\n');

    const embed = {
      title: `📡 ${feed.title} - Feed Updated`,
      description: feed.description ? feed.description.substring(0, 200) + '...' : 'New content available',
      color: 0x00ff00, // Green
      fields: [
        {
          name: '📊 Update Stats',
          value: `**Items:** ${stats.totalItems}\n**Monetized Links:** ${stats.monetizedLinks}\n**Processed:** ${new Date(stats.processedAt).toLocaleString()}`,
          inline: true
        },
        {
          name: '🔗 Recent Items',
          value: previewItems || 'No items available',
          inline: false
        }
      ],
      footer: {
        text: `💰 Links monetized to support content creators | Feed: ${processedFeed.feedName}`,
        icon_url: this.avatarUrl
      },
      timestamp: new Date().toISOString()
    };

    // Add revenue info if significant monetization occurred
    if (stats.monetizedLinks > 5) {
      embed.fields.push({
        name: '💰 Monetization Impact',
        value: `${stats.monetizedLinks} links converted to support creators`,
        inline: true
      });
    }

    return embed;
  }

  async sendBulkUpdate(processedFeeds) {
    const successful = [];
    const failed = [];

    for (const feed of processedFeeds) {
      const sent = await this.sendFeedUpdate(feed);
      if (sent) {
        successful.push(feed.feedName);
      } else {
        failed.push(feed.feedName);
      }
      
      // Delay between webhooks to respect rate limits
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    logger.info('Bulk Discord webhook update completed', { 
      successful: successful.length,
      failed: failed.length,
      successfulFeeds: successful,
      failedFeeds: failed
    });

    return { successful, failed };
  }

  async sendSystemStatus(stats) {
    const canSend = await rateLimiter.checkDiscordLimit();
    if (!canSend) {
      logger.warn('Discord rate limit exceeded for system status');
      return false;
    }

    try {
      const embed = {
        title: '🤖 RSS Monetizer System Status',
        color: 0x0099ff, // Blue
        fields: [
          {
            name: '📊 Processing Stats',
            value: `**Feeds Monitored:** ${stats.feedsProcessed}\n**Total Items:** ${stats.totalItems}\n**Links Monetized:** ${stats.totalMonetized}`,
            inline: true
          },
          {
            name: '💾 Cache Stats',
            value: `**Cached Links:** ${stats.cachedLinks}\n**Valid Entries:** ${stats.validCacheEntries}`,
            inline: true
          },
          {
            name: '🔄 Last Run',
            value: new Date().toLocaleString(),
            inline: true
          }
        ],
        timestamp: new Date().toISOString(),
        footer: {
          text: 'Automated system status report'
        }
      };

      await axios.post(this.webhookUrl, {
        username: this.botName,
        avatar_url: this.avatarUrl,
        embeds: [embed]
      });

      logger.info('System status sent to Discord');
      return true;
    } catch (error) {
      logger.error('Error sending system status to Discord', { error: error.message });
      return false;
    }
  }
}

module.exports = new DiscordWebhook();