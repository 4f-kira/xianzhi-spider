import os
import sys
import getopt
import requests
import random
import re
import html2text
from bs4 import BeautifulSoup

useragents = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    ]

f=open("url_list.txt","w",encoding="utf-8")
    
    
def getUrl(url):
    headers = {
        'User-Agent': random.choice(useragents)
    }
    ## 获取网页主体
    html = requests.get(url,headers=headers).text
    ## bs4
    #soup = BeautifulSoup(html,'lxml')
    #title = soup.find_all('title')[0].get_text()
    #print(html)
    url_list = re.findall(r"\"topic-title\" href=\".+?\"", html)
    for i in url_list:
        rel_url="https://xz.aliyun.com"+i[20:].split('"')[0]
        print(rel_url)
        f.write(rel_url+"\n")
   # print(html)

#getUrl("https://xz.aliyun.com/?page=2")
 
for i in range(1,3):
    url="https://xz.aliyun.com/?page="+str(i)
    print(url)
    getUrl(url)
f.close()