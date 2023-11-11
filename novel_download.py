# # 名称：笔趣阁小说爬取
# # 作者：Scar乄心痕
# # 时间：2023-11-10 考研摸鱼ing
# # 说明：此代码只适用于笔趣阁网页小说的爬取，如果想要爬取其他的小说网站，需要根据网站的HTML文件的内容修改一些格式化代码
import requests
import re
from bs4 import BeautifulSoup
import threading
import sys  # 导入sys模块
sys.setrecursionlimit(3000)  # 将默认的递归深度修改为3000

# 全局变量
book_url = "https://m.xbiquge.bz/book/36670/"  # 书的首页URL
start_url = "https://m.xbiquge.bz/book/36670/40468115_2.html"  # 小说第一章对应的URL
file_name = "swzy.txt"  # 设置保存的文件名字

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
count = 5965  # 计数器 计数章节数
lock = threading.Lock()  # 线程锁，用于控制对文件的访问
visited_urls = set()  # 用于存储已经访问过的章节链接


def getContent(content_url):
    global count
    res = requests.get(content_url, headers=header, timeout=30)
    res.encoding = 'gbk'

    soup = BeautifulSoup(res.text, 'html.parser')
    title = soup.select('.nr_title')[0].text.lstrip('章 节目录 ')  # 获取章节题目
    content = soup.select('#nr1')[0].text.rstrip('-->>本章未完，点击下一页继续阅读')  # 获取章节内容
    next_url = book_url + soup.select('#pb_next')[0]['href']  # 获取下个章节URL

    # ======格式化代码，笔趣阁的前端程序员wdnmd======
    content = content.replace('    ', '\n')
    content = content.replace('  ', '')
    content = content.replace(' ', '')
    content = content.replace('&nbs', '\n')
    content = content.replace('&nbsp', '\n')
    if '_' not in content_url:
        content = content[:-1] if content.endswith('\n') else content
        content = content[:-3] if content.endswith('...') else content
        both = title + '\n' + content
    else:
        # content = re.sub(r'^.*?[，；。,;”？.]', '', content, count=1)
        both = content + '\n'
    # ======格式化代码，笔趣阁的前端程序员wdnmd======

    with lock:
        if content_url not in visited_urls:
            visited_urls.add(content_url)
            print(both, file=f)  # 写入文件
            print("已下载 第" + str(count) + "章")  # 输出到屏幕提示 状态
            count += 1

    if next_url.split('/')[3] != 'book':
        return
    getContent(next_url)


def download_novels(start_url, thread_num=8):
    threads = []

    for _ in range(thread_num):
        t = threading.Thread(target=getContent, args=(start_url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


if __name__ == '__main__':
    f = open(file_name, 'a+', encoding='utf-8')
    download_novels(start_url)
    f.close()
    print('小说下载完成!')
