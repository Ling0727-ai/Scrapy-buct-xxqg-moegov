# Scrapy settings for scrapy_spider project

BOT_NAME = "scrapy_spider"

SPIDER_MODULES = ["scrapy_spider.spiders"]
NEWSPIDER_MODULE = "scrapy_spider.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 32

DOWNLOAD_DELAY = 0.5

# Crawl responsibly
COOKIES_ENABLED = False

TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

SPIDER_MIDDLEWARES = {
    "scrapy_spider.middlewares.ScrapySpiderSpiderMiddleware": 543,
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy_spider.middlewares.ScrapySpiderDownloaderMiddleware": 543,
}

EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
}

ITEM_PIPELINES = {
    "scrapy_spider.pipelines.ScrapySpiderPipeline": 300,
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

FEED_EXPORT_ENCODING = "utf-8-sig"
