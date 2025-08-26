module.exports = {
  GAMERPOWER_LOOT_CONFIG: {
    id: 'gamerpower-loot',
    name: 'GamerPower DLC',
    rss_url: 'https://www.gamerpower.com/api/filter?platform=epic-games-store.steam.gog&type=loot&sort-by=date',
    base_url: 'https://gamerpower.com',
    max_entries: 50,
    feed_type: 'api', // This is an API, not RSS
    api_type: 'gamerpower'
  },
  
  GAMERPOWER_GAMES_CONFIG: {
    id: 'gamerpower-games',
    name: 'GamerPower Games',
    rss_url: 'https://www.gamerpower.com/api/filter?platform=epic-games-store.steam.gog&type=game&sort-by=date',
    base_url: 'https://gamerpower.com',
    max_entries: 50,
    feed_type: 'api',
    api_type: 'gamerpower'
  },

  ITCH_CONFIG: {
    id: 'itch-games',
    name: 'Itch.io Free Games',
    rss_url: 'https://itch.io/games/free.rss',
    base_url: 'https://itch.io',
    max_entries: 20,
    feed_type: 'rss'
  },

  CLASS_CENTRAL_CONFIG: {
    id: 'class-central',
    name: 'Class Central Ivy League',
    rss_url: 'https://www.classcentral.com/report/tag/ivy-league/feed/',
    base_url: 'https://classcentral.com',
    max_entries: 10,
    feed_type: 'rss_xpath',
    xpath: '//a[contains(@class, "course-link")]/@href',
    image_xpath: '//img[contains(@class, "course-image")]/@src'
  },

  UDEMY_SOURCES: [
    {
      id: 'real-discount',
      name: 'Real Discount Udemy',
      rss_url: 'https://www.real.discount/api-web/all-courses/?store=Udemy&category=All&free=1&page=1',
      base_url: 'https://real.discount',
      max_entries: 30,
      feed_type: 'api',
      api_type: 'real_discount'
    },
    {
      id: 'udemy-freebies',
      name: 'Udemy Freebies',
      rss_url: 'https://udemyfreebies.com/feed',
      base_url: 'https://udemyfreebies.com',
      max_entries: 20,
      feed_type: 'rss_xpath',
      xpath: '//div[@class="entry-content"]//a[contains(@href, "udemy.com")]/@href',
      image_xpath: '//div[@class="entry-featured-media"]//img/@src'
    }
  ]
};