const axios = require('axios');
const cheerio = require('cheerio');
const Parser = require('rss-parser');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const xml2js = require('xml2js');
const feedSources = require('../config/feed-sources');
const databaseManager = require('./databaseManager');
const logger = require('../utils/logger');
const config = require('../config/settings');

class AdvancedFeedGenerator {
  constructor() {
    this.parser = new Parser();
    this.builder = new xml2js.Builder({
      rootName: 'rss',
      xmldec: { version: '1.0', encoding: 'UTF-8' },
      renderOpts: { pretty: true }
    });
  }

  generateItemHash(title, link) {
    const content = `${title}${link}`;
    return crypto.createHash('sha256').update(content).digest('hex').substring(0, 7);
  }

  determineItemClass(sourceConfig, item) {
    const sourceUrl = sourceConfig.base_url.toLowerCase();
    
    if (sourceUrl.includes('gamerpower.com')) {
      if (sourceConfig.id === 'gamerpower-loot') {
        return 'DLC';
      } else if (sourceConfig.id === 'gamerpower-games') {
        return 'Videogame';
      }
    }
    
    if (sourceUrl.includes('itch.io')) return 'itchio_game';
    if (sourceUrl.includes('classcentral.com')) return 'Ivy_League_Course';
    if (sourceUrl.includes('real.discount') || 
        sourceUrl.includes('udemyfreebies.com')) return 'Udemy_Course';
    
    return 'unknown';
  }

  async processGamerPowerAPI(config) {
    try {
      const response = await axios.get(config.rss_url, { timeout: 30000 });
      const items = response.data || [];
      
      const results = [];
      for (const item of items.slice(0, config.max_entries)) {
        const feedItem = {
          title: item.title,
          link: item.gamerpower_url || item.open_giveaway_url,
          description: item.description || '',
          image_url: item.image,
          pub_date: new Date().toISOString(),
          source_url: config.base_url,
          feed_type: this.determineItemClass(config, item),
          item_hash: this.generateItemHash(item.title, item.gamerpower_url || item.open_giveaway_url)
        };
        
        const added = await databaseManager.addFeedItem(feedItem);
        if (added) {
          results.push(feedItem);
          logger.info(`Added GamerPower item: ${feedItem.title}`);
        }
      }
      
      return results;
    } catch (error) {
      logger.error(`Error processing GamerPower API: ${config.name}`, { error: error.message });
      return [];
    }
  }

  async processRealDiscountAPI(config) {
    try {
      const response = await axios.get(config.rss_url, { timeout: 30000 });
      const data = response.data;
      
      const results = [];
      const courses = data.results || [];
      
      for (const course of courses.slice(0, config.max_entries)) {
        const feedItem = {
          title: course.name,
          link: course.url,
          description: course.headline || '',
          image_url: course.image_240x135,
          pub_date: new Date().toISOString(),
          source_url: config.base_url,
          feed_type: this.determineItemClass(config, course),
          item_hash: this.generateItemHash(course.name, course.url)
        };
        
        const added = await databaseManager.addFeedItem(feedItem);
        if (added) {
          results.push(feedItem);
          logger.info(`Added Real Discount item: ${feedItem.title}`);
        }
      }
      
      return results;
    } catch (error) {
      logger.error(`Error processing Real Discount API: ${config.name}`, { error: error.message });
      return [];
    }
  }

  async processRSSFeed(config) {
    try {
      const feed = await this.parser.parseURL(config.rss_url);
      const results = [];
      
      for (const entry of feed.entries.slice(0, config.max_entries)) {
        const feedItem = {
          title: entry.title,
          link: entry.link,
          description: entry.contentSnippet || entry.content || '',
          pub_date: entry.isoDate || new Date().toISOString(),
          source_url: config.base_url,
          feed_type: this.determineItemClass(config, entry),
          item_hash: this.generateItemHash(entry.title, entry.link)
        };
        
        // Extract image from enclosures
        if (entry.enclosure && entry.enclosure.type && entry.enclosure.type.startsWith('image/')) {
          feedItem.image_url = entry.enclosure.url;
        }
        
        const added = await databaseManager.addFeedItem(feedItem);
        if (added) {
          results.push(feedItem);
          logger.info(`Added RSS item: ${feedItem.title}`);
        }
      }
      
      return results;
    } catch (error) {
      logger.error(`Error processing RSS feed: ${config.name}`, { error: error.message });
      return [];
    }
  }

