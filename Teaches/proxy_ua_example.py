#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代理IP池和UA轮换使用示例

这个文件展示了如何在Scrapy项目中使用代理IP池和User-Agent轮换功能
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from Teaches.spiders.encu import EncuSpider


class ProxyTestSpider(scrapy.Spider):
    """测试代理和UA轮换的简单爬虫"""
    name = 'proxy_test'
    start_urls = [
        'http://httpbin.org/ip',  # 显示当前IP
        'http://httpbin.org/user-agent',  # 显示当前User-Agent
        'http://httpbin.org/headers',  # 显示所有请求头
    ]
    
    def parse(self, response):
        self.logger.info(f"响应URL: {response.url}")
        self.logger.info(f"响应内容: {response.text}")
        yield {
            'url': response.url,
            'content': response.text,
            'status': response.status
        }


def run_proxy_test():
    """运行代理测试爬虫"""
    process = CrawlerProcess({
        'USER_AGENT': 'proxy_test',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'Teaches.middlewares.ProxyMiddleware': 350,
            'Teaches.middlewares.UserAgentMiddleware': 400,
        },
        'LOG_LEVEL': 'INFO'
    })
    
    process.crawl(ProxyTestSpider)
    process.start()


if __name__ == '__main__':
    print("开始测试代理IP池和UA轮换功能...")
    print("注意: 请确保代理IP池中的代理地址是有效的")
    run_proxy_test()