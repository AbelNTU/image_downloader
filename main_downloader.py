# -*- coding: UTF-8 -*-
import google_image_downloader
import ig_image_downloader
import baidu_image_downloader
import bing_image_downloader
import pinterest_image_downloader
import flickr_image_downloader
import os,time
from datetime import datetime
import downloader_setting

if __name__ == '__main__':
    if downloader_setting.is_python3():
        search = input('關鍵字：')
    else:
        search = raw_input('關鍵字：')

    starttime = datetime.now()
    #google
    print(starttime,'開始從google搜尋引擎下載圖片=============================================================')
    mydownloader = google_image_downloader.downloader(search)
    google_image_num = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    #instagram
    nowtime = datetime.now()
    print(nowtime,'開始從Instagram下載圖片=============================================================')
    mydownloader = ig_image_downloader.downloader(search)
    ig_image_num = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    #pinterest
    nowtime = datetime.now()
    print(nowtime,'開始從pinterest下載圖片=============================================================')
    mydownloader = pinterest_image_downloader.downloader(search)
    pin_image_num = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    #bing
    nowtime = datetime.now()
    print(nowtime,'開始從Bing搜尋引擎下載圖片=============================================================')
    mydownloader = bing_image_downloader.downloader(search)
    bing_image_num = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    #baidu
    nowtime = datetime.now()
    print(nowtime,'開始從Baidu搜尋引擎下載圖片=============================================================')
    mydownloader = baidu_image_downloader.downloader(search)
    baidu_image_num = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    #flickr
    print(nowtime,'開始從flickr下載圖片=============================================================')
    mydownloader = flickr_image_downloader.downloader(search)
    flickr_image_num = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader

    endtime = datetime.now()
    all_num = google_image_num+ig_image_num+pin_image_num+bing_image_num+baidu_image_num+flickr_image_num
    print(search,'的圖片下載結束,共下載',all_num,'張圖片')
    print('總歷時',endtime-starttime)
    print('Google:',google_image_num,'張')
    print('Instagram:',ig_image_num,'張')
    print('Pinterest:',pin_image_num,'張')
    print('Bing:',bing_image_num,'張')
    print('Baidu:',baidu_image_num,'張')
    print('flickr:',flickr_image_num,'張')






