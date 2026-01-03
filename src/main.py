import asyncio
import sys
import os

# 将当前目录添加到路径以便导入 src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crawler import GoogleTrendsCrawler
from src.storage import JSONLStorage
from src.aggregator import TrendsAggregator
from src.analyzer import TrendsAnalyzer

async def run_pipeline():
    # 1. 抓取数据
    proxy = os.getenv('HTTPS_PROXY') or os.getenv('HTTP_PROXY')
    crawler = GoogleTrendsCrawler(proxy=proxy)
    print("开始抓取最新趋势...")
    trends = await crawler.fetch_trends()

    if not trends:
        print("未抓取到任何数据，流程终止。")
        return

    # 2. 存储数据 (使用 JSONL 快照)
    storage = JSONLStorage()
    storage.save_trends(trends)

    # 3. 深度产品分析
    analyzer = TrendsAnalyzer(storage)
    analysis_results = analyzer.analyze(days=7)
    
    # 4. 聚合数据并生成前端 JSON (包含分析结果)
    aggregator = TrendsAggregator(storage)
    aggregator.aggregate_and_export(insights=analysis_results['product_insights'])
    
    print("数据管道执行完成。")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
