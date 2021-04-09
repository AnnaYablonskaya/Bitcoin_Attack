import time

import os
import grequests
import requests
from bs4 import BeautifulSoup

start_time = time.time()

links = "https://www.blockchain.com/btc/unconfirmed-transactions"

req = requests.get(links)
soup = BeautifulSoup(req.text, 'xml')
# lists = soup.find_all('a', attrs={'class':"sc-1r996ns-0 fLwyDF sc-1tbyx6t-1 kCGMTY iklhnl-0 eEewhk d53qjk-0 ctEFcK"})
# refs = []
# for a in lists:
#     refs.append("https://www.blockchain.com/ru/" + a["href"])
# print(refs.__repr__())

lists = soup.find_all('div', attrs={'class':"sc-1g6z4xm-0 hXyplo"})
refs = []
for l in lists:
    ref = l.a["href"]
    refs.append("https://www.blockchain.com/ru/"+ref)

print("Got transaction")

reqs = (grequests.get(link) for link in refs)
resp = grequests.imap(reqs, grequests.Pool(10))

res = []
for r in resp:
   soup = BeautifulSoup(r.text, 'lxml')
   sops = soup.find_all('div', attrs={"class":"sc-19pxzmk-0 dVzTcW"})
   for s in sops:
       try:
           key = s.a["href"][16:]
           if(len(key)<35):
                res.append(key)
       except Exception:
           pass

print("Got keys")

res = list(set(res))

with open("list-addresses.txt", "w") as file:
    for r in res:
        file.write(r + "\n")

print("Wrote keys")

os.system("py balance_checker.py")

print("--- %s seconds ---" % (time.time() - start_time))
