import asyncio
import sys
import os

# 将当前目录添加到路径以便导入 src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler import GoogleTrendsCrawler
from src.storage import CSVStorage
from src.aggregator import TrendsAggregator

async def run_pipeline():
    # 1. 抓取数据 (可以从环境变量读取代理)
    proxy = os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY')
    crawler = GoogleTrendsCrawler(proxy=proxy)
    print("开始抓取最新趋势...")
    trends = await crawler.fetch_trends()

    if not trends:
        print("未抓取到任何数据，流程终止。")
        return

    # 2. 存储数据
    storage = CSVStorage()
    storage.save_trends(trends)

    # 3. 聚合数据并生成前端 JSON
    aggregator = TrendsAggregator(storage)
    aggregator.aggregate_and_export()
    print("数据管道执行完成。")

if __name__ == "__main__":
    asyncio.run(run_pipeline())