  async processRSSWithXPath(config) {
    try {
      const feed = await this.parser.parseURL(config.rss_url);
      const results = [];
      
      for (const entry of feed.entries.slice(0, config.max_entries)) {
        try {
          // Fetch the page content for XPath processing
          const response = await axios.get(entry.link, { timeout: 30000 });
          const $ = cheerio.load(response.data);
          
          // Convert XPath to CSS selector (simplified conversion)
          const cssSelector = this.xpathToCssSelector(config.xpath);
          const extractedUrl = $(cssSelector).attr('href');
          
          if (extractedUrl) {
            let finalUrl = extractedUrl;
            if (!finalUrl.startsWith('http')) {
              finalUrl = new URL(extractedUrl, config.base_url).href;
            }
            
            // Extract image if xpath provided
            let imageUrl = null;
            if (config.image_xpath) {
              const imageCssSelector = this.xpathToCssSelector(config.image_xpath);
              const rawImageUrl = $(imageCssSelector).attr('src');
              imageUrl = this.cleanImageUrl(rawImageUrl);
            }
            
            const feedItem = {
              title: entry.title,
              link: finalUrl,
              description: entry.contentSnippet || entry.content || '',
              image_url: imageUrl,
              pub_date: entry.isoDate || new Date().toISOString(),
              source_url: config.base_url,
              feed_type: this.determineItemClass(config, entry),
              item_hash: this.generateItemHash(entry.title, finalUrl)
            };
            
            const added = await databaseManager.addFeedItem(feedItem);
            if (added) {
              results.push(feedItem);
              logger.info(`Added XPath-processed item: ${feedItem.title}`);
            }
          }
        } catch (entryError) {
          logger.warn(`Error processing entry: ${entry.title}`, { error: entryError.message });
          continue;
        }
      }
      
      return results;
    } catch (error) {
      logger.error(`Error processing RSS with XPath: ${config.name}`, { error: error.message });
      return [];
    }
  }

