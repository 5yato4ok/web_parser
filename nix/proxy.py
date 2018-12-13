import requests
from bs4 import BeautifulSoup

class Proxy:
    proxy_list = set()
    def __init__(self):
        self.proxy_list = self.load_proxy_list()
    def load_proxy_list(self):
        res = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(res.text)
        proxy_list = list()
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

    def get_valid_proxy(self):
        while True:
            if not self.proxy_list:
                self.proxy_list = self.load_proxy_list()
            proxy = self.proxy_list.pop()
            try:
                response = requests.get(url="https://ya.ru/", proxies=proxy)
                if response.status_code == 200:
                    return proxy
            except:
                continue