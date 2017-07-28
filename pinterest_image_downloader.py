# -*- coding: UTF-8 -*-
from selenium import webdriver
import os,time,requests,threading
import urllib.parse
from datetime import datetime
from multiprocessing.dummy import Pool
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
        self.lock = threading.Lock()
        self.imageURLerror = 0

    def build_image_folder(self):
        DIR = os.getcwd()
        DIR = os.path.join(DIR,'image',self.word,'Pinterest')
        nowtime = datetime.now()
        print(nowtime,'正在建立圖片儲存資料夾')
        self.DIR = os.path.join(DIR,nowtime.strftime('%Y-%m-%d %H-%M-%S'))
        os.makedirs(self.DIR)

    def get_image_url(self):
        search_word = urllib.parse.quote(self.word)
        url = 'https://www.pinterest.com/search/pins/?q='+search_word
        driver = webdriver.Chrome()
        driver.implicitly_wait(2)
        driver.get(url)
        scroll_down = "document.body.scrollTop=document.body.scrollHeight"

        old_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            nowtime = datetime.now()
            driver.execute_script(scroll_down)
            print('%s 模擬滾動條下拉中 ' %(str(nowtime)))
            time.sleep(3)
            height = driver.execute_script("return document.body.scrollHeight")
            if old_height == height:
                print('%s 頁面已到底 ' %(str(datetime.now())))
                break
            old_height = height

        elements = driver.find_elements_by_class_name('GrowthUnauthPinImage')
        image_tags = [element.find_element_by_tag_name('img') for element in elements]
        imageURL = [image_tag.get_attribute('src') for image_tag in image_tags]
        driver.quit()
        del elements,image_tags
        return imageURL

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
        self.build_image_folder()
        image_urls = self.get_image_url()
        self.pool.map(self.saveImage,image_urls)
        self.pool.close()
        self.pool.join()
        endTime = datetime.now()
        print(endTime,'下載結束,共下載',self.index-self.start_index,'張圖片')
        print('共',self.imageURLerror,'圖片網址回報錯誤')
        print('總歷時',endTime - startTime)
        return self.index-1

if __name__ == '__main__':
    if downloader_setting.is_python3():
        search = input('關鍵字：')
    else:
        search = raw_input('關鍵字：')

    mydownloader = downloader(search)
    mydownloader.start_downloader()

