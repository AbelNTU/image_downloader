# -*- coding: UTF-8 -*-
import re
import requests
import os
import urllib.parse
import threading
from multiprocessing.dummy import Pool
import time
from queue import Queue
from datetime import datetime
import downloader_setting

class downloader(object):
    str_table = {
        '_z2C$q': ':',
        '_z&e3B': '.',
        'AzdH3F': '/'
    }

    char_table = {
        'w': 'a',
        'k': 'b',
        'v': 'c',
        '1': 'd',
        'j': 'e',
        'u': 'f',
        '2': 'g',
        'i': 'h',
        't': 'i',
        '3': 'j',
        'h': 'k',
        's': 'l',
        '4': 'm',
        'g': 'n',
        '5': 'o',
        'r': 'p',
        'q': 'q',
        '6': 'r',
        'f': 's',
        'p': 't',
        '7': 'u',
        'e': 'v',
        'o': 'w',
        '8': '1',
        'd': '2',
        'n': '3',
        '9': '4',
        'c': '5',
        'm': '6',
        '0': '7',
        'b': '8',
        'l': '9',
        'a': '0'
    }
    char_table = {ord(key): ord(value) for key, value in char_table.items()}

    """docstring for downloader"""
    def __init__(self, word):
        super(downloader, self).__init__()
        self.word = word
        self.DIR = ''
        self.index = 1
        self.start_index = 1
        self.char_table = downloader.char_table
        self.str_table = downloader.str_table
        self.pool = Pool(30)
        self.imageURL = Queue()
        self.lock = threading.Lock()
        self.error = 0

    def decode(self, url):
        for key,value in self.str_table.items():
            url = url.replace(key,value)
        url = url.translate(self.char_table)
        return url

    def build_image_folder(self):
        DIR = os.getcwd()
        DIR = os.path.join(DIR,'image',self.word,'baidu')
        nowtime = datetime.now()
        print(nowtime,'正在建立圖片儲存資料夾')
        self.DIR = os.path.join(DIR,nowtime.strftime('%Y-%m-%d %H-%M-%S'))
        os.makedirs(self.DIR)

    def build_query_url(self):
        word = urllib.parse.quote(self.word)
        URL = r"http://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&st=-1&ic=0&word={word}&face=0&istype=2nc=1&pn={pn}&rn=60"
        URL_res = requests.session().get(URL.format(word=word,pn=0)).content.decode('utf-8')
        res_list = re.findall(r'"displayNum":(\d+),', URL_res)
        max_num = int(res_list[0]) if res_list else 0
        display_URLs = [URL.format(word=word,pn = i) for i in range(0,1000,60)]
        return display_URLs

    def revolveImageURL(self,display_url):
        time.sleep(0.5)
        try:
            res = requests.get(display_url,timeout=1.5)
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            self.MessageOutput('連線出問題，暫停')
            return
        imgUrls = re.findall(r'"objURL":"(.*?)"',res.text)
        if len(imgUrls) == 0:
            return
        orgURLs = [self.decode(imgUrl) for imgUrl in imgUrls]
        self.lock.acquire()
        self.imageURL.put(orgURLs)
        self.lock.release()
        nowtime = datetime.now()
        message = str(nowtime)+' 已解析出'+str(len(orgURLs))+'個網址'
        self.MessageOutput(message)
        del res

    def saveImage(self,imgURL):
        try:
            time.sleep(0.5)
            img_res = requests.get(imgURL,timeout=5)
            if str(img_res.status_code)[0] != '2':
                self.MessageOutput("download fail!!!："+imgURL+'\n status code:',img_res.status_code)
                self.error += 1
                return
        except Exception as e:
            self.MessageOutput("download fail!!!："+imgURL)
            self.error += 1
            return
        self.lock.acquire()
        index = self.index
        self.index += 1
        self.lock.release()
        filename = self.word+str(index)+'.jpg'
        f = open(os.path.join(self.DIR,filename),'wb')
        f.write(img_res.content)
        f.close
        nowtime = datetime.now()
        message = str(nowtime)+' 第'+str(index)+'張圖片下載完成'
        self.MessageOutput(message)
        del img_res

    def MessageOutput(self,message):
        self.lock.acquire()
        print(message)
        self.lock.release()

    def start_downloader(self):
        start_time = datetime.now()
        self.build_image_folder()
        urls = self.build_query_url()
        self.pool.map(self.revolveImageURL,urls)
        resolve_time = datetime.now()
        print('解析網址共花',resolve_time-start_time)
        while self.imageURL.qsize():
            url = self.imageURL.get()
            self.pool.map(self.saveImage,url)
        self.pool.close()
        self.pool.join()
        endtime = datetime.now()
        print('下載結束,共花了',endtime-resolve_time)
        print('共下載',self.index-self.start_index,'張圖片')
        print('共',self.error,'個圖片網址無法獲取')
        return self.index-1

if __name__ == '__main__':
    if downloader_setting.is_python3():
        search = input('關鍵字：')
    else:
        search = raw_input('關鍵字：')

    mydownloader = downloader(search)
    mydownloader.start_downloader()


