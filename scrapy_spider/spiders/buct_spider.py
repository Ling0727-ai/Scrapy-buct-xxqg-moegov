from urllib.parse import urljoin

import scrapy


class BuctSpider(scrapy.Spider):
    name = "buct"
    allowed_domains = ["buct.edu.cn"]
    base_url = "https://news.buct.edu.cn"
    start_urls = ["https://news.buct.edu.cn/main.htm"]

    custom_settings = {
        "FEEDS": {
            "buct_output.csv": {
                "format": "csv",
                "encoding": "utf-8-sig",
                "fields": ["title", "conclusion", "url", "channelNames", "publishTime", "content"],
                "overwrite": True,
            }
        }
    }

    def parse(self, response):
        self.logger.info("Parsing %s", response.url)
        
        # 遍历每个 li 标签
        for li in response.css('div.content.container.clearFix li'):
            # title: div2>a>h3>span
            title = li.css('div a h3 span::text').get()
            
            # conclusion: div2>a>p
            conclusion = li.css('div a p::text').get()
            
            # url: div2>a 的 href
            href = li.css('div a::attr(href)').getall()[-2]
            url = urljoin(self.base_url, href) if href else None
            
            # channelNames: div2>div>span1>a 的 title 属性
            channel_names = li.css('div div span a::attr(title)').get()
            
            # 遇到精彩推荐或新媒体动态直接结束
            if channel_names in ["精彩推荐", "新媒体动态"]:
                break
            
            # publishTime: 包含<i>标签的span的文本
            publish_time = li.css('div div span:has(i)::text').get()
            
            # 发起请求获取详情页内容
            if url:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_detail,
                    meta={
                        "title": title.strip() if title else None,
                        "conclusion": conclusion.strip() if conclusion else None,
                        "url": url,
                        "channelNames": channel_names,
                        "publishTime": publish_time.strip() if publish_time else None,
                    }
                )
    
    def parse_detail(self, response):
        """解析详情页内容"""
        meta = response.meta
        
        # 提取 .wp_articlecontent 下所有 p 标签的内容
        p_contents = response.css('.wp_articlecontent p::text').getall()
        content = ' '.join(p.strip() for p in p_contents if p.strip())
        # 替换 \xa0 (不间断空格) 为普通空格
        content = content.replace('\xa0', ' ')
        
        yield {
            "title": meta.get("title"),
            "conclusion": meta.get("conclusion"),
            "url": meta.get("url"),
            "channelNames": meta.get("channelNames"),
            "publishTime": meta.get("publishTime"),
            "content": content,
        }