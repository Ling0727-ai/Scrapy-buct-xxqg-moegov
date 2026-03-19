import json
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

import scrapy


class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["xuexi.cn"]
    tm = int(time.time())
    start_urls = [f"https://www.xuexi.cn/lgdata/1jscb6pu1n2.json?_st=29563600&js_v={tm}"]

    custom_settings = {
        "FEEDS": {
            "xxqg_output.csv": {
                "format": "csv",
                "encoding": "utf-8-sig",
                "fields": ["title", "publishTime", "showSource", "channelNames", "url", "item_id", "content"],
                "overwrite": True,
            }
        }
    }

    def parse(self, response):
        self.logger.info("Parsing %s", response.url)

        # 解析 JSON 数据
        data = json.loads(response.text)

        for item in data:
            # 检查发布时间是否在一周内
            if not self.is_within_one_week(item.get("publishTime")):
                self.logger.info(f"Reached data older than 1 week, stopping: {item.get('title')}")
                break  # 数据按时间排序，遇到超过一周的数据即可停止
            
            url = item.get("url")
            
            # 从URL中提取id或item_id参数
            item_id = self.extract_id_from_url(url)
            
            if item_id:
                # 构造新的详情页URL
                detail_url = f"https://boot-source.xuexi.cn/data/app/{item_id}.js?callback=callback&_st={self.tm}"
                
                # 发起新请求获取详细内容
                yield scrapy.Request(
                    url=detail_url,
                    callback=self.parse_detail,
                    meta={
                        "title": item.get("title"),
                        "publishTime": item.get("publishTime"),
                        "showSource": item.get("showSource"),
                        "channelNames": item.get("channelNames"),
                        "url": url,


                    }
                )
            else:
                # 如果没有提取到id，直接返回基础信息
                yield {
                    "title": item.get("title"),
                    "publishTime": item.get("publishTime"),
                    "showSource": item.get("showSource"),
                    "channelNames": item.get("channelNames"),
                    "url": url,
                    "item_id": None,
                    "content": None,
                }

    def extract_id_from_url(self, url):
        """从URL中提取id或item_id参数"""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # 优先获取id，如果没有则获取item_id
            item_id = query_params.get("id", [None])[0]
            if not item_id:
                item_id = query_params.get("item_id", [None])[0]
            
            return item_id
        except Exception as e:
            self.logger.error(f"Failed to extract id from URL {url}: {e}")
            return None

    def parse_detail(self, response):
        """解析详情页内容"""
        meta = response.meta
        content = None
        
        # 解析JSONP响应：callback({...})
        jsonp_text = response.text.strip()
        
        try:
            # 提取callback()中的JSON内容
            json_str = None
            
            # 匹配 callback(...) 格式
            if jsonp_text.startswith('callback(') and jsonp_text.endswith(')'):
                # 直接去掉 callback( 和最后的 )
                json_str = jsonp_text[9:-1]  # len('callback(') = 9
                self.logger.debug(f"Extracted JSON from callback for {response.url}")
            else:
                # 使用正则作为备选方案
                match = re.search(r'callback\((.*)\)\s*$', jsonp_text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                else:
                    # 尝试其他函数名
                    match = re.search(r'\w+\((.*)\)\s*$', jsonp_text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
            
            if json_str:
                # 尝试解析JSON
                try:
                    json_data = json.loads(json_str)
                    content = json_data.get("content", None)
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON parse error for {response.url}: {e}")
                    
                    # 尝试修复JSON格式问题
                    try:
                        # 移除控制字符
                        json_str_clean = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
                        json_data = json.loads(json_str_clean)
                        content = json_data.get("content", None)
                        self.logger.info(f"Parsed after removing control chars for {response.url}")
                    except Exception:
                        # 尝试使用正则直接提取content字段
                        content_match = re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', json_str, re.DOTALL)
                        if content_match:
                            raw_content = content_match.group(1)
                            try:
                                content = raw_content.encode('utf-8').decode('unicode_escape')
                                self.logger.info(f"Extracted content via regex for {response.url}")
                            except:
                                content = raw_content
            else:
                self.logger.warning(f"No callback() found in {response.url}")
        
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {e}")
        
        # 清理HTML标签
        if content:
            content = self.clean_html_tags(content)
        
        yield {
            "title": meta.get("title"),
            "publishTime": meta.get("publishTime"),
            "showSource": meta.get("showSource"),
            "channelNames": meta.get("channelNames"),
            "url": meta.get("url"),
            "item_id": meta.get("item_id"),
            "content": content,
        }

    def clean_html_tags(self, text):
        """清理HTML标签"""
        # 移除HTML标签
        clean_text = re.sub(r'<[^>]+>', '', text)
        # 移除多余的空白字符
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text
    
    def is_within_one_week(self, publish_time):
        """检查发布时间是否在一周内"""
        if not publish_time:
            # 如果没有发布时间，默认跳过
            return False
        
        try:
            # 尝试解析时间戳（毫秒）
            if isinstance(publish_time, (int, float)):
                # 如果是毫秒时间戳
                if publish_time > 10000000000:
                    pub_datetime = datetime.fromtimestamp(publish_time / 1000)
                else:
                    # 如果是秒时间戳
                    pub_datetime = datetime.fromtimestamp(publish_time)
            else:
                # 尝试解析字符串格式的时间
                # 常见格式：2024-01-01 12:00:00 或 2024-01-01T12:00:00
                pub_datetime = datetime.fromisoformat(str(publish_time).replace('Z', '+00:00'))
            
            # 计算一周前的时间
            one_week_ago = datetime.now() - timedelta(days=7)
            
            # 检查是否在一周内
            return pub_datetime >= one_week_ago
        except Exception as e:
            self.logger.warning(f"Failed to parse publish time {publish_time}: {e}")
            return False
