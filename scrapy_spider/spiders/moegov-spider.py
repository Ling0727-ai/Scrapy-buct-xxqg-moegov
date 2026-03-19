from urllib.parse import urljoin

import scrapy


class MoegovSpider(scrapy.Spider):
    name = "moegov"
    allowed_domains = ["moe.gov.cn"]
    base_url = "http://www.moe.gov.cn/"
    start_urls = ["http://www.moe.gov.cn/jyb_sy/sy_jyyw/"]

    custom_settings = {
        "FEEDS": {
            "moegov_output.csv": {
                "format": "csv",
                "encoding": "utf-8-sig",
                "fields": ["title", "url", "publishTime", "content"],
                "overwrite": True,
            }
        }
    }

    def parse(self, response):
        self.logger.info("Parsing %s", response.url)

        # 遍历每个 li 标签
        for li in response.css('div#wcmpagehtml ul li'):
            # title: a 里的 title 属性
            title = li.css('a::attr(title)').get()

            # url: a 的 href 属性
            href = li.css('a::attr(href)').get()[5:]  # 去掉前面的 '../../'
            url = urljoin(self.base_url, href) if href else None

            # publishTime: 包含<i>标签的span的文本
            publish_time = li.css('span::text').get()

            # 发起请求获取详情页内容
            if url:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_detail,
                    meta={
                        "title": title.strip() if title else None,
                        "url": url,
                        "publishTime": publish_time.strip() if publish_time else None,
                    }
                )

    def parse_detail(self, response):
        """解析详情页，获取文章内容"""
        # 获取所有 p 标签的文字内容
        paragraphs = response.css('.TRS_Editor p::text').getall()
        content = '\n'.join(p.strip() for p in paragraphs if p.strip())

        yield {
            "title": response.meta["title"],
            "url": response.meta["url"],
            "publishTime": response.meta["publishTime"],
            "content": content,
        }
