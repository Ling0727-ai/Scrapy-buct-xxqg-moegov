import csv
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


# moegov spider 的表头
MOEGOV_HEADERS = ["title", "url", "publishTime", "content"]


def run_moegov_spider():
    """运行 moegov spider 并保存为 CSV"""
    settings = get_project_settings()
    settings.set("FEEDS", {
        "moegov_output.csv": {
            "format": "csv",
            "encoding": "utf-8-sig",
            "fields": MOEGOV_HEADERS,
            "overwrite": True,
        }
    })

    process = CrawlerProcess(settings)
    process.crawl("moegov")
    process.start()


def main():
    print("=" * 50)
    print("Scrapy Spider 入口")
    print("=" * 50)
    print("可用的爬虫:")
    print("  1. moegov - 教育部新闻")
    print("-" * 50)

    choice = input("请选择要运行的爬虫 (输入名称或序号): ").strip()

    if choice in ("1", "moegov"):
        print("\n正在运行 moegov 爬虫...")
        run_moegov_spider()
    else:
        print(f"未知的爬虫: {choice}")


if __name__ == "__main__":
    main()
