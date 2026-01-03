import pandas as pd
import json
import os
from datetime import datetime

class TrendsAggregator:
    def __init__(self, storage):
        self.storage = storage

    def categorize(self, kw):
        categories = {
            '科技/AI': ['ai', 'tech', 'app', 'update', 'software', 'chip', 'nvidia', 'chatgpt', 'openai', 'apple', 'ces'],
            '体育': ['vs', 'match', 'score', 'league', 'nfl', 'nba', 'mlb', 'football', 'basketball', 'soccer'],
            '金融/商业': ['stock', 'crypto', 'bitcoin', 'price', 'market', 'economy', 'fed', 'tax', 'irs'],
            '娱乐/生活': ['movie', 'series', 'netflix', 'singer', 'concert', 'award', 'game', 'star', 'show', 'year']
        }
        kw_l = kw.lower()
        for cat, kws in categories.items():
            if any(k in kw_l for k in kws):
                return cat
        return '其他'

    def aggregate_and_export(self, insights=None, output_path='web/data.json'):
        """
        聚合最近一周的数据并生成前端 JSON
        """
        df = self.storage.load_recent_trends(days=7)
        if df.empty:
            print("没有数据可聚合")
            return

        # 计算权重得分 (如果 JSONL 有 traffic_numeric 就用它)
        if 'traffic_numeric' in df.columns:
            def calculate_score(row):
                # 基础分来自流量，加成来自频次
                return row['traffic_numeric']
        else:
            def calculate_score(row):
                score = 1
                traffic_str = str(row.get('traffic', ''))
                if '500万+' in traffic_str: score += 10
                elif '200万+' in traffic_str: score += 5
                elif '100万+' in traffic_str: score += 3
                elif '50万+' in traffic_str: score += 2
                return score

        df['score'] = df.apply(calculate_score, axis=1)
        
        # 重新分类以确保使用最新的分类逻辑
        df['category'] = df['keyword'].apply(self.categorize)

        # 按关键词聚合
        agg = df.groupby('keyword').agg({
            'score': 'sum',
            'traffic_numeric': 'max' if 'traffic_numeric' in df.columns else 'count',
            'category': 'first',
            'timestamp': 'max'
        }).reset_index()

        # 将 timestamp 转为字符串以支持 JSON 序列化
        agg['timestamp'] = agg['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # 排序并取 Top 30
        top_trends = agg.sort_values(by='score', ascending=False).head(30)

        # 格式化为前端 JSON
        result = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'trends': top_trends.to_dict(orient='records'),
            'category_stats': agg['category'].value_counts().to_dict(),
            'insights': insights or []
        }

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"聚合数据已导出至 {output_path}")

