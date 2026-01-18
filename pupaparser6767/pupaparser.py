import requests
from bs4 import BeautifulSoup
import re
from collections import Counter

def get_price_pro(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    
    price = None

    title_element = soup.find('h4', "css-1au435n")
    if title_element:
        title = title_element.text.strip()
    else:
        title = "Назва не знайдена"

    found_prices = []
    
    elements = soup.find_all('div')
    for el in elements:
        text = el.text.strip()
        if "zł" in text and len(text) < 30:
            match = re.search(r'([\d\s,.]+)\s?zł', text)
            if match:
                price_str = match.group(1).strip()
                price_str = price_str.replace(' ', '').replace('\xa0', '')
                price_str = price_str.replace(',', '.')
                
                try:
                    price = float(price_str)
                    found_prices.append(price)
                except ValueError:
                    continue

    if found_prices:    
        data = Counter(found_prices)
        most_frequent_price = data.most_common(1)[0][0]
        return title, most_frequent_price
    else:
        return title, None