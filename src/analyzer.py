import pandas as pd
from datetime import datetime

class TrendsAnalyzer:
    def __init__(self, storage):
        self.storage = storage

    def get_product_insights(self, df):
        """
        基于关键词分类和流量特征，提供产品方向建议
        """
        insights = []
        
        # 1. 识别爆发趋势 (对比最近两次抓取，或者简单的流量分级)
        # 这里使用简单的分类规则模拟
        
        categories = df.groupby('category').size().to_dict()
        
        if '科技/AI' in categories and categories['科技/AI'] > 0:
            tech_kws = df[df['category'] == '科技/AI'].head(3)['keyword'].tolist()
            insights.append({
                'title': 'AI/Tech 垂直工具',
                'context': f"检测到 {', '.join(tech_kws)} 等科技热点。",
                'suggestion': "可以开发针对这些特定 AI 模型或硬件的中文教程、提示词库或轻量级 API 包装工具。"
            })
            
        if '体育' in categories and categories['体育'] > 0:
            sports_kws = df[df['category'] == '体育'].head(3)['keyword'].tolist()
            insights.append({
                'title': '垂直赛事社交/数据看板',
                'context': f"体育赛事 {', '.join(sports_kws)} 流量巨大。",
                'suggestion': "考虑建立特定赛事的即时聊天室、比分预测工具或基于动态岛的实时比分提醒 APP。"
            })

        if '金融/商业' in categories and categories['金融/商业'] > 0:
            finance_kws = df[df['category'] == '金融/商业'].head(3)['keyword'].tolist()
            insights.append({
                'title': '金融行情预警/内容站',
                'context': f"市场关注 {', '.join(finance_kws)}。",
                'suggestion': "开发针对波动资产的极简价格预警工具，或编写深度行业解析报告以捕获 SEO 流量。"
            })

        # 通用：针对新年/季节性
        df_newyear = df[df['keyword'].str.contains('new year|新年|2026', case=False)]
        if not df_newyear.empty:
            insights.append({
                'title': '季节性效率/计划应用',
                'context': "新年计划相关关键词搜索量激增。",
                'suggestion': "开发带有社交对赌性质的‘新年目标达成’应用，通过押金模式强制用户坚持习惯。"
            })

        return insights

    def analyze(self, days=7):
        """
        执行完整分析流程
        """
        df = self.storage.load_recent_trends(days=days)
        if df.empty:
            return {
                'burst_trends': [],
                'product_insights': []
            }
        
        # 简单计算热度分 (基于 traffic_numeric 和出现频次)
        # 如果是 JSONL 加载的，会有 traffic_numeric
        if 'traffic_numeric' not in df.columns:
            df['traffic_numeric'] = 0 # 兜底
            
        # 聚合分析
        agg = df.groupby('keyword').agg({
            'traffic_numeric': 'max',
            'category': 'first',
            'timestamp': 'count' # 出现频次
        }).rename(columns={'timestamp': 'frequency'}).reset_index()
        
        # 计算权重得分
        agg['weight_score'] = agg['traffic_numeric'] * (1 + agg['frequency'] * 0.1)
        top_30 = agg.sort_values(by='weight_score', ascending=False).head(30)
        
        product_insights = self.get_product_insights(top_30)
        
        return {
            'last_analyzed': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product_insights': product_insights
        }

