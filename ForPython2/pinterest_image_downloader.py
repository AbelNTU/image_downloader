# -*- coding: UTF-8 -*-
from selenium import webdriver
import os,time,requests,threading
import urllib
from datetime import datetime
from multiprocessing.dummy import Pool


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
        search_word = urllib.quote(self.word)
        url = 'https://www.pinterest.com/search/pins/?q='+search_word
        driver = webdriver.Chrome()
        driver.implicitly_wait(2)
        driver.get(url)
        scroll_down = "document.body.scrollTop=document.body.scrollHeight"
        page = 40
        for i in range(page):
            nowtime = datetime.now()
            progress = round((i+1)/page*100,1)
            driver.execute_script(scroll_down)
            print('%s 模擬滾動條下拉中 -- %.1f%%' %(str(nowtime),progress))
            time.sleep(1)
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
    search = raw_input('搜尋關鍵字：')
    DIR = os.path.join(DIR,search)
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    mydownloader = downloader(search,DIR,1)
    mydownloader.start_downloader()

