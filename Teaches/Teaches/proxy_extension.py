#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代理IP池扩展模块
基于KDL代理API的动态代理获取实现
"""

import time
import threading
import requests
import logging
from scrapy import signals


# 代理API配置 - 请替换为你的实际API信息
API_URL = 'https://dps.kdlapi.com/api/getdps/?secret_id=o8n0k8q1pyeqjf8dzvw1&signature=ofw1fvs1k4pxmekaz5cls41gfxr9b9xy&num=20&format=json&sep=1'

# 全局控制变量
proxy_refresh_running = True


class ProxyPool:
    """代理IP池类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 初始化时获取代理列表
        self._proxy_list = self._fetch_proxy_list()
        
    def _fetch_proxy_list(self):
        """从API获取代理列表"""
        try:
            response = requests.get(API_URL, timeout=10)
            data = response.json()
            if data.get('code') == 0:  # 成功
                proxy_list = data.get('data', {}).get('proxy_list', [])
                self.logger.info(f"成功获取 {len(proxy_list)} 个代理IP")
                return proxy_list
            else:
                self.logger.error(f"获取代理失败: {data.get('msg', '未知错误')}")
                return []
        except Exception as e:
            self.logger.error(f"获取代理异常: {e}")
            # 返回备用代理列表
            return [
                '127.0.0.1:7890',
            ]
    
    @property
    def proxy_list(self):
        """获取代理列表"""
        return self._proxy_list
    
    @proxy_list.setter
    def proxy_list(self, proxy_list):
        """设置代理列表"""
        self._proxy_list = proxy_list
        self.logger.info(f"代理列表已更新，当前有 {len(proxy_list)} 个代理")
    
    def refresh_proxy_list(self):
        """刷新代理列表"""
        new_list = self._fetch_proxy_list()
        if new_list:
            self.proxy_list = new_list
        return len(self._proxy_list)


# 全局代理池实例
proxy_pool = ProxyPool()


class ProxyExtension:
    """代理扩展类 - 定期刷新代理IP池"""
    
    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)
        self.refresh_interval = crawler.settings.getint('PROXY_REFRESH_INTERVAL', 240)  # 默认60秒
        
        # 绑定信号
        crawler.signals.connect(self.spider_opened, signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signals.spider_closed)
    
    @classmethod
    def from_crawler(cls, crawler):
        """从crawler创建扩展实例"""
        return cls(crawler)
    
    def spider_opened(self, spider):
        """爬虫开始时启动代理刷新线程"""
        self.logger.info("启动代理IP池刷新服务")
        self.refresh_thread = threading.Thread(target=self._refresh_proxy_loop)
        self.refresh_thread.daemon = True
        self.refresh_thread.start()
    
    def spider_closed(self, spider):
        """爬虫关闭时停止代理刷新"""
        global proxy_refresh_running
        proxy_refresh_running = False
        self.logger.info("代理IP池刷新服务已停止")
    
    def _refresh_proxy_loop(self):
        """代理刷新循环"""
        global proxy_refresh_running
        while proxy_refresh_running:
            try:
                count = proxy_pool.refresh_proxy_list()
                self.logger.info(f"代理池已刷新，当前代理数量: {count}")
            except Exception as e:
                self.logger.error(f"刷新代理池时发生错误: {e}")
            
            # 等待指定时间后再次刷新
            time.sleep(self.refresh_interval)