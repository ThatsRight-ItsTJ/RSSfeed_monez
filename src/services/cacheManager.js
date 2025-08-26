const fs = require('fs');
const path = require('path');
const config = require('../config/settings');
const logger = require('../utils/logger');

class CacheManager {
  constructor() {
    this.cacheDir = path.join(process.cwd(), 'cache');
    this.cacheFile = path.join(this.cacheDir, 'monetized-links.json');
    this.ensureCacheDirectory();
    this.loadCache();
  }

  ensureCacheDirectory() {
    if (!fs.existsSync(this.cacheDir)) {
      fs.mkdirSync(this.cacheDir, { recursive: true });
    }
  }

  loadCache() {
    try {
      if (fs.existsSync(this.cacheFile)) {
        const cacheData = fs.readFileSync(this.cacheFile, 'utf8');
        this.cache = new Map(JSON.parse(cacheData));
        logger.info(`Loaded ${this.cache.size} cached links`);
      } else {
        this.cache = new Map();
      }
    } catch (error) {
      logger.error('Error loading cache', { error: error.message });
      this.cache = new Map();
    }
  }

  saveCache() {
    try {
      const cacheArray = Array.from(this.cache.entries());
      fs.writeFileSync(this.cacheFile, JSON.stringify(cacheArray, null, 2));
      logger.debug(`Saved ${cacheArray.length} cached links`);
    } catch (error) {
      logger.error('Error saving cache', { error: error.message });
    }
  }

  get(originalUrl) {
    const cached = this.cache.get(originalUrl);
    if (cached && this.isValid(cached)) {
      return cached.monetizedUrl;
    }
    return null;
  }

  set(originalUrl, monetizedUrl) {
    const cacheEntry = {
      monetizedUrl,
      createdAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + (config.app.cacheTTL * 60 * 60 * 1000)).toISOString()
    };
    this.cache.set(originalUrl, cacheEntry);
    this.saveCache();
  }

  isValid(cacheEntry) {
    return new Date(cacheEntry.expiresAt) > new Date();
  }

  cleanup() {
    const beforeSize = this.cache.size;
    for (const [url, entry] of this.cache.entries()) {
      if (!this.isValid(entry)) {
        this.cache.delete(url);
      }
    }
    const afterSize = this.cache.size;
    if (beforeSize !== afterSize) {
      logger.info(`Cleaned up ${beforeSize - afterSize} expired cache entries`);
      this.saveCache();
    }
  }

  getStats() {
    return {
      totalEntries: this.cache.size,
      validEntries: Array.from(this.cache.values()).filter(entry => this.isValid(entry)).length
    };
  }
}

module.exports = new CacheManager();