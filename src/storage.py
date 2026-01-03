import pandas as pd
import os
import json
import uuid
import re
from abc import ABC, abstractmethod
from datetime import datetime

class BaseStorage(ABC):
    @abstractmethod
    def save_trends(self, trends):
        pass

    @abstractmethod
    def load_recent_trends(self, days=7):
        pass

class JSONLStorage(BaseStorage):
    def __init__(self, base_dir='data/snapshots'):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _parse_traffic(self, traffic_text):
        """将 '500万+ 次搜索' 解析为数字 5000000"""
        try:
            match = re.search(r'(\d+)([万|M|K]?)', traffic_text)
            if not match:
                return 0
            num = int(match.group(1))
            unit = match.group(2)
            if unit == '万':
                return num * 10000
            elif unit == 'M':
                return num * 1000000
            elif unit == 'K':
                return num * 1000
            return num
        except:
            return 0

    def save_trends(self, trends):
        if not trends:
            return
        
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        file_name = timestamp.strftime('%Y%m%d_%H%M%S.jsonl')
        file_path = os.path.join(self.base_dir, file_name)
        
        records = []
        for t in trends:
            records.append({
                'id': str(uuid.uuid4()),
                'timestamp': timestamp_str,
                'keyword': t['keyword'],
                'traffic_numeric': self._parse_traffic(t.get('traffic', '0')),
                'category': t.get('category', '其他'),
                'raw_traffic_text': t.get('traffic', 'N/A')
            })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"快照已保存至 {file_path}，新增 {len(records)} 条记录")
        return file_path

    def load_recent_trends(self, days=7):
        """从所有快照中加载最近 days 天的数据"""
        all_data = []
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)
        
        if not os.path.exists(self.base_dir):
            return pd.DataFrame()

        for file in sorted(os.listdir(self.base_dir), reverse=True):
            if file.endswith('.jsonl'):
                # 简单从文件名判断日期以优化性能
                try:
                    file_time = datetime.strptime(file.split('.')[0], '%Y%m%d_%H%M%S').timestamp()
                    if file_time < cutoff:
                        continue
                    
                    with open(os.path.join(self.base_dir, file), 'r', encoding='utf-8') as f:
                        for line in f:
                            all_data.append(json.loads(line))
                except:
                    continue
        
        if not all_data:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

class CSVStorage(BaseStorage):
    """保持兼容性的 CSV 存储，以后可能被弃用"""
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
        df_combined = pd.concat([df_master, df_new], ignore_index=True)
        df_combined.to_csv(self.file_path, index=False, encoding='utf-8-sig')
        print(f"数据已追加至 {self.file_path}")

    def load_recent_trends(self, days=7):
        if not os.path.exists(self.file_path):
            return pd.DataFrame()
        df = pd.read_csv(self.file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = datetime.now() - pd.Timedelta(days=days)
        return df[df['timestamp'] > cutoff]
