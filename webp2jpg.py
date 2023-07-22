import os

comic = []
path = './image/'
a = os.listdir(path)
for img in a:
    if img.split('.')[-1] == 'webp':
        os.rename(path + img,path + img[0:-4]+'jpg')

print('done!')