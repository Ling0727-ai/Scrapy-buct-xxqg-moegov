# Scrapy Spider

基于 Scrapy 的新闻爬虫项目，用于抓取教育部网站新闻内容。

## 项目结构

```
Scrapy-spider/
├── scrapy.cfg                 # Scrapy 配置文件
├── pyproject.toml             # Python 项目配置
├── main.py                    # 程序入口
├── scrapy_spider/
│   ├── __init__.py
│   ├── items.py               # 数据模型定义
│   ├── middlewares.py         # 中间件
│   ├── pipelines.py           # 数据管道
│   ├── settings.py            # 爬虫设置
│   └── spiders/
│       ├── __init__.py
│       └── moegov-spider.py   # 教育部新闻爬虫
└── README.md
```

## 环境要求

- Python >= 3.13
- uv (推荐) 或 pip

## 安装

```bash
# 使用 uv 安装依赖
uv sync

# 或使用 pip
pip install -r requirements.txt
```

## 使用方法

### 方式一：交互式运行

```bash
python main.py
# 或
uv run main.py
```

根据提示选择要运行的爬虫。

### 方式二：直接运行爬虫

```bash
# 运行 moegov 爬虫
scrapy crawl moegov

# 保存为 JSON 文件
scrapy crawl moegov -o output.json

# 保存为 CSV 文件
scrapy crawl moegov -o output.csv
```

### 方式三：使用 Scrapyd 部署运行

#### 1. 启动 Scrapyd 服务

```bash
scrapyd
# 服务默认运行在 http://localhost:6800
```

#### 2. 配置部署 (scrapy.cfg)

确保 `scrapy.cfg` 中已配置部署目标：

```ini
[deploy]
url = http://localhost:6800/
project = scrapy_spider
```

#### 3. 部署项目

```bash
scrapyd-deploy
```

#### 4. 运行爬虫

```bash
# 通过 API 运行爬虫
curl http://localhost:6800/schedule.json -d project=scrapy_spider -d spider=moegov

# 或访问 Web 界面
# 打开浏览器访问 http://localhost:6800
```

#### 5. 查看任务状态

```bash
# 查看项目列表
curl http://localhost:6800/listprojects.json

# 查看爬虫列表
curl http://localhost:6800/listspiders.json?project=scrapy_spider

# 查看任务状态
curl http://localhost:6800/listjobs.json?project=scrapy_spider
```

## 爬虫列表

### moegov - 教育部新闻爬虫

**目标网站**: http://www.moe.gov.cn/jyb_sy/sy_jyyw/

**输出字段**:

| 字段 | 说明 |
|------|------|
| title | 新闻标题 |
| url | 新闻链接 |
| publishTime | 发布时间 |
| content | 新闻正文内容 |

**输出文件**: `moegov_output.csv`

## 输出示例

```csv
title,url,publishTime,content
教育部新闻标题,http://www.moe.gov.cn/...,2024-01-01,新闻正文内容...
```

## 注意事项

1. 请遵守目标网站的 robots.txt 规则
2. 建议设置合理的下载延迟，避免对服务器造成压力
3. 输出文件使用 `utf-8-sig` 编码，确保 Excel 正确显示中文
