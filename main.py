import xml.etree.ElementTree
import requests
from bs4 import BeautifulSoup
d=[]

def get_inner_url(productDivs, add =''):
    result = []
    for div in productDivs:
        result.append(str(add+div.a['href']))
    return result

def parse(url):
    smth =2

def get_items_url(catolog_page_url,soup):
    curp_items = soup.find_all('div', {"class": "item_info TYPE_1"})
    result = get_inner_url(curp_items, 'https://gipfel.ru')
    return result

def parse_catolog(url):
    par = {'p': 0}
    r = requests.get(url, params=par)
    soup = BeautifulSoup(r.text, 'html.parser')
    div_pages = soup.find_all('div', {"class": "adm-navigation"})
    add_url_pages = get_inner_url(div_pages,'https://gipfel.ru')
    add_url_pages.append(url)
    items_url = []
    for url in add_url_pages:
        items_url+=get_items_url(url,soup)

if __name__ == "__main__":
    parse_catolog("https://gipfel.ru/catalog/nabory-posudy/nabory-kastryul-i-kovshey/")
