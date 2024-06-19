import aiohttp
import asyncio
import aiofiles
import re
import requests
from lxml import etree
import os
from loguru import logger

'''
    comic网站: https://godamh.com/chapterlist/zhenhunjie-xuchen
    在网络调试器中(均为get请求): 
        单章节 get?mid=175 ==>> 调用接口,获得接口数据 https://api-get.mgsearcher.com/api/manga/get?mid=175
        整个章节 https://api-get.mgsearcher.com/api/manga/get?mid=175&mode=all ==>> 获得每个章节的id
        对每个章节图片数据 getinfo https://api-get.mgsearcher.com/api/chapter/getinfo?m=175&c=1525162 ==>> 获得每个章节图片数据json
'''

# 获取所有章节链接以及章节名称
def get_page_url(origion_url,headers):
    resp = requests.get(url=origion_url,headers=headers).json()
    chapters = resp['data']['chapters']
    for chapter in chapters:
        id = chapter.get("id")
        chapter_url = f'https://api-get.mgsearcher.com/api/chapter/getinfo?m=175&c={id}'
        chapter_urls.append(chapter_url)

# 异步获取所有图片的下载链接
async def get_comic_url(url,file_path,text_name):
    async with aiohttp.ClientSession() as session:
        async with await session.get(url=url,headers=headers) as response:
            resp = await response.json()
            images = resp['data']['info']['images']
            for img in images:
                img = img.get('url')
                img_src = img.split('/')
                pic_name = file_path + img_src[-2] + img_src[-1]
                image_dic[pic_name] = img
                logger.info(f'{pic_name} have saved in the dic.')
                # 存储到文件中
                async with aiofiles.open(text_name,'a',encoding='utf-8') as fp:
                    await fp.write(pic_name + ',' + img + '\n')
    
# 异步下载
async def pic_download(pic_name,img_url,semaphore = asyncio.Semaphore(100)):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with await session.get(url=img_url,headers=headers) as response:
                img_content = await response.content.read()
                dir_path = '/'.join(pic_name.split('/')[:-1])
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                if not os.path.exists(pic_name):
                    async with aiofiles.open(pic_name,'wb') as fp:
                        await fp.write(img_content)
                        print(pic_name,'download successfully!')

if __name__ == '__main__':
    tasks = []
    chapter_urls = []
    image_dic = {}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer' : 'https://godamh.com/',
    }
    origion_url = 'https://api-get.mgsearcher.com/api/manga/get?mid=175&mode=all'
    get_page_url(origion_url=origion_url,headers=headers)


    logger.info(f'{len(chapter_urls)}')

    # # 存放的文件路径 默认再当前的image文件夹下
    file_path = './image/'
    text_name = '镇魂街New.txt'

    for i in range(len(chapter_urls)):
        asyncio.run(get_comic_url(chapter_urls[i],file_path,text_name))
        
    # 从文件中获取图片存储路径和链接
    with open(text_name,'r',encoding='utf-8') as f:
        for line in f.readlines():
            line = line.replace('\n','').split(',')
            image_dic[line[0]] = line[1]

    # tasks数量有并发限制 设置数量为100 windows最大为500
    loop = asyncio.get_event_loop()
    semaphore = asyncio.Semaphore(100)
    for pic_name,img_url in image_dic.items():
        task = asyncio.ensure_future(pic_download(pic_name,img_url,semaphore))
        tasks.append(task)
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()