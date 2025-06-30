#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KDL代理测试爬虫
用于测试代理IP池和User-Agent轮换功能
"""

import scrapy


class KdlTestSpider(scrapy.Spider):
    """KDL代理测试爬虫"""
    name = "kdl_test"
    allowed_domains = ["dev.kdlapi.com", "httpbin.org"]
    
    def start_requests(self):
        """开始请求"""
        urls = [
            "https://dev.kdlapi.com/testproxy",  # KDL测试代理接口
            "http://httpbin.org/ip",  # 显示当前IP
            "http://httpbin.org/user-agent",  # 显示当前User-Agent
            "http://httpbin.org/headers",  # 显示所有请求头
        ]
        
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)
    
    def parse(self, response):
        """解析响应"""
        self.logger.info(f"请求URL: {response.url}")
        self.logger.info(f"响应状态: {response.status}")
        self.logger.info(f"响应内容: {response.text[:200]}...")  # 只显示前200个字符
        
        yield {
            'url': response.url,
            'status': response.status,
            'content': response.text,
            'proxy_used': response.meta.get('proxy', 'No proxy'),
            'user_agent': response.request.headers.get('User-Agent', b'').decode('utf-8')
        }