  xpathToCssSelector(xpath) {
    // Simple XPath to CSS conversion - you may need to expand this
    return xpath
      .replace(/\/\//g, '') // Remove //
      .replace(/\[@class="([^"]+)"\]/g, '.$1') // Convert class attributes
      .replace(/\[@href/g, '[href') // Keep href attributes as is
      .replace(/\/@href/g, '') // Remove /@href
      .replace(/\/@src/g, '') // Remove /@src
      .replace(/\/a/g, ' a') // Convert /a to space a
      .replace(/\/img/g, ' img'); // Convert /img to space img
  }

  cleanImageUrl(url) {
    if (!url) return null;
    
    if (url.endsWith('/h')) {
      url = url.slice(0, -2);
    }
    
    if (url.includes('udemycdn.com')) {
      const parts = url.split('/');
      if (parts.length >= 2) {
        const courseId = parts[parts.length - 2];
        const imageName = parts[parts.length - 1];
        return `https://img-c.udemycdn.com/course/750x422/${courseId}_${imageName}`;
      }
    }
    
    return url;
  }

  async generateAllFeeds() {
    try {
      logger.info('Starting feed generation process');
      let totalNewItems = 0;
      
      // Process GamerPower feeds
      const gamerPowerResults = await this.processGamerPowerAPI(feedSources.GAMERPOWER_LOOT_CONFIG);
      totalNewItems += gamerPowerResults.length;
      
      const gamerPowerGamesResults = await this.processGamerPowerAPI(feedSources.GAMERPOWER_GAMES_CONFIG);
      totalNewItems += gamerPowerGamesResults.length;
      
      // Process Itch.io
      const itchResults = await this.processRSSFeed(feedSources.ITCH_CONFIG);
      totalNewItems += itchResults.length;
      
      // Process Class Central
      const classCentralResults = await this.processRSSWithXPath(feedSources.CLASS_CENTRAL_CONFIG);
      totalNewItems += classCentralResults.length;
      
      // Process Udemy sources
      for (const udemyConfig of feedSources.UDEMY_SOURCES) {
        let results = [];
        if (udemyConfig.api_type === 'real_discount') {
          results = await this.processRealDiscountAPI(udemyConfig);
        } else {
          results = await this.processRSSWithXPath(udemyConfig);
        }
        totalNewItems += results.length;
      }
      
      // Generate RSS files from database
      await this.generateRSSFiles();
      
      logger.info(`Feed generation completed. Added ${totalNewItems} new items`);
      return { totalNewItems, timestamp: new Date().toISOString() };
      
    } catch (error) {
      logger.error('Feed generation failed', { error: error.message });
      throw error;
    }
  }

  async generateRSSFiles() {
    try {
      // Generate main feed with all items
      const allItems = await databaseManager.getFeedItems();
      await this.createRSSFile(allItems, 'all-offers.xml', 'All Offers', 'Combined feed from all sources');
      
      // Generate category-specific feeds
      const feedTypes = ['DLC', 'Videogame', 'itchio_game', 'Ivy_League_Course', 'Udemy_Course'];
      
      for (const feedType of feedTypes) {
        const items = await databaseManager.getFeedItems(feedType);
        if (items.length > 0) {
          const filename = `${feedType.toLowerCase().replace('_', '-')}.xml`;
          const title = `${feedType.replace('_', ' ')} Offers`;
          await this.createRSSFile(items, filename, title, `Feed for ${feedType} offers`);
        }
      }
      
      // Generate redirect feeds
      await this.generateRedirectFeeds();
      
    } catch (error) {
      logger.error('Error generating RSS files', { error: error.message });
    }
  }

  async createRSSFile(items, filename, title, description) {
    try {
      const rssItems = items.map(item => {
        const rssItem = {
          title: [item.title],
          description: [`<![CDATA[<class>${item.feed_type}</class><hash>${item.item_hash}</hash>${item.description || ''}]]>`],
          link: [item.link],
          guid: [item.item_hash],
          pubDate: [new Date(item.pub_date).toUTCString()]
        };
        
        if (item.image_url) {
          rssItem.enclosure = {
            $: {
              url: item.image_url,
              length: '0',
              type: 'image/jpeg'
            }
          };
        }
        
        return rssItem;
      });

      const rssObject = {
        $: { 
          version: '2.0',
          'xmlns:atom': 'http://www.w3.org/2005/Atom'
        },
        channel: [{
          title: [title],
          description: [description],
          link: [config.app.baseUrl || 'https://www.goodoffers.theworkpc.com'],
          language: ['en-US'],
          lastBuildDate: [new Date().toUTCString()],
          generator: ['Advanced RSS Generator v2.0'],
          'atom:link': {
            $: {
              href: `${config.app.baseUrl || 'https://www.goodoffers.theworkpc.com'}/feeds/${filename}`,
              rel: 'self',
              type: 'application/rss+xml'
            }
          },
          item: rssItems
        }]
      };

      const xml = this.builder.buildObject(rssObject);
      const fs = require('fs');
      const path = require('path');
      
      const feedsDir = path.join(process.cwd(), 'public/feeds');
      if (!fs.existsSync(feedsDir)) {
        fs.mkdirSync(feedsDir, { recursive: true });
      }
      
      fs.writeFileSync(path.join(feedsDir, filename), xml);
      logger.info(`Generated RSS file: ${filename} with ${items.length} items`);
      
    } catch (error) {
      logger.error(`Error creating RSS file: ${filename}`, { error: error.message });
    }
  }

  async generateRedirectFeeds() {
    try {
      const allItems = await databaseManager.getFeedItems();
      const redirectItems = allItems.map(item => ({
        title: item.title,
        description: `Original content at: ${item.link}`,
        link: `https://www.goodoffers.theworkpc.com/?item_hash=${item.item_hash}`,
        guid: `redirect-${item.item_hash}`,
        pubDate: new Date(item.pub_date).toUTCString(),
        enclosure: item.image_url ? {
          $: {
            url: item.image_url,
            length: '0',
            type: 'image/jpeg'
          }
        } : undefined
      }));

      await this.createRSSFileFromItems(redirectItems, 'redirect-all.xml', 'All Offers (Redirect)', 'Redirect feed for all offers');
      
      logger.info('Generated redirect feeds');
    } catch (error) {
      logger.error('Error generating redirect feeds', { error: error.message });
    }
  }

  async createRSSFileFromItems(items, filename, title, description) {
    const rssItems = items.map(item => {
      const rssItem = {
        title: [item.title],
        description: [item.description],
        link: [item.link],
        guid: [item.guid],
        pubDate: [item.pubDate]
      };
      
      if (item.enclosure) {
        rssItem.enclosure = item.enclosure;
      }
      
      return rssItem;
    });

    const rssObject = {
      $: { 
        version: '2.0',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
      },
      channel: [{
        title: [title],
        description: [description],
        link: [config.app.baseUrl || 'https://www.goodoffers.theworkpc.com'],
        language: ['en-US'],
        lastBuildDate: [new Date().toUTCString()],
        generator: ['Advanced RSS Generator v2.0'],
        item: rssItems
      }]
    };

    const xml = this.builder.buildObject(rssObject);
    const fs = require('fs');
    const path = require('path');
    
    const feedsDir = path.join(process.cwd(), 'public/feeds');
    fs.writeFileSync(path.join(feedsDir, filename), xml);
  }
}

module.exports = new AdvancedFeedGenerator();