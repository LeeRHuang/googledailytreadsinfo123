import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import time

class GoogleTrendsCrawler:
    def __init__(self, geo='US', hours=168, proxy=None):
        self.url = f"https://trends.google.com/trending?geo={geo}&hl=zh-CN&hours={hours}"
        self.proxy = proxy

    async def fetch_trends(self):
        """
        使用 Playwright 抓取 Google Trends 数据
        """
        async with async_playwright() as p:
            launch_args = {
                "headless": True
            }
            if self.proxy:
                launch_args["proxy"] = {"server": self.proxy}

            browser = await p.chromium.launch(**launch_args)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            print(f"正在访问: {self.url}")
            try:
                await page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(5) 
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                trends = []
                rows = soup.find_all(attrs={'role': 'row'})
                
                for r in rows:
                    try:
                        kw_el = r.find(class_='mZ3RIc')
                        tf_el = r.find(class_='qNpYPd')
                        
                        if kw_el:
                            kw = kw_el.get_text().strip()
                            tf = tf_el.get_text().strip() if tf_el else "N/A"
                            
                            if kw and kw != "趋势":
                                trends.append({
                                    'keyword': kw,
                                    'traffic': tf
                                })
                    except:
                        continue
                
                await browser.close()
                return trends
            except Exception as e:
                print(f"抓取错误: {e}")
                await browser.close()
                return []

