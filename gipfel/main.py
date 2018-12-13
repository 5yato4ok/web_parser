#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import sys
#from PyQt4 import QtCore,QtGui
import time
from bs4 import BeautifulSoup
from threading import Lock
from anytree import NodeMixin, RenderTree
import random
from proxy import Proxy
cur_text = "Result of parsing:\n"
mutex = Lock()

class Category(NodeMixin):
    def __init__(self, name, num, parent=None):
        super(Category, self).__init__()
        self.name = name
        self.parent = parent
        self.num = num


class Item:
    name = ''
    category = None
    category_parent = None
    article = ''
    picture = []
    old_price = 0
    new_price = 0
    description = ''
    vendor = ''
    param = dict()

#class Gipfel_Parser(QtCore.QObject):
class Gipfel_Parser():
    root_url = ''
    catalog_url = ''
    items_url = set()
    category_url = set()
    categories = Category(u'Каталог',1)
    cat_id = list()
    cat_list = list()
    sub_category_url = set()
    items = set()
    timeout = 5
    is_log = False
    proxy_mngr = None
    #textWritten = QtCore.pyqtSignal(str)

    def __init__(self,root_url_,catalog_url_,timeout_,is_log_,max_counter=1):
        #QtCore.QObject.__init__(self)
        self.root_url = root_url_
        self.catalog_url = catalog_url_
        self.timeout = timeout_
        self.is_log = is_log_
        self.cat_id.append(1)
        self.proxy_mngr = Proxy(max_counter)


    def parse_catalog(self):
        print("Parsing catalog")
        par = {'p': 0}
        r = requests.get(self.catalog_url, params=par,proxies = self.proxy_mngr.get_valid_proxy())
        soup = BeautifulSoup(r.text, 'html.parser')
        #self.sub_category_url = self.get_subcategory_url(soup)
        #for url in self.sub_category_url:
        #    self.parse_subcategory(url)
        self.parse_subcategory('https://gipfel.ru/catalog/posuda-dlya-prigotovleniya/skovorody-i-soteyniki/nabor-skovorod/')
        counter = 0
        for item in self.items_url:
            if counter%50 == 0:
                time.sleep(self.timeout)
            self.parse_item(item)
            counter += 1
            if self.is_log:
                text = "Current number of items parse:" + str(counter)
                if mutex.acquire():
                    global cur_text
                    cur_text += text
                    mutex.release()
                print(text)
                #self.textWritten.emit(text)

    def parse_item(self,url):
        #try:
            r = requests.get(url, allow_redirects=False,proxies = self.proxy_mngr.get_valid_proxy())
            if r.status_code != 200:
                return
            soup = BeautifulSoup(r.text, 'html.parser')
            item = Item()
            item.description = self.get_description(soup)
            item.param,item.vendor = self.get_charecteristics(soup)
            item.name,item.article = self.get_name_articulos(soup)
            #item.categories = self.get_categories(soup)
            item.category = self.get_categories(soup)
            item.picture = self.get_picture(soup)
            item.old_price,item.new_price = self.get_price(soup)
            self.items.add(item)
        #except:
        #    return


    def get_price(self,soup):
        cur_price = soup.find_all('div', {"class", "price eres"})
        current = 0
        for value in cur_price:
            current_s = value.get_text().replace(u"руб.","").replace(" ","")
            current = int(current_s)
        old_price = soup.find_all('div', {"class", "price discount"})
        old = 0
        for val in old_price:
            old_s = val.get_text().replace(u"руб.","").replace(" ","")
            old = int(old_s)
        return old, current

    def get_picture(self,soup):
        pictures = []
        divs = soup.find_all('div', {"class", "slides"})
        for value in divs:
            imgs = value.find_all('img')
            for pic in imgs:
                pictures.append(self.root_url+pic['src'])
        return pictures


    def get_categories(self,soup):
        category = None
        div = soup.find_all('div', {"class", "nav-page"})
        parent = None
        for val in div:
            bread = val.find_all("a")
            i = 0
            for crumb in bread:
                i += 1
                cat = crumb.get_text()
                if cat == u"Главная":
                    continue
                cur_node = parent
                found = False
                for pre,_,node in RenderTree(self.categories):
                    val = node.name.encode('utf8')
                    if cat.encode('utf8') == node.name.encode('utf8'):
                        parent = node
                        found = True
                if not found:
                    uniq = False
                    key = random.randint(2,500)
                    while not uniq:
                        if key in self.cat_id:
                            key = random.randint(2, 500)
                        else:
                            break
                    self.cat_id.append(key)
                    cur_node = Category(cat,key,parent)
                    self.cat_list.append(category)
                elif i == len(bread):
                    cur_node = parent
                category = cur_node
        return category

    def get_name_articulos(self,soup):
        name = ''
        articulos = 0
        name_artic = soup.find_all('div', {"class": "col-md-12"})
        for value in name_artic:
            name = list(value.find_all('h1'))[0].get_text()
            art = value.find_all('p',{"class":"good-vendor"})
            for a in art:
                href = list(a.find_all('a'))[0].get_text()
                articulos = href.replace(u"Артикул: ","")
        return name,articulos

    def get_description(self,soup):
        description = soup.find_all('div', {"class": "detail_text"})
        text = ""
        for value in description:
            text = value.get_text()
        return text

    def get_charecteristics(self,soup):
        charecteristics = soup.find_all('table', {"class": "props_list"})
        vendor = ''
        charac = dict()
        for val in charecteristics:
            tds_name = list(val.find_all('td', {"class": "char_name"}))
            tds = list(val.find_all('td', {"class": "char_value"}))
            for k in range(0,len(tds_name)):
                category = tds_name[k].contents[1].get_text()
                cat_val = tds[k].contents[1].get_text().replace('\t','').replace('\n','')
                if u'Бренд' == category:
                    vendor = cat_val
                    continue
                charac[category] = cat_val
        return charac,vendor



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
        r = requests.get(subcat_url, allow_redirects=False,proxies = self.proxy_mngr.get_valid_proxy())
        if r.status_code != 200:
            text = "Error connecting to page:"+ str(r.status_code)
            if mutex.acquire():
                global cur_text
                cur_text += text
                mutex.release()
            print(text)
            #self.textWritten.emit(text)
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        pages_url = self.get_pages_url(soup)
        pages_url.add(subcat_url)
        for page in pages_url:
            #need to check for additional pages
            self.parse_page(page)
        if self.is_log:
            text = "Current number of items url:"+str(len(self.items_url))
            if mutex.acquire():
                global cur_text
                cur_text += text
                mutex.release()
            print(text)
            #self.textWritten.emit(text)

    def parse_page(self, page_url):
        self.get_items_url(page_url)

    def get_categories_url(self,soup):
        categories_pages = soup.find_all('li', {"class": "menu_top_catalog_li"})
        for div in categories_pages:
            self.category_url.add(self.get_inner_url(div,self.root_url))
        return self.category_url

    def get_pages_url(self,soup):
        #start pages
        div_pages = soup.find_all('div', {"class": "nums"})
        pages_url  = set()
        for div in div_pages:
            pages_url.add(str(self.root_url + div.a['href']))
            links = div.find_all('a')
            pages_num = dict()
            for a in links:
                if a.has_attr('class'):
                    continue
                pages_num[int(a.contents[0])] = self.root_url+ str(a['href'])
            max_page = max(pages_num,key=int)
            for num in range(2,max_page+1):
                page_url = str(self.root_url + div.a['href'])
                page_url = page_url.replace(page_url[len(page_url)-1], str(num))
                pages_url.add(page_url)
        return pages_url

    def get_items_url(self,page_url):
        par = {'p': 0}
        try:
            r = requests.get(page_url, params=par,proxies = self.proxy_mngr.get_valid_proxy())
            soup = BeautifulSoup(r.text, 'html.parser')
            curp_items = soup.find_all('div', {"class": "main__goods--item main__goods--tile"})
            for item in curp_items :
                self.items_url.update(self.get_inner_url(item,self.root_url)) #TODO: check non unique values
        except:
            return

    def write_to_txml(self,file_name):
        result = open(file_name,'w')
        start = """<?xml version="1.0" encoding="UTF-8"?>\n
    <yml_catalog date="2017-02-05 17:22">\n"""
        result.write(start)
        tabs = "          "
        result.write(tabs + " <categories>\n")
        for pre,_,cat in RenderTree(self.categories):
            p_num = str(cat.num)
            if cat.parent:
                p_num = str(cat.parent.num)
            result.write(tabs + "     <category id = \"" + str(cat.num) + "\" parentId=\"" + p_num + "\">")
            result.write(cat.name.encode('utf8'))
            result.write("</category>\n")
        result.write(tabs + "</categories>\n")
        result.write("<offers>\n")
        for item in self.items:
            result.write(tabs+"<offer>\n")
            result.write(tabs+" <name>")
            item.name = item.name.replace('&','&amp;')
            result.write(item.name.encode('utf8'))
            result.write("</name>\n")
            result.write(tabs+" <article>"+item.article+"</article>\n")
            for pic in item.picture:
                result.write(tabs+" <picture>"+pic+"</picture>\n")
            result.write(tabs+" <oldprice>"+str(item.old_price)+"</oldprice>\n")
            result.write(tabs + " <price>" + str(item.new_price) + "</price>\n")
            result.write(tabs + " <categoryId>"+str(item.category.num)+"</categoryId>\n")
            result.write(tabs + " <description>")
            rmv_str ="Заказать товар можно на нашем сайте через корзину или по телефону"
            rmv_str2='8 (495) 222-15-158, (800) 700-34-88'
            form_descr = item.description.encode('utf8').replace(rmv_str,'').replace(rmv_str2,'').replace('&','&amp;')
            result.write(form_descr)
            result.write( "</description>\n")
            vendor = item.vendor.replace('&','&amp;')
            result.write(tabs + " <vendor>" + vendor + "</vendor>\n")
            for par in item.param:
                result.write(tabs+" <param name=\"")
                par_name = par.encode('utf8').replace('&','&amp;')
                result.write(par_name)
                result.write("\">")
                par_val = item.param[par].encode('utf8').replace('&','&amp;')
                result.write(par_val)
                result.write("</param>\n")
            result.write(tabs+"</offer>\n")
        end = """
        </offers>\n
    </yml_catalog>\n"""
        result.write(end)
        result.close()
        print("Finished writing results")
