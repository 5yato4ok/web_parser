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
        self.sub_category_url = self.get_subcategory_url(soup)
        for url in self.sub_category_url:
            self.parse_subcategory(url)

    def get_subcategory_url(self,soup):
        parent_blocks = soup.find_all('div', {"class": "submenu-block"})
        for div in parent_blocks:
            heads = div.find_all('div',{"class":"submenu-item submenu-item--more"})
            add_head = div.find_all('div',{"class":"submenu-item "})
            for value in add_head:
                heads.insert(len(heads),value)
            for head in heads:
                children = head.find_all('div', {"class": "submenu-item-body"})
                for child in children:
                   self.sub_category_url.update(self.get_inner_url(child,self.root_url))
                if not children:
                    self.sub_category_url.update(self.get_inner_url(head,self.root_url))

        return self.sub_category_url

    def get_inner_url(self,div,add = ''):
        test = set()
        test.add(str(add + div.a['href']))
        links = div.find_all('a href')
        for a in links:
            test.add(str(add + a['href']))
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
            #need to check for additional pages
            self.parse_page(page)

    def parse_page(self, page_url):
        self.get_items_url(page_url)

    def get_categories_url(self,soup):
        categories_pages = soup.find_all('li', {"class": "menu_top_catalog_li"})
        for div in categories_pages:
            self.category_url.add(self.get_inner_url(div,self.root_url))
        return self.category_url

    def get_pages_url(self,soup):
        div_pages = soup.find_all('div', {"class": "module-pagination"})
        pages_url  = set()
        for div in div_pages:
            pages_url.update(self.get_inner_url(div,self.root_url))
        return pages_url

    def get_items_url(self,page_url):
        par = {'p': 0}
        r = requests.get(page_url, params=par)
        soup = BeautifulSoup(r.text, 'html.parser')
        curp_items = soup.find_all('div', {"class": "main__goods--item main__goods--tile"})
        for item in curp_items :
            self.items_url.update(self.get_inner_url(item,self.root_url)) #TODO: check non unique values


if __name__ == "__main__":
    #parse_catolog("https://gipfel.ru/catalog/nabory-posudy/nabory-kastryul-i-kovshey/")
    test_class = Gipfel_Parser('https://gipfel.ru','https://gipfel.ru/catalog')
    #test_class.parse_subcategory("https://gipfel.ru/catalog/nabory-posudy/nabory-kastryul-i-kovshey/")
    test_class.parse_catalog()