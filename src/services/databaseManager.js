const { createClient } = require('@libsql/client');
const config = require('../config/settings');
const logger = require('../utils/logger');

class DatabaseManager {
  constructor() {
    this.client = createClient({
      url: config.database.url,
      authToken: config.database.authToken
    });
    this.initializeDatabase();
  }

  async initializeDatabase() {
    try {
      await this.client.execute(`
        CREATE TABLE IF NOT EXISTS feed_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          item_hash TEXT UNIQUE NOT NULL,
          title TEXT NOT NULL,
          link TEXT NOT NULL,
          description TEXT,
          image_url TEXT,
          feed_type TEXT NOT NULL,
          source_url TEXT NOT NULL,
          pub_date DATETIME NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(title, link)
        )
      `);
      
      await this.client.execute(`
        CREATE INDEX IF NOT EXISTS idx_item_hash ON feed_items(item_hash);
      `);
      
      await this.client.execute(`
        CREATE INDEX IF NOT EXISTS idx_feed_type ON feed_items(feed_type);
      `);
      
      logger.info('Database initialized successfully');
    } catch (error) {
      logger.error('Database initialization failed', { error: error.message });
      throw error;
    }
  }

  async addFeedItem(item) {
    try {
      const result = await this.client.execute({
        sql: `INSERT OR IGNORE INTO feed_items 
              (item_hash, title, link, description, image_url, feed_type, source_url, pub_date)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        args: [
          item.item_hash,
          item.title,
          item.link,
          item.description,
          item.image_url || null,
          item.feed_type,
          item.source_url,
          item.pub_date
        ]
      });
      
      if (result.rowsAffected > 0) {
        logger.debug(`Added new feed item: ${item.title}`);
        return true;
      }
      return false; // Item already exists
      
    } catch (error) {
      logger.error(`Error adding feed item: ${item.title}`, { error: error.message });
      return false;
    }
  }

  async getFeedItems(feedType = null, limit = 1000) {
    try {
      let sql = `SELECT * FROM feed_items`;
      let args = [];
      
      if (feedType) {
        sql += ` WHERE feed_type = ?`;
        args.push(feedType);
      }
      
      sql += ` ORDER BY pub_date DESC LIMIT ?`;
      args.push(limit);
      
      const result = await this.client.execute({ sql, args });
      return result.rows || [];
      
    } catch (error) {
      logger.error('Error getting feed items', { error: error.message });
      return [];
    }
  }

  async getItemByHash(itemHash) {
    try {
      const result = await this.client.execute({
        sql: `SELECT * FROM feed_items WHERE item_hash = ?`,
        args: [itemHash]
      });
      
      return result.rows[0] || null;
    } catch (error) {
      logger.error(`Error getting item by hash: ${itemHash}`, { error: error.message });
      return null;
    }
  }

  async cleanup() {
    try {
      // Keep only the most recent 10,000 items
      await this.client.execute(`
        DELETE FROM feed_items 
        WHERE id NOT IN (
          SELECT id FROM feed_items 
          ORDER BY created_at DESC 
          LIMIT 10000
        )
      `);
      
      logger.info('Database cleanup completed');
    } catch (error) {
      logger.error('Database cleanup failed', { error: error.message });
    }
  }
}

module.exports = new DatabaseManager();