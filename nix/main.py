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
#from cachetools import cached, TTLCache  # 1 - let's import the "cached" decorator and the "TTLCache" object from cachetools
#cache = TTLCache(maxsize=5000, ttl=300000)


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
    price = 0
    description = ''
    vendor = ''
    param = dict()
    def valid(self):
        return self.name!='' and self.category and self.article != '' and self.picture

class Nix_Parser():
    root_url = ''
    catalog_url = ''
    items_url = set()
    category_url = set()
    categories = Category(u'Прайс-лист',1)
    cat_id = list()
    cat_list = list()
    sub_category_url = set()
    items = set()
    timeout = 5
    is_log = False


    def __init__(self,root_url_,catalog_url_,timeout_,is_log_):
        self.root_url = root_url_
        self.catalog_url = catalog_url_
        self.timeout = timeout_
        self.is_log = is_log_
        self.cat_id.append(1)


    #@cached(cache)
    def parse_catalog(self):
        print("Parsing catalog")
        par = {'p': 0}
        r = requests.get(self.catalog_url, params=par)
        soup = BeautifulSoup(r.text, 'html.parser')
        #self.sub_category_url = self.get_subcategory_url(soup)
        #for url in self.sub_category_url:
        #    self.parse_subcategory(url)

        #test parsing

        self.parse_subcategory('https://www.nix.ru/price/price_list.html?section=diskettes_disks_all')
        #self.parse_subcategory('https://www.nix.ru/price/price_list.html?section=mouses_all')
        counter = 0
        for item in self.items_url:
            if counter%30 == 0:
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
        try:
            r = requests.get(url, allow_redirects=False)
            if r.status_code != 200:
                return
            soup = BeautifulSoup(r.text, 'html.parser')
            item = Item()
            item.name = self.get_name(soup)
            item.article = self.get_articulos(soup)
            item.category = self.get_categories(soup)
            item.picture = self.get_picture(soup)
            item.price = self.get_price(soup)
            item.param,item.description ,item.vendor = self.get_charecteristics(soup)
            self.items.add(item)
        except:
            time.sleep(self.timeout*3)
            text = "Error in url:"+url+"\n"
            cur_text += text
            return


    def get_price(self,soup):
        cur_price = soup.find_all('div', {"class", "price"})
        current = 0
        for value in cur_price:
            price = list(value.find_all('span'))[0].get_text()
            price = ''.join(price.split())
            price = price.replace(u"руб.","")
            current = int(price)
        return current

    def get_picture(self,soup):
        pictures = []
        divs = soup.find_all('div', {"class", "carousel-content"})
        for value in divs:
            imgs = value.find_all('a')
            for pic in imgs:
                pictures.append(pic['href'])
        return pictures

    def get_categories(self,soup):
        category = None
        #div = soup.find('ul', {'id', "goods_crumbs"})
        div = soup.find_all(id="goods_crumbs")
        name = self.get_name(soup)
        parent = None
        for val in div:
            bread = val.find_all("span")
            i = 0
            for crumb in bread:
                i += 1
                cat = crumb.get_text()
                if cat == name:
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
                    self.cat_list.append(cur_node)
                elif i == len(bread):
                    cur_node = parent
                category = cur_node
        return category

    def get_name(self,soup):
        name = ''
        block = soup.find_all('h1', {"class": "big"})
        for val in block:
            name = val.get_text()
        return name

    def get_articulos(self,soup):
        articulos = ''
        block = soup.find_all('div', {"class": "goods_compare"})
        for value in block:
            articulos = list(value.find_all('input'))[0]['value']
        return articulos

    def get_charecteristics(self,soup):
        categories =  list(soup.find_all(id=lambda value: value and value.startswith("tds") and not value.startswith("tdsa")))
        cat_val = list(soup.find_all(id=lambda value2: value2 and value2.startswith("tdsa")))
        vendor = ''
        charac = dict()
        desc = ''
        for i in range(0,len(categories)):
            val_s = cat_val[i].contents[0]
            category = categories[i]
            if isinstance(val_s, basestring):
                val_s = val_s.replace('\t', '').replace('\n', '').rstrip()
            else:
                smth=2
                continue
            category = category.get_text().replace(u"(измерено в НИКСе)", "")
            if u'Производитель' == category:
                vendor = val_s
                continue
            if u'Описание' == category:
                desc = val_s
                continue
            charac[category] = val_s
        return charac,vendor,desc

    def get_subcategory_url(self,soup):
        parent_blocks = soup.find_all('li', {"class": "e"})
        for div in parent_blocks:
            self.sub_category_url.update(self.get_inner_url(div,self.root_url))
        return self.sub_category_url

    def get_inner_url(self,div,add = ''):
        test = set()
        test.add(str(add + div.a['href']))
        links = div.find_all('a href')
        for a in links:
            test.add(str(add + a['href']))
        return test

    def parse_subcategory(self,subcat_url):
        r = requests.get(subcat_url, allow_redirects=False)
        if r.status_code != 200:
            text = "Error connecting to page:"+ str(r.status_code)
            if mutex.acquire():
                global cur_text
                cur_text += text
                mutex.release()
            print(text)
            #self.textWritten.emit(text)
            return
        self.get_items_url(subcat_url)
        if self.is_log:
            text = "Current number of items url:"+str(len(self.items_url))
            if mutex.acquire():
                global cur_text
                cur_text += text
                mutex.release()
            print(text)
            #self.textWritten.emit(text)

    def get_page_params(self,page_url):
        par = {'p': 0}
        r = requests.get(page_url, allow_redirects=False)
        if r.status_code != 200:
            return
        soup = BeautifulSoup(r.text, 'html.parser')
        inp = soup.find_all(type='hidden')
        t_g_id = soup.find('input',{'name',u'g_id'})
        fn = 0
        c_id = 0
        g_id = 0
        store = 'msk-0_1721_1'
        sys_all = 0
        sort = ''
        page = 'all'
        thumbnail_view = 2
        command='get_goods'
        for val in inp:
            if u'name' not in val.attrs:
                continue
            if val[u'name'] == 'g_id':
                g_id = val['value']
            elif val[u'name'] == 'fn':
                fn = val['value']
            elif val[u'name'] == 'c_id':
                c_id = val['value']
            elif val[u'name'] == 'store':
                store = val['value']
            elif val[u'name'] == 'sys_all':
                sys_all = val['value']
            elif val[u'name'] == 'sort':
                sort = val['value']
            elif val[u'name'] == 'page':
                page = val['value']
            elif val[u'name'] == 'def_sort':
                sort = val['value'].replace('+',"%")
            elif val[u'name'] == 'page':
                page = val['value']
            elif val[u'name'] == 'thumbnail_view':
                thumbnail_view = val['value']
        data = {
            'fn':fn,
            'c_id':c_id,
            'g_id':g_id,
            'store':store,
            'sys_all':sys_all,
            'sort':sort,
            'page': page,
            'thumbnail_view':thumbnail_view,
            'command':command
        }
        return data


    def load_full_list(self,page_url):
        data = self.get_page_params(page_url)
        r = requests.post('https://www.nix.ru/lib/fast_search.php',data=data)
        if r.status_code!=200:
            return None
        return r

    def get_items_url(self,page_url):
        r = self.load_full_list(page_url)
        if r:
            soup = BeautifulSoup(r.text, 'html.parser')
            curp_items = soup.find_all('a', {"class": "t"})
            for item in curp_items:
                url = str(self.root_url+item['href'])
                url = url.replace('\\/','/')
                self.items_url.add(url)


    def write_to_txml(self,file_name):
        result = open(file_name, 'w')
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
            try:
                if not item.valid():
                    continue
                result.write(tabs+"<offer>\n")
                result.write(tabs+" <name>")
                item.name = item.name.replace('&','&amp;')
                result.write(item.name.encode('utf8'))
                result.write("</name>\n")
                result.write(tabs+" <article>"+item.article+"</article>\n")
                for pic in item.picture:
                    result.write(tabs+" <picture>"+pic.encode('utf8').replace('&','&amp;')+"</picture>\n")
                result.write(tabs + " <price>" + str(item.price) + "</price>\n")
                result.write(tabs + " <categoryId>"+str(item.category.num)+"</categoryId>\n")
                if item.description!='':
                    result.write(tabs + " <description>")
                    form_descr = item.description.encode('utf8').replace('&','&amp;')
                    result.write(form_descr)
                    result.write( "</description>\n")
                if item.vendor!='':
                    vendor = item.vendor.replace('&','&amp;')
                    result.write(tabs + " <vendor>" + vendor.encode('utf8') + "</vendor>\n")
                for par in item.param:
                    result.write(tabs+" <param name=\"")
                    par_name = par.encode('utf8').replace('&','&amp;')
                    result.write(par_name)
                    result.write("\">")
                    par_val = item.param[par].encode('utf8').replace('&','&amp;')
                    result.write(par_val)
                    result.write("</param>\n")
                result.write(tabs+"</offer>\n")
            except:
                continue
        end = """
        </offers>\n
    </yml_catalog>\n"""
        result.write(end)
        result.close()
        print("Finished writing results")
