import xml.etree.ElementTree
import requests
from bs4 import BeautifulSoup
d=[]

def get_inner_url(productDivs):
    result = []
    for div in productDivs:
        result.append(div.a['href'])
    return result

def parse(url):
    #for j in range(10):
    par = {'p': 0}
    r = requests.get(url, params=par)
    soup = BeautifulSoup(r.text, 'html.parser')
        #product = soup.find_all('h3')[i].get_text()
    url_all_set = soup.find_all('div',{"class":"adm-navigation"})
    all_items = soup.find_all('div',{"class":"item_info TYPE_1"})
    smth =2

if __name__ == "__main__":
    parse("https://gipfel.ru/catalog/nabory-posudy/nabory-kastryul-i-kovshey/")
