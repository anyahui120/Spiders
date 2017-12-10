# -*- coding: utf-8 -*-
"""
Scrapy settings for an_edx_crawl project

For simplicity, this file contains only settings considered important or
commonly used. You can find more settings consulting the documentation:

    http://doc.scrapy.org/en/latest/topics/settings.html
    http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
    http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
"""

# Main settings used by crawler: handle with care! --------
SPIDER_MODULES = ['an_edx_crawl.spiders']
NEWSPIDER_MODULE = 'an_edx_crawl.spiders'
DEFAULT_ITEM_CLASS = 'an_edx_crawl.items.A11yItem'

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'an_edx_crawl.pipelines.DuplicatesPipeline': 200,
    'an_edx_crawl.pipelines.DropDRFPipeline': 250,
    'an_edx_crawl.pipelines.Pa11yPipeline': 300,
}

# Other items you are likely to want to override ---------------
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
COOKIES_DEBUG = False
COOKIES_ENABLED = True
DEPTH_LIMIT = 6
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s]: %(message)s'
LOG_STDOUT = True

# Error catching
COMMANDS_MODULE = 'an_edx_crawl.commands'
FAILURE_CATEGORIES = [
    'log_count/ERROR',
]
