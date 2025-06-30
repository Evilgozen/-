# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import logging

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class TeachesSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ProxyMiddleware:
    """代理IP池中间件"""
    
    def __init__(self):
        # 代理IP池 - 这里使用一些免费代理作为示例
        # 实际使用时请替换为有效的代理IP
        self.proxy_list = [
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080', 
            'http://proxy3.example.com:8080',
            'http://127.0.0.1:7890',  # 本地代理示例
            # 可以添加更多代理IP
        ]
        self.logger = logging.getLogger(__name__)
    
    def process_request(self, request, spider):
        """为每个请求随机选择代理"""
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = proxy
            self.logger.info(f"使用代理: {proxy}")
        return None
    
    def process_exception(self, request, exception, spider):
        """代理失败时的处理"""
        proxy = request.meta.get('proxy')
        if proxy:
            self.logger.warning(f"代理 {proxy} 请求失败: {exception}")
            # 可以在这里实现代理失效处理逻辑
        return None


class KDLProxyMiddleware:
    """基于KDL API的高级代理中间件"""
    
    def __init__(self):
        from .proxy_extension import proxy_pool
        self.proxy_pool = proxy_pool
        self.logger = logging.getLogger(__name__)
        
        # 代理认证信息 - 请替换为你的实际信息
        self.username = "d2451979815"  # 替换为你的用户名
        self.password = "5849mpxx"  # 替换为你的密码
        
        # 是否使用用户名密码认证（私密代理/独享代理）
        self.use_auth = True  # 设置为False使用白名单认证
    
    def process_request(self, request, spider):
        """为每个请求随机选择代理"""
        if self.proxy_pool.proxy_list:
            proxy = random.choice(self.proxy_pool.proxy_list)
            
            if self.use_auth:
                # 用户名密码认证（私密代理/独享代理）
                proxy_url = f"http://{self.username}:{self.password}@{proxy}/"
            else:
                # 白名单认证（私密代理/独享代理）
                proxy_url = f"http://{proxy}/"
            
            request.meta['proxy'] = proxy_url
            self.logger.info(f"使用KDL代理: {proxy}")
        else:
            self.logger.warning("代理池为空，使用直连")
        
        return None
    
    def process_exception(self, request, exception, spider):
        """代理失败时的处理"""
        proxy = request.meta.get('proxy')
        if proxy:
            self.logger.warning(f"KDL代理请求失败: {exception}")
            # 可以在这里实现代理失效处理逻辑，比如从池中移除失效代理
        return None


class UserAgentMiddleware:
    """User-Agent轮换中间件"""
    
    def __init__(self):
        # User-Agent池
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.logger = logging.getLogger(__name__)
    
    def process_request(self, request, spider):
        """为每个请求随机选择User-Agent"""
        user_agent = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = user_agent
        self.logger.info(f"使用User-Agent: {user_agent[:50]}...")
        return None


class TeachesDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
