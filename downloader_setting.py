import sys

def is_python3():
    string = sys.version
    str_list = string.split(' ')
    if str_list[0][0] == '3':
        return True
    elif str_list[0][0] == '2':
        return False
    return False

def get_index(folder_dir,keyword):
    filenames = os.listdir(folder_dir)
    indexs = []
    for filename in filenames:
        if not '.jpg' in filename:
            filenames.remove(filename)
            continue
        i = int(filename.replace(keyword,'').replace('.jpg',''))
        indexs.append(i)
    if len(indexs) == 0:
        return 1
    return max(indexs)+1

if __name__ == '__main__':
    if not is_python3():
        print('now using python2')


