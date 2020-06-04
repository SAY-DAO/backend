import requests
from bs4 import BeautifulSoup

url = 'https://www.digikala.com/product/dkp-1821589/%D9%85%D8%AF%D8%A7%D8%AF-%D8%B1%D9%86%DA%AF%DB%8C-12-%D8%B1%D9%86%DA%AF-%D8%B3%D8%A8%D8%B2-%DA%A9%D8%AF-772'
result = requests.get(url)
c = result.content

soup = BeautifulSoup(c)
price_div = soup.find("div", "c-product__seller-price-raw js-price-value")
price_text = price_div.text.strip().replace(',', '')
price = int(price_text)
print(price)

