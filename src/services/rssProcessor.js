const fs = require('fs');
const path = require('path');
const Parser = require('rss-parser');
const xml2js = require('xml2js');
const config = require('../config/settings');
const logger = require('../utils/logger');
const linkMonetizer = require('./linkMonetizer');

class RSSProcessor {
  constructor() {
    this.parser = new Parser();
    this.feedsDir = config.feeds.directory;
    this.processedFeeds = new Map(); // Track last processing times
  }

  async getAllFeeds() {
    try {
      const feedFiles = fs.readdirSync(this.feedsDir)
        .filter(file => config.feeds.supportedFormats.some(ext => file.endsWith(ext)))
        .map(file => path.join(this.feedsDir, file));
      
      logger.info(`Found ${feedFiles.length} RSS feeds to process`);
      return feedFiles;
    } catch (error) {
      logger.error('Error reading feeds directory', { error: error.message });
      return [];
    }
  }

  async processFeed(feedPath) {
    try {
      const feedContent = fs.readFileSync(feedPath, 'utf8');
      const feed = await this.parser.parseString(feedContent);
      const feedName = path.basename(feedPath);
      
      logger.info(`Processing feed: ${feedName}`, { 
        items: feed.items.length,
        title: feed.title 
      });

      // Track if feed has new content
      const lastModified = fs.statSync(feedPath).mtime;
      const lastProcessed = this.processedFeeds.get(feedPath);
      
      if (lastProcessed && lastModified <= lastProcessed) {
        logger.debug(`Feed ${feedName} unchanged since last processing`);
        return null; // No new content
      }

      // Process and monetize links in feed items
      const processedItems = [];
      const monetizedUrls = [];
      
      for (const item of feed.items) {
        const originalItem = { ...item };
        
        // Monetize main link
        if (item.link) {
          const monetizedLink = await linkMonetizer.monetizeUrl(item.link);
          if (monetizedLink !== item.link) {
            monetizedUrls.push({ original: item.link, monetized: monetizedLink });
          }
          item.link = monetizedLink;
        }

        // Monetize links in content/description
        if (item.content || item.contentSnippet) {
          const content = item.content || item.contentSnippet;
          const monetizedContent = await this.monetizeLinksInContent(content);
          if (item.content) item.content = monetizedContent.content;
          if (item.contentSnippet) item.contentSnippet = monetizedContent.content;
          monetizedUrls.push(...monetizedContent.monetizedUrls);
        }

        processedItems.push(item);
      }

      // Update processing timestamp
      this.processedFeeds.set(feedPath, new Date());

      const result = {
        feedPath,
        feedName,
        feed: { ...feed, items: processedItems },
        originalFeed: feed,
        monetizedUrls,
        stats: {
          totalItems: feed.items.length,
          monetizedLinks: monetizedUrls.length,
          processedAt: new Date().toISOString()
        }
      };

      logger.info(`Completed processing feed: ${feedName}`, result.stats);
      return result;

    } catch (error) {
      logger.error(`Error processing feed: ${feedPath}`, { 
        error: error.message,
        stack: error.stack 
      });
      return null;
    }
  }

  async monetizeLinksInContent(content) {
    const urlRegex = /(https?:\/\/[^\s<>"]+)/gi;
    const urls = content.match(urlRegex) || [];
    const monetizedUrls = [];
    
    let updatedContent = content;
    
    for (const url of urls) {
      const monetized = await linkMonetizer.monetizeUrl(url);
      if (monetized !== url) {
        updatedContent = updatedContent.replace(url, monetized);
        monetizedUrls.push({ original: url, monetized });
      }
    }
    
    return {
      content: updatedContent,
      monetizedUrls
    };
  }

  async generateUpdatedFeed(processedFeed) {
    try {
      const builder = new xml2js.Builder({
        rootName: 'rss',
        xmldec: { version: '1.0', encoding: 'UTF-8' },
        renderOpts: { pretty: true }
      });

      const rssObject = {
        $: { version: '2.0' },
        channel: {
          title: processedFeed.feed.title,
          description: processedFeed.feed.description,
          link: processedFeed.feed.link,
          language: processedFeed.feed.language || 'en',
          lastBuildDate: new Date().toUTCString(),
          generator: 'RSS Feed Monetizer',
          item: processedFeed.feed.items.map(item => ({
            title: item.title,
            description: item.content || item.contentSnippet,
            link: item.link,
            guid: item.guid || item.link,
            pubDate: item.pubDate || item.isoDate
          }))
        }
      };

      return builder.buildObject(rssObject);
    } catch (error) {
      logger.error('Error generating updated feed', { error: error.message });
      return null;
    }
  }

  async processAllFeeds() {
    const feeds = await this.getAllFeeds();
    const results = [];
    
    for (const feedPath of feeds) {
      const processed = await this.processFeed(feedPath);
      if (processed) {
        results.push(processed);
      }
      
      // Small delay between feeds
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    return results;
  }

  getProcessingStats() {
    return {
      totalFeedsMonitored: this.processedFeeds.size,
      lastProcessingTimes: Object.fromEntries(
        Array.from(this.processedFeeds.entries()).map(([path, time]) => [
          path.basename(path), 
          time.toISOString()
        ])
      )
    };
  }
}

module.exports = new RSSProcessor();