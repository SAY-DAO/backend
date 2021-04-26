import requests
from bs4 import BeautifulSoup


url = 'https://www.digikala.com/product/dkp-1788820/%D8%AF%D8%B3%D8%AA%D9%85%D8%A7%D9%84-%DA%A9%D8%A7%D8%BA%D8%B0%DB%8C-200-%D8%A8%D8%B1%DA%AF-%D8%AF%D9%88%D8%B1%D8%AF%D8%A7%D9%86%D9%87-%D9%85%D8%AF%D9%84-ultra-soft-%D8%A8%D8%B3%D8%AA%D9%87-10-%D8%B9%D8%AF%D8%AF%DB%8C'

result = requests.get(url)
c = result.content

soup = BeautifulSoup(c)
price_div = soup.find("div", "c-product__seller-price-raw js-price-value")
price_text = price_div.text.strip().replace(',', '')
price = int(price_text)
print(price)
