const axios = require('axios');
const config = require('../config/settings');
const logger = require('../utils/logger');
const cacheManager = require('./cacheManager');
const rateLimiter = require('../utils/rateLimiter');

class LinkMonetizer {
  constructor() {
    this.apiToken = config.ouo.apiToken;
  }

  async monetizeUrl(originalUrl) {
    // Check cache first
    const cached = cacheManager.get(originalUrl);
    if (cached) {
      logger.debug('Using cached monetized URL', { originalUrl, cached });
      return cached;
    }

    // Check rate limit
    const canProceed = await rateLimiter.checkOuoLimit();
    if (!canProceed) {
      logger.warn('ouo.io rate limit exceeded, using original URL', { originalUrl });
      return originalUrl;
    }

    // Check if we have a valid API token
    if (!this.apiToken || this.apiToken === 'your_ouo_api_token_here') {
      logger.warn('ouo.io API token not configured, using original URL', { originalUrl });
      return originalUrl;
    }

    try {
      // Use the correct ouo.io API format: http://ouo.io/api/<ouo_token>?s=<yourdestinationlink.com>
      const apiUrl = `http://ouo.io/api/${this.apiToken}?s=${encodeURIComponent(originalUrl)}`;
      
      const response = await axios.get(apiUrl, {
        timeout: 10000,
        headers: {
          'User-Agent': 'RSS-Feed-Monetizer/2.0'
        }
      });

      // The ouo.io API returns the shortened URL directly as text
      if (response.data && typeof response.data === 'string' && response.data.startsWith('http')) {
        const monetizedUrl = response.data.trim();
        cacheManager.set(originalUrl, monetizedUrl);
        logger.info('Successfully monetized URL', { originalUrl, monetizedUrl });
        return monetizedUrl;
      } else {
        logger.warn('ouo.io API returned unexpected response', { 
          originalUrl, 
          response: response.data 
        });
        return originalUrl;
      }
    } catch (error) {
      logger.error('Error monetizing URL', { 
        originalUrl, 
        error: error.message,
        stack: error.stack 
      });
      return originalUrl; // Fallback to original URL
    }
  }

  async monetizeMultipleUrls(urls) {
    const results = [];
    for (const url of urls) {
      const monetized = await this.monetizeUrl(url);
      results.push({ original: url, monetized });
      
      // Add small delay to respect rate limits
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    return results;
  }

  getApiStats() {
    return rateLimiter.getOuoResetTime();
  }
}

module.exports = new LinkMonetizer();