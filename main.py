from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run_all_spiders():
    """并行运行所有爬虫"""
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # 添加所有爬虫到同一个进程
    # 每个爬虫会使用自己的 custom_settings 中的 FEEDS 配置
    process.crawl("moegov")
    process.crawl("buct")
    process.crawl("example")

    # 启动所有爬虫并行运行
    process.start()


def run_single_spider(spider_name):
    """运行单个爬虫"""
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(spider_name)
    process.start()


def main():
    print("=" * 50)
    print("Scrapy Spider 入口")
    print("=" * 50)
    print("可用的爬虫:")
    print("  1. moegov - 教育部新闻")
    print("  2. buct   - 北化新闻")
    print("  3. xxqg   - 学习强国")
    print("  4. all    - 并行运行所有爬虫")
    print("-" * 50)

    choice = input("请选择要运行的爬虫 (输入名称或序号): ").strip()

    if choice in ("1", "moegov"):
        print("\n正在运行 moegov 爬虫...")
        run_single_spider("moegov")
    elif choice in ("2", "buct"):
        print("\n正在运行 buct 爬虫...")
        run_single_spider("buct")
    elif choice in ("3", "xxqg"):
        print("\n正在运行学习强国爬虫...")
        run_single_spider("example")
    elif choice in ("4", "all"):
        print("\n正在并行运行所有爬虫...")
        run_all_spiders()
    else:
        print(f"未知的爬虫: {choice}")


if __name__ == "__main__":
    main()
