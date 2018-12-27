import requests
from bs4 import BeautifulSoup

class Proxy:
    proxy_list = set()
    max_counter = 1
    current_value = dict()
    current_counter = 0
    max_tries = 0

    def __init__(self,max_counter=1,max_tries=100):
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

    def load_proxy_list_from_file(self): #TODO: remove hardcoded proxy
        proxy_list = list()
        with open("proxy.txt","r") as plist:
            lines = plist.readlines()
            for line in lines:
                http_proxy = "http://"+line.replace("\n","")
                https_proxy = "https://"+line.replace("\n","")
                proxyDict = {
                    "http": http_proxy,
                    "https": https_proxy
                }
                proxy_list.append(proxyDict)
        return proxy_list

    def load_proxy_list(self):
        proxy_list = list()
        res = requests.get('https://www.proxynova.com/proxy-server-list/elite-proxies/',
                           headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(res.text,'html.parser')
        for items in soup.select("tbody tr"):
            values = items.select("td")
            if not len(values):
                continue
            ip = values[0].select("abbr")
            if not ip:
                continue
            ip = ip[0]['title']
            if not self.is_valid_ip(ip):
                continue
            port = values[1].get_text()
            port = filter(lambda x: x.isdigit(),port)
            proxy = ip+":"+port
            proxyDict = {"http": "http://"+proxy.encode('utf8'),
                         "https": "https://"+proxy.encode('utf8')
                         }
            proxy_list.append(proxyDict)
        return proxy_list

    def load_proxy_list3(self):
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
                proxyDict = {"https":  "https://"+proxy.encode('utf8'),
                             "http":  "http://"+proxy.encode('utf8') }
            else:
                continue
            proxy_list.append(proxyDict)
        return proxy_list

    def is_valid_https(self,proxy):
        try:
            proxy_ip = proxy['https']
            if "@" in proxy_ip:
                proxy_ip = proxy_ip.split("@")[1].split(":")[0]
            else:
                proxy_ip = proxy_ip.replace('https://', '').split(":")[0]
            session = requests.session()
            session.proxies = proxy
            r = session.get("https://icanhazip.com/")
            ip_resp = r.text.replace("\n","")
            val = ip_resp.encode('utf8') == proxy_ip
            return val
        except:
            return False

    def is_valid_http(self,proxy):
        try:
            proxy_ip=proxy['http']
            if "@" in proxy_ip:
                proxy_ip = proxy_ip.split("@")[1].split(":")[0]
            else:
                proxy_ip = proxy_ip.replace('http://','').split(":")[0]
            session = requests.session()
            session.proxies = proxy
            r = session.get("http://httpbin.org/ip")
            ip_resp = r.text.replace(u"{","").replace(u"}","").replace(u"origin","").\
                replace(u"\"","").replace(" ","").replace(u":","").replace("\n","")
            val = ip_resp.encode('utf8') ==proxy_ip
            return val
        except:
            return False

    def is_valid(self,proxy):
        if not proxy:
            return False
        return self.is_valid_http(proxy) and self.is_valid_https(proxy)


    def get_valid_proxy(self,Force=False):
        cur_try = 0
        if self.current_counter%self.max_counter == 0 or Force or not self.is_valid(self.current_value):
            while True:
                if not self.proxy_list:
                    self.proxy_list = self.load_proxy_list()
                proxy = self.proxy_list.pop()
                if not self.is_valid(proxy):
                    print("Proxy is not valid")
                    print(proxy)
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
            print("Current proxy counter" + str(self.current_counter))
        return self.current_value


