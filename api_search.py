import os
import sys
import requests
from bs4 import BeautifulSoup
import re
import json
import socket
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import ssl

class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


class ApiSearch():

    def __init__(self, q):
        self.q = q
        self.domain_pattern = re.compile(r"[%a-zA-Z0-9_\-\.]+{}".format(q))

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def parseCRTSH(self):

        CRT_URL = "https://crt.sh/"
        REQUEST_PARAM = "q"
        try:
            response = requests.get(CRT_URL, params={REQUEST_PARAM: "%.{}".format(self.q)}, verify=False, timeout=30)
            if response.status_code == 200:
                c = response.content
                soup = BeautifulSoup(c, "lxml")
                """
                For now we parse only second table since the first one is a title.
                Anyway, this behavior may be changed in future
                """
                tr = soup.find_all('tr')[1]
                domains = []
                index = 1
                for domain in list(set(self.domain_pattern.findall(str(tr)))):
                    if "%25" not in domain:
                        socket.setdefaulttimeout(2)
                        try:
                            # Here we remove the leading dot from a domain name, if present
                            domains.append({"id": index, "hostName": domain.lstrip("."), "hostIP": ""})
                            index += 1
                        except Exception as e:
                            # print("{}: {}".format(domain,e))
                            continue
                return domains
            else:
                return []
        except:
            e = sys.exc_info()
            print(e)
            return []


if __name__ == "__main__":
    target = sys.argv[1]
    f = ApiSearch(target)
    for domain in f.parseCRTSH():
        print(domain["hostName"])

