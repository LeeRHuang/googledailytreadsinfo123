import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import os
from bs4 import BeautifulSoup

async def fetch_trends_playwright(geo='US', hours=168):
    """
    使用 Playwright 模拟浏览器访问 Google Trends 页面并抓取数据。
    """
    url = f"https://trends.google.com/trending?geo={geo}&hl=zh-CN&hours={hours}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": "http://127.0.0.1:7890"}
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        print(f"正在访问: {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5) 
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            trends = []
            rows = soup.find_all(attrs={'role': 'row'})
            for r in rows:
                kw_el = r.find(class_='mZ3RIc')
                tf_el = r.find(class_='qNpYPd')
                if kw_el:
                    kw = kw_el.get_text().strip()
                    tf = tf_el.get_text().strip() if tf_el else "N/A"
                    if kw and kw != "趋势":
                        trends.append({'keyword': kw, 'traffic': tf})
            
            await browser.close()
            if trends:
                seen = set()
                unique_trends = []
                for t in trends:
                    if t['keyword'] not in seen:
                        unique_trends.append(t)
                        seen.add(t['keyword'])
                trends = unique_trends
                pd.DataFrame(trends).to_csv('trends_automated_result.csv', index=False, encoding='utf-8-sig')
            return trends
        except Exception as e:
            print(f"抓取错误: {e}")
            await browser.close()
            return []

def analyze_and_report(trends):
    df = pd.DataFrame(trends)
    categories = {
        '科技/AI': ['ai', 'tech', 'app', 'update', 'software', 'chip', 'nvidia', 'chatgpt', 'openai', 'apple', 'ces'],
        '体育': ['vs', 'match', 'score', 'league', 'nfl', 'nba', 'mlb', 'football', 'basketball', 'soccer'],
        '金融/商业': ['stock', 'crypto', 'bitcoin', 'price', 'market', 'economy', 'fed', 'tax', 'irs'],
        '娱乐/生活': ['movie', 'series', 'netflix', 'singer', 'concert', 'award', 'game', 'star', 'show', 'year']
    }
    def get_category(kw):
        kw_l = kw.lower()
        for cat, kws in categories.items():
            if any(k in kw_l for k in kws): return cat
        return '其他'
    df['category'] = df['keyword'].apply(get_category)
    print("\n[趋势榜单]\n", df.head(15).to_string(index=False))
    return df

def generate_html_report(df):
    html = f"""<html><head><meta charset="utf-8"><style>
    body {{ font-family: sans-serif; padding: 20px; background: #f9f9f9; }}
    table {{ width: 100%; border-collapse: collapse; background: white; }}
    th, td {{ padding: 10px; border: 1px solid #eee; text-align: left; }}
    th {{ background: #4CAF50; color: white; }}
    </style></head><body><h1>Google Trends 2026-01-02</h1>
    <table><tr><th>关键词</th><th>搜索量</th><th>类别</th></tr>
    {"".join([f"<tr><td>{r.keyword}</td><td>{r.traffic}</td><td>{r.category}</td></tr>" for r in df.itertuples()])}
    </table></body></html>"""
    with open('trends_report.html', 'w', encoding='utf-8') as f: f.write(html)
    print("\nHTML报表已生成: trends_report.html")

async def main():
    trends = await fetch_trends_playwright()
    if trends:
        df = analyze_and_report(trends)
        generate_html_report(df)
        print("\n[建议方向]")
        print("- 新年/计划类工具\n- AI 代理应用\n- 垂直体育社区")

if __name__ == "__main__":
    asyncio.run(main())
