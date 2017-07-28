# -*- coding: UTF-8 -*-
import random,os
import shutil
from downloader_setting import is_python3
random.seed(10)

def get_filenames(folder_dir):
    filenames = os.listdir(folder_dir)
    not_image = []
    for filename in filenames:
        if not '.jpg' in filename:
            not_image.append(filename)
    for filename in not_image:
        filenames.remove(filename)
    return filenames

def build_subfolder(folder_dir):
    name_list = ['train','validation']
    for name in name_list:
        subfolder_dir = os.path.join(folder_dir,name)
        if not os.path.exists(subfolder_dir):
            os.makedirs(subfolder_dir)

if __name__ == '__main__':
    if is_python3():
        DIR = input('input folder directory:')
    else:
        DIR = raw_input('input folder directory:')
    build_subfolder(DIR)
    filenames = get_filenames(DIR)
    print(filenames)

    num = len(filenames)
    train_num = num*4//5
    val_num = num//5
    random.shuffle(filenames)
    train = filenames[:train_num]
    validation = filenames[train_num:]

    folder_list = [train,validation]
    name_list = ['train','validation']

    for i in range(len(folder_list)):
        filenames = folder_list[i]
        print(filenames)
        folder_name = name_list[i]
        for filename in filenames:
            file_dir = os.path.join(DIR,filename)
            new_dir = os.path.join(DIR,folder_name,filename)
            shutil.move(file_dir, new_dir)
