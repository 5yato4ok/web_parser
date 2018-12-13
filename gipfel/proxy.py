import requests
from bs4 import BeautifulSoup

class Proxy:
    proxy_list = set()
    max_counter = 1
    current_value = dict()
    current_counter = 0
    max_tries = 0

    def __init__(self,max_counter=1,max_tries=1000):
        self.proxy_list = self.load_proxy_list()
        self.max_counter = max_counter
        self.max_tries = max_tries

    def load_proxy_list(self):
        proxy_list = list()
        res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(res.text,'html.parser')
        for items in soup.select("tbody tr"):
            https = ""
            for item in items.select("td")[6]:
                https = str(item)
            proxy = ':'.join([item.text for item in items.select("td")[:2]])
            proxyDict = {}
            if "yes" in https:
                proxyDict = {"https": proxy}
            else:
                proxyDict = {"http": proxy}
            proxy_list.append(proxyDict)
        return proxy_list

    def is_valid(self,proxy):
        if not proxy:
            return False
        try:
            response = requests.get(url="https://ya.ru/", proxies=proxy)
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def get_valid_proxy(self):
        cur_try = 0
        if self.current_counter%self.max_counter == 0 and not self.is_valid(self.current_value):
            while True:
                if not self.proxy_list:
                    self.proxy_list = self.load_proxy_list()
                proxy = self.proxy_list.pop()
                if not self.is_valid(proxy):
                    cur_try += 1
                    if cur_try >= self.max_tries:
                        self.current_value = {}
                        break
                    continue
                else:
                    self.current_counter = 1
                    self.current_value = proxy
                    break
        else:
            self.current_counter += 1
        return self.current_value


