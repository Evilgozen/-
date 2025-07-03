import scrapy


class BuptSpider(scrapy.Spider):
    name = "bupt"
    allowed_domains = ["teacher.bupt.edu.cn"]
    start_urls = ["https://teacher.bupt.edu.cn"]

    def parse(self, response):
        pass
