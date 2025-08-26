const axios = require('axios');
const config = require('../config/settings');
const logger = require('../utils/logger');
const cacheManager = require('./cacheManager');
const rateLimiter = require('../utils/rateLimiter');

class LinkMonetizer {
  constructor() {
    this.apiUrl = config.ouo.apiUrl;
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

    try {
      const response = await axios.post(this.apiUrl, 
        `token=${this.apiToken}&url=${encodeURIComponent(originalUrl)}`,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          timeout: 10000
        }
      );

      if (response.data && response.data.status === 'success') {
        const monetizedUrl = response.data.shortenedUrl;
        cacheManager.set(originalUrl, monetizedUrl);
        logger.info('Successfully monetized URL', { originalUrl, monetizedUrl });
        return monetizedUrl;
      } else {
        logger.warn('ouo.io API returned error', { 
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