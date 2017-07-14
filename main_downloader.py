import google_image_downloader
import ig_image_downloader
import baidu_image_downloader
import bing_image_downloader
import os,time
from datetime import datetime

def get_index(folder_dir,food):
    filenames = os.listdir(folder_dir)
    indexs = []
    for filename in filenames:
        if not '.jpg' in filename:
            filenames.remove(filename)
            continue
        i = int(filename.replace(food,'').replace('.jpg',''))
        indexs.append(i)
    if len(indexs) == 0:
        return 1
    return max(indexs)+1

if __name__ == '__main__':
    search = input('輸入關鍵字:')
    DIR = os.getcwd()
    DIR = os.path.join(DIR,'image',search)
    index = 0
    if not os.path.exists(DIR):
        os.mkdir(DIR)
        index = 1
    else:
        index = get_index(DIR,search)

    starttime = datetime.now()
    #google
    print(starttime,'開始從google搜尋引擎下載圖片')
    mydownloader = google_image_downloader.downloader(search,DIR,index)
    nowindex = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    google_image_num = nowindex - index
    lastindex = nowindex
    #instagram
    nowtime = datetime.now()
    print(nowtime,'開始從Instagram下載圖片')
    mydownloader = ig_image_downloader.downloader(search,DIR,nowindex)
    nowindex = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    ig_image_num = nowindex - lastindex
    lastindex = nowindex
    #bing
    nowtime = datetime.now()
    print(nowtime,'開始從Bing搜尋引擎下載圖片')
    mydownloader = bing_image_downloader.downloader(search,DIR,nowindex)
    nowindex = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    bing_image_num = nowindex - lastindex
    lastindex = nowindex
    #baidu
    nowtime = datetime.now()
    print(nowtime,'開始從Baidu搜尋引擎下載圖片')
    mydownloader = baidu_image_downloader.downloader(search,DIR,nowindex)
    nowindex = mydownloader.start_downloader()
    time.sleep(1)
    del mydownloader
    baidu_image_num = nowindex - lastindex
    endtime = datetime.now()
    print(search,'的圖片下載結束,共下載',nowindex-1,'張圖片')
    print('總歷時',endtime-starttime)
    print('Google:',google_image_num,'張')
    print('Instagram:',ig_image_num,'張')
    print('Bing:',bing_image_num,'張')
    print('Baidu:',baidu_image_num,'張')





