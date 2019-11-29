import os
import sys
import getopt
import requests
import random
import re
import html2text
from bs4 import BeautifulSoup
import time
from urllib.request import urlretrieve
from urllib import error
import sqlite3
import hashlib

useragents = [
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    ]

def sha1(s):
    return hashlib.sha1(s.encode()).hexdigest()

def getHtml(url):
    headers = {        
        'User-Agent': random.choice(useragents)
    }
    ## 获取网页主体
    html = requests.get(url,headers=headers).text
    soup = BeautifulSoup(html,'lxml')
    pwd = os.getcwd() # 获取当前的文件路径
    dirpath = pwd + '/xianzhi/'
    title = soup.find_all('title')[0].get_text()
    article = str(soup.find_all("div",class_="topic-content markdown-body")[0])
    #print(article)
    # 去除windows非法文件名字符
    title=title.replace('*','-').replace('|','-').replace(':','：').replace('"','\'').replace('/','-').replace('\\','-').replace('<','小于').replace('>','大于').replace('?','')
    title=title[:-7] # 去掉后面字符
    write2md(dirpath,title,article)
    #print(html)
    download_pic(title+'.md')
    print("[+] 本地转换完成 => "+ title+'.md')

def write2md(dirpath,title,article):
    ## 创建转换器
    h2md = html2text.HTML2Text()
    h2md.ignore_links = False
    h2md.mark_code = True # 添加代码段标记
    ## 转换文档
    article = h2md.handle(article)
    #print(article)
    ## 写入文件
    if not os.path.exists(dirpath):# 判断目录是否存在，不存在则创建新的目录
        os.makedirs(dirpath)
    # 创建md文件
    with open(dirpath+title+'.md','w',encoding="utf8") as f:
        f.write('# '+title+'\n')
        lines = article.splitlines()
        for line in lines:
            if line.endswith('-'):
                f.write(line)
            else:
                if line.startswith('#'):
                    line = line.replace('###','##')
                f.write(line+"\n")
    print("[+] MD下载完成 => "+ title+'.md')

def model_picture_download(model_picture_url, file_dir,text,new_pic):
    headers = {
        'User-Agent': random.choice(useragents)
    }
    model_picture_downloaded = False
    err_status = 0
    while model_picture_downloaded is False and err_status < 10:
        try:
            html_model_picture = requests.get(
                model_picture_url,headers=headers, timeout=1)
            with open(file_dir, 'wb') as file:
                file.write(html_model_picture.content)
                model_picture_downloaded = True
                text=text.replace(model_picture_url,"./img/"+new_pic)
                print('[*] 图片下载成功 '+ model_picture_url)
                return text
        except Exception as e:
            err_status += 1
            random_int = 4
            time.sleep(random_int)
            print(e)
            print('[!] 出现异常！睡眠 ' + str(random_int) + ' 秒')
            return text
        continue
    return text

def download_pic(filename):
    dirpath = os.getcwd()+ '/xianzhi/' # 获取当前的文件路径 
    f=open(dirpath+filename,"r+",encoding='utf-8')
    text=f.read()
    f.close()
    pic_list=re.findall(r"!\[\]\(.+?\)", text) #找到了所有文件
    for pic in pic_list:
        pic_url=pic[4:].split('\)')[0].replace(")","")
        # print(pic_url)
        #  https://xzfile.aliyuncs.com/media/upload/picture/20191103220108-6232f526-fe42-1.png
        # pic_name = pic_url.split('/')[-1]
        #pic_name = re.findall(r"picture/(.+?)\.png",pic_url)[0]
        #print(pic_name)
        new_pic= sha1(pic_url)+'.png'
        try:
            text=model_picture_download(pic_url, dirpath+'img/'+new_pic,text,new_pic)
            # print(pic_url)
            # print(new_pic)
            
        except error.URLError as e:
            raise e
        continue
        
    f=open(dirpath+filename,"w+",encoding='utf-8')
    f.write(text)
    f.close()


# getHtml("https://xz.aliyun.com/t/6729")

conn = sqlite3.connect('xianzhi.db')
cursor = conn.cursor()
file = open("url_list.txt") 

n = 0 # 1621
for line in file.readlines():
    line=line.strip('\n')
    cursor.execute('select * from markdown where url=?', (line,))# 执行查询语句:
    # if n < 1621:
    #     id = re.findall(r'\d{1,5}',line)[0]
    #     cursor.execute('insert into markdown (id, url) values (\'{}\', \'{}\')'.format(id,line))
    #     n+=1
    #     print(line)
    #     continue
    if len(cursor.fetchall()): # 获得查询结果集:
        print('[!]已下载 '+line)
        continue
    try:
        print(line)
        getHtml(line)
        id = re.findall(r'\d{1,5}',line)[0]
        cursor.execute('insert into markdown (id, url) values (\'{}\', \'{}\')'.format(id,line))
    except Exception as e:
        raise e


file.close()
cursor.close()
conn.commit()
conn.close()

