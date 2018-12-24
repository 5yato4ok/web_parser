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

    def is_valid_ip(self,s):
        a = s.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def load_proxy_list(self):
        proxy_list = list()
        res = requests.get('https://www.proxynova.com/proxy-server-list/elite-proxies/',
                           headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(res.text,'html.parser')
        http_proxy = "http://Ko4s1F:VLawa7@193.7.196.160:8000"
        https_proxy = "https://Ko4s1F:VLawa7@193.7.196.160:8000"
        proxyDict = {
            "http": http_proxy,
            "https": https_proxy
        }
        # response = requests.get(url="https://icanhazip.com/", proxies=proxyDict)
        proxy_list.append(proxyDict)
        return proxy_list

    def is_valid(self,proxy):
        if not proxy:
            return False
        try:
            # response = requests.get(url="https://ya.ru/", proxies=proxy)
            response = requests.get(url="https://icanhazip.com/", proxies=proxy)
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def get_valid_proxy(self):
        cur_try = 0
        if self.current_counter%self.max_counter == 0 or not self.is_valid(self.current_value):
            while True:
                if not self.proxy_list:
                    self.proxy_list = self.load_proxy_list()
                proxy = self.proxy_list.pop()
                if not self.is_valid(proxy):
                    print("Proxy is not valid")
                    cur_try += 1
                    if cur_try >= self.max_tries:
                        print("Exceeded all proxy tries")
                        self.current_value = {}
                        self.proxy_list = {}
                        break
                    continue
                else:
                    print("Proxy is valid")
                    print("Using proxy: "+str(proxy))
                    self.current_counter = 1
                    self.current_value = proxy
                    break
        else:
            self.current_counter += 1
        return self.current_value


