const { RateLimiterMemory } = require('rate-limiter-flexible');
const config = require('../config/settings');

class RateLimitManager {
  constructor() {
    this.ouoLimiter = new RateLimiterMemory({
      points: config.ouo.rateLimitPerHour,
      duration: 3600, // 1 hour
    });

    this.discordLimiter = new RateLimiterMemory({
      points: config.discord.rateLimitPerMinute,
      duration: 60, // 1 minute
    });
  }

  async checkOuoLimit() {
    try {
      await this.ouoLimiter.consume('ouo-api');
      return true;
    } catch (rejRes) {
      return false;
    }
  }

  async checkDiscordLimit() {
    try {
      await this.discordLimiter.consume('discord-webhook');
      return true;
    } catch (rejRes) {
      return false;
    }
  }

  getOuoResetTime() {
    return this.ouoLimiter.get('ouo-api');
  }

  getDiscordResetTime() {
    return this.discordLimiter.get('discord-webhook');
  }
}

module.exports = new RateLimitManager();