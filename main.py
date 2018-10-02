import xml.etree.ElementTree
import requests
from bs4 import BeautifulSoup, NavigableString

class Gipfel_Parser:
    root_url = ''
    catalog_url = ''
    items_url = set()
    category_url = set()
    sub_category_url = set()
    def __init__(self,root_url_,catalog_url_):
        self.root_url = root_url_
        self.catalog_url = catalog_url_

    def parse_catalog(self):
        par = {'p': 0}
        r = requests.get(self.catalog_url, params=par)
        soup = BeautifulSoup(r.text, 'html.parser')
        #self.categories_url = self.get_categories_url(soup)
        self.sub_category_url = self.get_subcategory_url(soup)
        #self.sub_category_url = self.get_subcategory_url()
        #for url in categories_url:
        #    self.parse_category(url)
    def get_subcategory_url(self,soup):
        subcategories_pages = soup.find_all('ul', {"class": "inner-menu"})
        for div in subcategories_pages:
            sub_sub = div.find_all('ul',{"class":"submenu"})
            if sub_sub:
                for sub_val in sub_sub:
                    self.sub_category_url.update(self.get_inner_url(sub_val, self.root_url))
            else: #TODO: add null item sub_sub
                self.sub_category_url.update(self.get_inner_url(div, self.root_url))
        return self.sub_category_url

    def get_inner_url(self,div,add = ''):
        test = set()
        test.add(str(add + div.a['href']))
        for value in div.contents:
            if isinstance(value, NavigableString):
                continue
            test.add(str(add+ value.a['href']))
        return test
    def parse_category(self, category_url):
        sub_cat_url = self.get_subcategory_url(category_url)
        for url in sub_cat_url:
            self.parse_subcategory(url)

    def parse_subcategory(self,subcat_url):
        par = {'p': 0}
        r = requests.get(subcat_url, params=par)
        soup = BeautifulSoup(r.text, 'html.parser')
        pages_url = self.get_pages_url(soup)
        pages_url.add(subcat_url)
        for page in pages_url:
            self.parse_page(page)

    def parse_page(self, page_url):
        self.get_items_url(page_url)

    def get_categories_url(self,soup):
        categories_pages = soup.find_all('li', {"class": "menu_top_catalog_li"})
        for div in categories_pages:
            self.category_url.add(self.get_inner_url(div,self.root_url))
        return self.category_url

    def get_pages_url(self,soup):
        div_pages = soup.find_all('div', {"class": "adm-navigation"})
        pages_url  = set()
        for div in div_pages:
            pages_url.add(self.get_inner_url(div,self.root_url))
        return pages_url

    def get_items_url(self,page_url):
        par = {'p': 0}
        r = requests.get(page_url, params=par)
        soup = BeautifulSoup(r.text, 'html.parser')
        curp_items = soup.find_all('div', {"class": "item_info TYPE_1"})
        for item in curp_items :
            self.items_url.add(self.get_inner_url(item,self.root_url)) #TODO: check non unique values






def get_items_url2(category_page_url,soup):
    curp_items = soup.find_all('div', {"class": "item_info TYPE_1"})
    result = get_inner_url(curp_items, 'https://gipfel.ru')
    return result


def get_inner_url(productDivs, add='https://gipfel.ru'):
    result = []
    for div in productDivs:
        result.append(str(add + div.a['href']))
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
    #parse_catolog("https://gipfel.ru/catalog/nabory-posudy/nabory-kastryul-i-kovshey/")
    test_class = Gipfel_Parser('https://gipfel.ru','https://gipfel.ru/catalog')
    #test_class.parse_subcategory("https://gipfel.ru/catalog/nabory-posudy/nabory-kastryul-i-kovshey/")
    test_class.parse_catalog()