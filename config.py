from typing import List, Dict

# Constants
SCRAPED_FILENAME = "scraped_xml_feed.xml"
FINAL_MERGE_FILENAME = "final_merged_feed.xml"
GAMERPOWER_GAMES_FILENAME = "gamerpower_games.xml"
GAMERPOWER_LOOT_FILENAME = "gamerpower_loot.xml"
ITCHIO_GAMES_FILENAME = "itchio_games.xml"
IVY_LEAGUE_FILENAME = "ivy_league.xml"
REPO_NAME = "Offren/RSS-feed-to-Xpath"
MAX_RUNTIME_HOURS = 24
MAX_RETRIES = 3
RETRY_DELAY = 5

# User agents for rotation
USER_AGENTS: List[str] = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'
]

# GamerPower Feed Configurations
GAMERPOWER_GAMES_CONFIG = {
    'rss_url': 'https://politepol.com/fd/N6Zhs7rik02G.xml',
    'xpath': '/html/body/main/div/div[1]/div/section/article/div[1]/div[2]/a/@href',
    'image_xpath': '/html/body/main/div/div[1]/div/section/article/div[1]/div[1]/img/@src',
    'base_url': 'https://www.gamerpower.com',
    'max_entries': 10,
    'title': 'GamerPower Free Games',
    'description': 'Latest free games from GamerPower',
    'link': 'https://www.gamerpower.com',
    'filename': GAMERPOWER_GAMES_FILENAME
}

GAMERPOWER_LOOT_CONFIG = {
    'rss_url': 'https://politepol.com/fd/KC5aCOn6Jefb.xml',
    'xpath': '/html/body/main/div/div[1]/div/section/article/div[1]/div[2]/a/@href',
    'image_xpath': '/html/body/main/div/div[1]/div/section/article/div[1]/div[1]/img/@src',
    'base_url': 'https://www.gamerpower.com',
    'max_entries': 10,
    'title': 'GamerPower Free Loot',
    'description': 'Latest free DLC and in-game items from GamerPower',
    'link': 'https://www.gamerpower.com',
    'filename': GAMERPOWER_LOOT_FILENAME
}

# Itch.io Games Configuration
ITCHIO_GAMES_CONFIG = {
    'rss_url': 'https://feed.phenx.de/lootscraper_itch_game.xml',
    'base_url': 'https://itch.io',
    'max_entries': 10,
    'title': 'Itch.io Free Games',
    'description': 'Latest free games from Itch.io',
    'link': 'https://itch.io',
    'filename': ITCHIO_GAMES_FILENAME
}

# Ivy League Configuration
IVY_LEAGUE_CONFIG = {
    'rss_url': 'https://politepol.com/fd/X1jEZm46yBaM.xml',
    'base_url': 'https://www.classcentral.com',
    'max_entries': 10,
    'title': 'Ivy League Free Courses',
    'description': 'Latest free courses from Ivy League universities',
    'link': 'https://www.classcentral.com',
    'filename': IVY_LEAGUE_FILENAME
}

# Feed configurations
FEEDS: List[Dict] = [
    {
        'rss_url': "https://www.real.discount/rss",
        'xpath': "/html/body/div[2]/div/div[2]/div[3]/div[2]/a/@href",
        'image_xpath': "concat('https://img-c.udemycdn.com/course/750x422/', substring-after(substring-after(//img[@class='card-img-top']/@src, '/'), 'files/'))",
        'title': "Extracted real.discount Udemy Courses",
        'description': "A feed of 100% Off Udemy Courses from real.discount",
        'link': "https://www.real.discount/",
        'max_entries': 5
    },
    {
        'rss_url': "https://politepol.com/fd/XGgtG8T9dC1d.xml",
        'xpath': "/html/body/main/div[4]/div/div[3]/div/a/@href",
        'image_xpath': "substring-before(/html/body/main/div[4]/div/div[1]/img/@srcset,'480w')",
        'title': "Extracted scrollcoupons Udemy Courses",
        'description': "A feed of 100% Off Udemy Courses from scrollcoupons",
        'link': "https://www.scrollcoupons.com/",
        'max_entries': 5
    },
    {
        'rss_url': "https://politepol.com/fd/dDI6e3Dkp93h.xml",
        'xpath': "//a[contains(@class, 'btn_offer_block')]/@href",
        'image_xpath': "concat('https://img-c.udemycdn.com/course/750x422/',substring-after(substring-after(//figure[@class='top_featured_image']/img/@src,'/'),'/'))",
        'title': "Extracted onlinecourses.ooo Udemy Courses",
        'description': "A feed of 100% Off Udemy Courses from onlinecourses.ooo",
        'link': "https://onlinecourses.ooo/",
        'max_entries': 5
    },
    {
        'rss_url': "https://politepol.com/fd/WjDGnyuwpgJo.xml",
        'xpath': "/html/body/div[1]/div/div/div[1]/div/div/div[3]/div/a/@href",
        'image_xpath': "concat('https://img-c.udemycdn.com/course/240x135/',substring-after(substring-after(//div[@class='theme-img']/img/@src,'/'),'/'))",
        'title': "Extracted udemyfreebies.com Udemy Courses",
        'description': "A feed of 100% Off Udemy Courses from udemyfreebies.com",
        'link': "https://udemyfreebies.com/",
        'max_entries': 5
    },
    {
        'rss_url': "https://politepol.com/fd/k54boRNn7Kxi.xml",
        'xpath': "//*[@id='enroll']/a/@href",
        'image_xpath': "concat('https://img-c.udemycdn.com/course/480x270/',(substring-after(substring-after(/html/body/div/div[2]/div/div[2]/div[1]/div/img/@src,'/'),'/')))",
        'title': "Extracted infognu.com Udemy Courses",
        'description': "A feed of 100% Off Udemy Courses from infognu.com",
        'link': "https://infognu.com/",
        'max_entries': 5
    },
    {
        'rss_url': "https://politepol.com/fd/JxnPv53Bgo5Q.xml",
        'xpath': '//*[@id="msg_374549"]/a[1]/@href',
        'image_xpath': "concat('https://img-b.udemycdn.com/course/480x270/',(substring-after(substring-after(//*[@id=\"msg_375278\"]/img/@src,'/'),'/')))",
        'title': "Extracted Jucktion Forum Udemy Courses",
        'description': "A feed of 100% Off Udemy Courses from jucktion.com",
        'link': "https://jucktion.com/",
        'max_entries': 5
    }
]