import requests
import xml.etree.ElementTree as ET

def fetch_trends(geo='US'):
    url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"

if __name__ == "__main__":
    content = fetch_trends()
    print(content[:1000])
