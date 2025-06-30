import scrapy
from ..items import TeachesItem
import json
from urllib.parse import urlencode, urljoin

class EncuSpider(scrapy.Spider):
    name = "encu"
    allowed_domains = ["faculty.ecnu.edu.cn"]
    start_url = "https://faculty.ecnu.edu.cn/_s2/flss/list.psp"
    ajax_url = "https://faculty.ecnu.edu.cn/_wp3services/generalQuery"
    base_url = "https://faculty.ecnu.edu.cn"
    now_page = 1

    # 完整的headers
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://faculty.ecnu.edu.cn",
        "Referer": "https://faculty.ecnu.edu.cn/_s2/flss/list.psp",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }

    def start_requests(self):
        # 第一步：访问主页获取cookie，使用session自动处理
        yield scrapy.Request(
            url=self.start_url,
            callback=self.make_api_request,
            headers={
                'User-Agent': self.headers['User-Agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9'
            },
            meta={'dont_cache': True}  # 确保获取最新的cookie
        )

    def make_api_request(self, response):
        # Scrapy会自动处理cookie，无需手动提取
        self.logger.info("已访问主页，开始发送API请求")
        
        # 构建form data
        form_data = {
            "pageIndex": str(self.now_page),
            "rows": "52",
            "conditions": '[{"field":"language","value":"1","judge":"="},{"field":"published","value":"1","judge":"="},{"orConditions":[{"field":"ownDepartment","value":"16","judge":"="},{"field":"exField3","value":"计算机科学与技术学院","judge":"="}]}]',
            "orders": '[{"field":"new","type":"desc"}]',
            "returnInfos": '[{"field":"title","name":"title"},{"field":"cnUrl","name":"cnUrl"},{"field":"post","name":"post"},{"field":"headerPic","name":"headerPic"},{"field":"department","name":"department"},{"field":"exField1","name":"exField1"},{"field":"exField2","name":"exField2"},{"field":"exField3","name":"exField3"}]',
            "articleType": "1",
            "level": "0",
            "pageEvent": "doSearchByPage"
        }
        
        # URL参数
        params = {"queryObj": "teacherHome"}
        
        # 构建完整URL
        full_url = f"{self.ajax_url}?{urlencode(params)}"
        
        # self.logger.info(f"发送请求到: {full_url}")
        
        # 发送POST请求
        yield scrapy.FormRequest(
            url=full_url,
            formdata=form_data,
            headers=self.headers,
            callback=self.parse_json,
            dont_filter=True
        )

    def parse_json(self, response):
        # 解析JSON响应
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"JSON解析失败: {response.text}")
            return
        
        # 提取需要的信息
        items = data.get('data', [])
        for item in items:
            # 创建基本的item信息
            basic_info = {
                'school_level':'中9',
                'school':'华东师范大学',
                'name': item.get('title', ''),
                'title': item.get('post', ''),
                'school_college': item.get('department', ''),
                'url': item.get('cnUrl', '')
            }
            
            # 构建详情页面URL
            detail_url = urljoin(self.base_url, item.get('cnUrl', ''))
            
            # self.logger.info(f"准备访问详情页面: {detail_url}")
            
            # 访问详情页面获取email和resh_dict
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                headers={
                    'User-Agent': self.headers['User-Agent'],
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9'
                },
                meta={'basic_info': basic_info},
                dont_filter=True
            )

        # 分页处理
        total_pages = data.get('pageCount', 0)
        if total_pages > self.now_page:
            self.now_page += 1
            
            # 构建下一页的form data
            form_data = {
                "pageIndex": str(self.now_page),
                "rows": "52",
                "conditions": '[{"field":"language","value":"1","judge":"="},{"field":"published","value":"1","judge":"="},{"orConditions":[{"field":"ownDepartment","value":"16","judge":"="},{"field":"exField3","value":"计算机科学与技术学院","judge":"="}]}]',
                "orders": '[{"field":"new","type":"desc"}]',
                "returnInfos": '[{"field":"title","name":"title"},{"field":"cnUrl","name":"cnUrl"},{"field":"post","name":"post"},{"field":"headerPic","name":"headerPic"},{"field":"department","name":"department"},{"field":"exField1","name":"exField1"},{"field":"exField2","name":"exField2"},{"field":"exField3","name":"exField3"}]',
                "articleType": "1",
                "level": "0",
                "pageEvent": "doSearchByPage"
            }
            
            params = {"queryObj": "teacherHome"}
            full_url = f"{self.ajax_url}?{urlencode(params)}"
            
            yield scrapy.FormRequest(
                url=full_url,
                formdata=form_data,
                headers=self.headers,
                callback=self.parse_json,
                dont_filter=True
            )

    def parse_detail(self, response):
        """解析教师详情页面，提取email和resh_dict信息"""
        basic_info = response.meta['basic_info']
        
        # 创建TeachesItem
        teachesItem = TeachesItem()
        teachesItem['school_level'] = basic_info['school_level']  # 添加这行
        teachesItem['school'] = basic_info['school']              # 添加这行
        teachesItem['name'] = basic_info['name']
        teachesItem['title'] = basic_info['title']
        teachesItem['school_college'] = basic_info['school_college']
        teachesItem['url'] = basic_info['url']
        
        # 提取email - 使用XPath
        email_xpath = '//*[@id="container-1"]/div/div/div[2]/div[1]/div/table/tbody/tr/td/div[1]/div[1]/div[2]/ul[2]/li[2]/span[2]/text()'
        email = response.xpath(email_xpath).get()
        if email:
            teachesItem['email'] = email.strip()
        else:
            # 如果XPath没有找到，尝试其他可能的选择器
            email_alt = response.css('span:contains("@")::text').get()
            teachesItem['email'] = email_alt.strip() if email_alt else ''
        
        # 修改后的resh_dict提取逻辑 - 使用兼容的选择器
        resh_dict = ''
        
        # 方法1：使用XPath直接查找包含"研究方向"的标题及其相关内容
        xpath_query = '//span[@class="title" and contains(text(), "研究方向")]/ancestor::div[contains(@class, "post")]//div[@class="con"]//text()'
        research_texts = response.xpath(xpath_query).getall()
        
        if research_texts:
            # 清理和合并文本
            clean_texts = [text.strip() for text in research_texts if text.strip()]
            resh_dict = ' '.join(clean_texts)
        
        # 方法2：如果方法1失败，尝试更宽泛的查找
        if not resh_dict:
            # 先找到包含"研究方向"的span元素
            title_elements = response.css('span.title')
            
            for title_element in title_elements:
                title_text = title_element.css('::text').get()
                if title_text and '研究方向' in title_text:
                    # 使用XPath找到该span的祖先post div
                    post_xpath = './ancestor::div[contains(@class, "post")]'
                    post_divs = title_element.xpath(post_xpath)
                    
                    if post_divs:
                        # 在该post div中查找con div的内容
                        con_texts = post_divs[0].css('div.con ::text').getall()
                        if con_texts:
                            clean_texts = [text.strip() for text in con_texts if text.strip()]
                            resh_dict = ' '.join(clean_texts)
                            break
        
        # 方法3：最后的备用方法 - 直接在maincon中查找
        if not resh_dict:
            maincon_divs = response.css('div.maincon')
            
            for maincon_div in maincon_divs:
                # 检查是否包含研究方向
                all_text = ' '.join(maincon_div.css('::text').getall())
                if '研究方向' in all_text:
                    # 提取con部分的内容
                    con_texts = maincon_div.css('div.con ::text').getall()
                    if con_texts:
                        clean_texts = [text.strip() for text in con_texts if text.strip()]
                        resh_dict = ' '.join(clean_texts)
                        break
        
        teachesItem['resh_dict'] = resh_dict
        
        # 添加调试日志
        # if resh_dict:
        #     self.logger.info(f"成功提取研究方向内容: {resh_dict[:100]}...")
        # else:
        #     self.logger.warning("未能提取到研究方向内容")
        
        yield teachesItem

                

