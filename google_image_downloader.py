# -*- coding: UTF-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import json,requests,os,time
import threading
from multiprocessing.dummy import Pool
from datetime import datetime
import downloader_setting

class downloader(object):
    """docstring for downloader"""
    def __init__(self, word):
        super(downloader, self).__init__()
        self.word = word
        self.header = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8'}
        self.DIR = ''
        self.index = 1
        self.start_index = 1
        self.pool = Pool(30)
        self.lock = threading.Lock()
        self.imageURLerror = 0
        self.iscopyright = False

    def build_image_folder(self):
        DIR = os.getcwd()
        DIR = os.path.join(DIR,'image',self.word,'Google')
        nowtime = datetime.now()
        print(nowtime,'正在建立圖片儲存資料夾')
        self.DIR = os.path.join(DIR,nowtime.strftime('%Y-%m-%d %H:%M:%S'))
        os.makedirs(self.DIR)

    def get_image_url(self):
        if not self.iscopyright:
            driver = webdriver.Chrome()
            driver.implicitly_wait(2)
            url = "https://www.google.com.tw/search?q="+self.word+"&source=lnms&tbm=isch"
            driver.get(url)
            scroll_down = "document.body.scrollTop=document.body.scrollHeight"
            for i in range(10):
                driver.execute_script(scroll_down)
                progress = (i+1)*10
                nowtime = datetime.now()
                print('%s 模擬滾動條下拉中 -- %.1f%%' %(str(nowtime),progress))
                time.sleep(1)
                try:
                    driver.find_element_by_id('smb').click()
                except Exception as e:
                    continue
            elements = driver.find_elements_by_class_name('rg_meta')
            items = [element.get_attribute('innerHTML') for element in elements]
            del elements
            driver.quit()
            imageURLs = []
            for item in items:
                link=json.loads(item)["ou"]
                imageURLs.append(link)
            return imageURLs
        else:
            '''
            url = 'https://www.google.com.tw/search?q='+self.word+'&source=lnms&tbm=isch&tbs=sur:fc'
            res = requests.get(url,headers = self.header)
            soup = BeautifulSoup(res.text,"html.parser")
            all_img = soup.find_all("div","rg_meta")
            imgURLs = []
            for a in all_img:
                link=json.loads(a.text)["ou"]
                imgURLs.append(link)
            return imgURLs
            '''

    def saveImage(self,url):
        try:
            res = requests.get(url,timeout = 5,headers = self.header)
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
        '''
        if downloader_setting.is_python3():
            choice = input('是否選擇標示允許再利用的圖片[Y/N]：')
        else:
            choice = raw_input('是否選擇標示允許再利用的圖片[Y/N]：')
        if choice.upper() == 'Y':
            self.iscopyright = True
        '''
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


