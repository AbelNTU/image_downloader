# -*- coding: UTF-8 -*-
import requests
import time
from bs4 import BeautifulSoup
import json
import urllib.parse
import os
import threading
from queue import Queue
from multiprocessing.dummy import Pool
from datetime import datetime
import downloader_setting

class downloader(object):
    """docstring for downloader"""
    def __init__(self, word):
        super(downloader, self).__init__()
        self.word = word
        self.DIR = ''
        self.index = 1
        self.start_index = 1
        self.pool = Pool(30)
        self.imageURL = Queue()
        self.lock = threading.Lock()
        self.imageError = 0
        self.header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8'}
        self.iscopyright = False

    def build_image_folder(self):
        DIR = os.getcwd()
        DIR = os.path.join(DIR,'image',self.word,'Bing')
        nowtime = datetime.now()
        print(nowtime,'正在建立圖片儲存資料夾')
        self.DIR = os.path.join(DIR,nowtime.strftime('%Y-%m-%d %H-%M-%S'))
        os.makedirs(self.DIR)

    def MessageOutput(self,message):
        self.lock.acquire()
        print(message)
        self.lock.release()

    def build_query_url(self):
        word = urllib.parse.quote(self.word)
        urlform = 'https://www.bing.com/images/async?q={word}&first={num}&count=35&relp=35&lostate=r&mmasync=1&IG=7E936964CEB741FFB2E0732236A95498&SFX=2&iid=images.5612'
        '''
        if self.iscopyright:
            urlform = 'https://www.bing.com/images/async?q={word}&first={num}&count=35&relp=35&qft=+filterui%3alicense-L2_L3_L4&lostate=r&mmasync=1&IG=7E936964CEB741FFB2E0732236A95498&SFX=2&iid=images.5612'
        else :
            urlform = 'https://www.bing.com/images/async?q={word}&first={num}&count=35&relp=35&lostate=r&mmasync=1&IG=7E936964CEB741FFB2E0732236A95498&SFX=2&iid=images.5612'
        '''
        Urls = [urlform.format(word = word,num = i) for i in range(0,1000,36)]
        return Urls

    def resolve_imgURL(self,query_url):
        time.sleep(0.1)
        try:
            req = requests.get(query_url,headers=self.header)
        except Exception as e:
            nowtime = datetime.now()
            message = str(nowtime)+' 連線出錯'
            self.MessageOutput(message)
            return
        html = BeautifulSoup(req.text,'html.parser')
        alltag = html.find_all('a','iusc')
        imgURLs = []
        for a in alltag:
            imgURL = json.loads(a['m'])['murl']
            imgURLs.append(imgURL)
        if len(imgURLs) != 0:
            self.imageURL.put(imgURLs)
            nowtime = datetime.now()
            message = str(nowtime)+' 已解析出'+str(len(imgURLs))+'圖片網址'
            self.MessageOutput(message)
        del req

    def saveImage(self,url):
        try:
            res = requests.get(url,timeout = 5)
            if str(res.status_code)[0] != '2':
                self.MessageOutput('connect fail,status code:'+str(res.status_code))
                self.imageError += 1
                return
        except Exception as e:
            self.MessageOutput('connect fail')
            self.imageError += 1
            return
        self.lock.acquire()
        index = self.index
        self.index += 1
        self.lock.release()
        filename = self.word+str(index)+'.jpg'
        f = open(os.path.join(self.DIR,filename),'wb')
        f.write(res.content)
        f.close
        del res
        nowtime = datetime.now()
        self.MessageOutput(str(nowtime)+' 第'+str(index)+'張圖片下載成功')

    def start_downloader(self):
        '''
        if downloader_setting.is_python3():
            choice = input('是否選擇允許商業用途的圖片[Y/N]：')
        else:
            choice = raw_input('是否選擇允許商業用途的圖片[Y/N]：')
        if choice.upper() == 'Y':
            self.iscopyright = True
        '''
        starttime = datetime.now()
        self.build_image_folder()
        queryURLs = self.build_query_url()
        self.pool.map(self.resolve_imgURL,queryURLs)
        while self.imageURL.qsize():
            urls = self.imageURL.get()
            self.pool.map(self.saveImage,urls)
        self.pool.close()
        self.pool.join()
        endtime = datetime.now()
        print(endtime,' 下載結束,共下載',self.index-self.start_index,'張圖片')
        print('共',self.imageError,'圖片網址回報錯誤')
        print('總歷時',endtime-starttime)
        return self.index-1

if __name__ == '__main__':
    if downloader_setting.is_python3():
        search = input('關鍵字：')
    else:
        search = raw_input('關鍵字：')

    mydownloader = downloader(search)
    mydownloader.start_downloader()
    del mydownloader


