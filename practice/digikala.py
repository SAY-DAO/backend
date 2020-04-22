import requests
from bs4 import BeautifulSoup

url = 'https://www.digikala.com/product/dkp-168997/%D8%B4%D8%A7%D9%85%D9%BE%D9%88-%D8%A8%DA%86%D9%87-%D9%81%DB%8C%D8%B1%D9%88%D8%B2-%D9%85%D8%AF%D9%84-aloe-vera-%D8%AD%D8%AC%D9%85-500-%D9%85%DB%8C%D9%84%DB%8C-%D9%84%DB%8C%D8%AA%D8%B1'
result = requests.get(url)
c = result.content

soup = BeautifulSoup(c)
price_div = soup.find("div", "c-product__seller-price-raw js-price-value")
price_text = price_div.text.strip().replace(',', '')
price = int(price_text)
print(price)

