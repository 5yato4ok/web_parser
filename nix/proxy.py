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

    def load_proxy_list(self): #TODO: remove hardcoded proxy
        proxy_list = list()
        http_proxy = "http://Ko4s1F:VLawa7@193.7.196.160:8000"
        https_proxy = "https://Ko4s1F:VLawa7@193.7.196.160:8000"
        proxyDict = {
            "http": http_proxy,
            "https": https_proxy
        }
        proxy_list.append(proxyDict)
        http_proxy = "http://HPNoN8:aUsT3T@146.185.198.192:8000"
        https_proxy = "https://HPNoN8:aUsT3T@146.185.198.192:8000"
        proxyDict = {
            "http": http_proxy,
            "https": https_proxy
        }
        proxy_list.append(proxyDict)
        http_proxy = "http://HPNoN8:aUsT3T@146.185.199.123:8000"
        https_proxy = "https://HPNoN8:aUsT3T@146.185.199.123:8000"
        proxyDict = {
            "http": http_proxy,
            "https": https_proxy
        }
        proxy_list.append(proxyDict)
        return proxy_list

    def is_valid_https(self,proxy):
        try:
            proxy_ip = proxy['https']
            proxy_ip = proxy_ip.split("@")[1].split(":")[0]
            session = requests.session()
            session.proxies = proxy
            r = session.get("https://icanhazip.com/")
            ip_resp = r.text.replace("\n","")
            return ip_resp.encode('utf8') == proxy_ip
        except:
            return False

    def is_valid_http(self,proxy):
        try:
            proxy_ip=proxy['http']
            proxy_ip = proxy_ip.split("@")[1].split(":")[0]
            session = requests.session()
            session.proxies = proxy
            r = session.get("http://httpbin.org/ip")
            ip_resp = r.text.replace(u"{","").replace(u"}","").replace(u"origin","").\
                replace(u"\"","").replace(" ","").replace(u":","").replace("\n","")
            return ip_resp.encode('utf8') ==proxy_ip
        except:
            return False

    def is_valid(self,proxy):
        if not proxy:
            return False
        return self.is_valid_http(proxy) and self.is_valid_https(proxy)

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


