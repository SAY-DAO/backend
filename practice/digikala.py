import requests
from bs4 import BeautifulSoup

url = 'https://www.digikala.com/product/dkp-788083/%D9%BE%D8%A7%DA%A9-%DA%A9%D9%86-%D8%AF%D9%84%DB%8C-%DA%A9%D8%AF-9367?utm_source=http%3a__say-company&utm_medium=AFFILIATE&utm_campaign=%d9%be%d8%a7%da%a9+%da%a9%d9%86+%d8%af%d9%84%db%8c+%da%a9%d8%af+9367&utm_content=SAY&affid=NmJjYWQxYzgtMDQ3NS00NTA2LTg2NDgtZmE0NjY0NjM1NGM1IyMjNDY3NTY%3d&exp=10&rexp=10'
result = requests.get(url)
c = result.content

soup = BeautifulSoup(c)
price_div = soup.find("div", "c-product__seller-price-raw js-price-value")
price_text = price_div.text.strip().replace(',', '')
price = int(price_text)
print(price)

