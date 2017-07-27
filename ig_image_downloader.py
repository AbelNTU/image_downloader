# -*- coding: UTF-8 -*-
from selenium import webdriver
import requests,re,time,os
import urllib.parse
import threading
from datetime import datetime
from multiprocessing.dummy import Pool
import downloader_setting

class downloader(object):
    """docstring for downloader"""
    def __init__(self, word, folder_dir, file_index):
        super(downloader, self).__init__()
        self.word = word
        self.DIR = folder_dir
        self.index = file_index
        self.start_index = file_index
        self.pool = Pool(30)
        self.lock = threading.Lock()
        self.imageURLerror = 0

    def get_image_url(self):
        word = urllib.parse.quote(self.word)
        url = 'https://www.instagram.com/explore/tags/{word}/?hl=zh-tw'
        url = url.format(word = word)

        driver = webdriver.Chrome()
        driver.get(url)
        driver.implicitly_wait(2)
        num = driver.find_element_by_class_name('_bkw5z').text
        print('共',num,'則貼文')
        maxnum = int(num.replace(',',''))
        scroll_down = "document.body.scrollTop=document.body.scrollHeight"
        scroll_up = "document.body.scrollTop=document.body.scrollHeight-5000"
        driver.execute_script(scroll_down)
        time.sleep(0.5)
        driver.find_element_by_link_text('載入更多內容').click()

        page =  maxnum // 12
        for i in range(page):
            driver.execute_script(scroll_down)
            nowtime = datetime.now()
            progress = round((i+1)/page*100,1)
            print('%s 模擬滾動條下拉中 -- %.1f%%' %(str(nowtime),progress))
            time.sleep(0.5)
            driver.execute_script(scroll_up)
            time.sleep(0.5)
        nowtime = datetime.now()
        print(nowtime,'開始擷取圖片網址')
        elements = driver.find_elements_by_class_name('_jjzlb')
        imgURLs = [element.find_element_by_tag_name("img").get_attribute("src") for element in elements]
        driver.quit()
        nowtime = datetime.now()
        print(nowtime,'已擷取',len(imgURLs),'圖片網址,開始下載圖片')
        return imgURLs

    def saveImage(self,url):
        try:
            res = requests.get(url,timeout = 5)
            if str(res.status_code)[0] != '2':
                self.MessageOutput('connect fail,status code:'+str(res.status_code))
                self.imageURLerror += 1
                return
        except Exception as e:
            self.MessageOutput('connect fail')
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
        self.MessageOutput(str(nowtime)+' 第'+str(index)+'張圖片下載成功')

    def MessageOutput(self,message):
        self.lock.acquire()
        print(message)
        self.lock.release()

    def start_downloader(self):
        startTime = datetime.now()
        image_urls = self.get_image_url()
        self.pool.map(self.saveImage,image_urls)
        self.pool.close()
        self.pool.join()
        endTime = datetime.now()
        print(endTime,'下載結束,共下載',self.index-self.start_index,'張圖片')
        print('共',self.imageURLerror,'圖片網址回報錯誤')
        print('總歷時',endTime - startTime)
        return self.index


if __name__ == '__main__':
    #路徑
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

