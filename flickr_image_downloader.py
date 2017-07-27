# -*- coding: UTF-8 -*-
import requests,os
import urllib.parse
from bs4 import BeautifulSoup
import threading
from multiprocessing.dummy import Pool
from queue import Queue
from datetime import datetime
import downloader_setting

class downloader(object):
    """docstring for downloader"""
    def __init__(self, word, folder_dir, file_index):
        super(downloader, self).__init__()
        self.word = word
        self.header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8'}
        self.DIR = folder_dir
        self.index = file_index
        self.start_index = file_index
        self.pool = Pool(30)
        self.lock = threading.Lock()
        self.imageURL = Queue()
        self.imageURLerror = 0
        self.iscopyright = False

    def build_page_url(self):
        word = urllib.parse.quote(self.word)
        url = 'https://www.flickr.com/search/?text='+word+'&page={page}'
        res = requests.get('https://www.flickr.com/search/?text='+word,headers = self.header)
        '''
        if self.iscopyright:
            url = 'https://www.flickr.com/search/?text='+word+'&page={page}&license=4%2C5%2C6%2C9%2C10'
            res = requests.get('https://www.flickr.com/search/?text='+word+'&license=4%2C5%2C6%2C9%2C10',headers = self.header)
        else:
            url = 'https://www.flickr.com/search/?text='+word+'&page={page}'
            res = requests.get('https://www.flickr.com/search/?text='+word,headers = self.header)
        '''
        soup = BeautifulSoup(res.text,"html.parser")
        tag = soup.find_all('a',"view-more-link")
        result_text = tag[0].text.split(' ')[2]
        result_num = int(result_text.replace(',',''))
        url_list = [url.format(page = i) for i in range(1,result_num//20)]
        return url_list

    def get_image_url(self,url):
        res = requests.get(url,headers = self.header)
        soup = BeautifulSoup(res.text,"html.parser")
        all_img = soup.find_all("div","view photo-list-photo-view requiredToShowOnServer awake")
        imgURLs = []
        for a in all_img:
            style_list = a['style'].split('; ')
            img_url = style_list[5]
            img_url = img_url.replace('background-image: url(','http:').replace(')','')
            imgURLs.append(img_url)
        self.lock.acquire()
        self.imageURL.put(imgURLs)
        self.lock.release()
        nowtime = datetime.now()
        message = str(nowtime)+' 已解析出'+str(len(imgURLs))+'個網址'
        self.MessageOutput(message)
        del res

    def saveImage(self,url):
        try:
            res = requests.get(url,timeout = 5,headers = self.header)
            if str(res.status_code)[0] != '2':
                self.MessageOutput('connect fail,status code:'+str(res.status_code)+'url:'+url)
                self.imageURLerror += 1
                return
        except Exception as e:
            self.MessageOutput('connect fail , url: '+url)
            self.imageURLerror += 1
            return
        imgdata = res.content
        self.lock.acquire()
        index = self.index
        self.index += 1
        self.lock.release()
        filename = self.word+str(index)+'.jpg'
        f = open(os.path.join(self.DIR,filename),'wb')
        f.write(imgdata)
        f.close
        del imgdata,res
        nowtime = datetime.now()
        self.MessageOutput(str(nowtime)+' 第'+str(index)+'張圖片下載成功:'+url)

    def MessageOutput(self,message):
        self.lock.acquire()
        print(message)
        self.lock.release()

    def start_downloader(self):
        '''
        if downloader_setting.is_python3():
            choice = input('是否選擇允許商業用途的圖片[Y/N]：')
        else:
            choice = raw_input('是否選擇允許商業用途的圖片[Y/N]：')
        if choice.upper() == 'Y':
            self.iscopyright = True
        '''
        startTime = datetime.now()
        page_urls = self.build_page_url()
        self.pool.map(self.get_image_url,page_urls)
        while self.imageURL.qsize():
            url = self.imageURL.get()
            self.pool.map(self.saveImage,url)
        self.pool.close()
        self.pool.join()
        endTime = datetime.now()
        print(endTime,'下載結束,共下載',self.index-self.start_index,'張圖片')
        print('共',self.imageURLerror,'圖片網址回報錯誤')
        print('總歷時',endTime - startTime)
        return self.index

if __name__ == '__main__':
    DIR = os.getcwd()
    if downloader_setting.is_python3():
        search = input('關鍵字：')
    else:
        search = raw_input('關鍵字：')
    DIR = os.path.join(DIR,'image',search)
    if not os.path.exists(DIR):
        os.makedirs(DIR)
        index = 1
    else:
        index = downloader_setting.get_index(DIR,search)

    mydownloader = downloader(search,DIR,index)
    mydownloader.start_downloader()

