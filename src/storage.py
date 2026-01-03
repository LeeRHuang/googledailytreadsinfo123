import pandas as pd
import os
from abc import ABC, abstractmethod
from datetime import datetime

class BaseStorage(ABC):
    @abstractmethod
    def save_trends(self, trends):
        pass

    @abstractmethod
    def load_recent_trends(self, days=7):
        pass

class CSVStorage(BaseStorage):
    def __init__(self, file_path='data/trends_master.csv'):
        self.file_path = file_path
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            df = pd.DataFrame(columns=['timestamp', 'keyword', 'traffic', 'category'])
            df.to_csv(self.file_path, index=False, encoding='utf-8-sig')

    def save_trends(self, trends):
        if not trends:
            return
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_data = []
        for t in trends:
            new_data.append({
                'timestamp': timestamp,
                'keyword': t['keyword'],
                'traffic': t['traffic'],
                'category': t.get('category', '其他')
            })
        
        df_new = pd.DataFrame(new_data)
        df_master = pd.read_csv(self.file_path)
        
        # 简单去重逻辑：如果同一个关键词在同一个小时内已经记录过，则跳过（可选）
        # 这里直接追加，后续聚合时处理
        df_combined = pd.concat([df_master, df_new], ignore_index=True)
        df_combined.to_csv(self.file_path, index=False, encoding='utf-8-sig')
        print(f"数据已保存至 {self.file_path}，新增 {len(new_data)} 条记录")

    def load_recent_trends(self, days=7):
        if not os.path.exists(self.file_path):
            return pd.DataFrame()
        
        df = pd.read_csv(self.file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = datetime.now() - pd.Timedelta(days=days)
        return df[df['timestamp'] > cutoff]

