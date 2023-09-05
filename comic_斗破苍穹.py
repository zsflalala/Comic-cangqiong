import aiohttp
import asyncio
import aiofiles
import re

'''
    comic网站: https://cocomanga.org/manga/doupocangqiong-zhiyinmankerenxiang/0_564/
    示例源代码: example.html
    webp windows不能够通过图片打开,改后缀名成jpg即可,批处理文件为webp2jpg.py
'''

# 异步获取所有图片的下载链接
async def get_comic_url(file_path):
    for page in range(0,570):
        url = f'https://cocomanga.org/manga/doupocangqiong-zhiyinmankerenxiang/0_{page}/'
        async with aiohttp.ClientSession() as session:
            async with await session.get(url=url,headers=headers) as response:
                page_text = await response.text()
                ex = '<img decoding="async" src="(.*?)" />'
                img_src_list = re.findall(ex,page_text,re.S)
                for img in img_src_list:
                    img_src = img.split('/')
                    pic_name = file_path + img_src[-2] + img_src[-1]
                    image_dic[pic_name] = img
                    print(pic_name,' have saved in the dic.')

    # 存储到文件中
    # for pic_name,img_url in image_dic.items(): 
    #     async with aiofiles.open('./斗破苍穹.txt','a',encoding='utf-8') as fp:
    #         await fp.write(pic_name + ',' + img_url + '\n')
    
# 异步下载
async def pic_download(pic_name,img_url,semaphore):
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            async with await session.get(url=img_url,headers=headers) as response:
                img_content = await response.content.read()
                async with aiofiles.open(pic_name,'wb') as fp:
                    await fp.write(img_content)
                    print(pic_name,'download successfully!')

if __name__ == '__main__':
    tasks = []
    image_dic = {}
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }

    # 存放的文件路径 默认再当前的image文件夹下
    file_path = './image/'
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(get_comic_url(file_path))
    loop.run_until_complete(task)

    # 从文件中获取图片存储路径和链接
    # with open('斗破苍穹.txt','r',encoding='utf-8') as f:
    #     for line in f.readlines():
    #         line = line.replace('\n','').split(',')
    #         image_dic[line[0]] = line[1]
    
    # tasks数量有并发限制 设置数量为100 windows最大为500
    semaphore = asyncio.Semaphore(100)
    for pic_name,img_url in image_dic.items():
        task = asyncio.ensure_future(pic_download(pic_name,img_url,semaphore))
        tasks.append(task)
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()