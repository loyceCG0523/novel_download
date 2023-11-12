import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from cn2an import cn2an
import threading
import sys  # 导入sys模块
sys.setrecursionlimit(3000)

book_url = "https://m.xbiquge.bz/book/36670/"
start_url = "https://m.xbiquge.bz/book/36670/22382149.html"
file_name = "swzy.txt"
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
count = 1
lock = threading.Lock()
visited_urls = set()


def getContent(session, content_url):
    global count
    try:
        res = session.get(content_url, headers=header, timeout=30)
        res.encoding = 'gbk'

        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.select('.nr_title')[0].text.lstrip('章 节目录 ')
        content = soup.select('#nr1')[0].text.rstrip('-->>本章未完，点击下一页继续阅读')
        next_url = book_url + soup.select('#pb_next')[0]['href']
        match = re.search(r'第([^章]+)章', title)
        if match:
            title_number = cn2an(match.group(1))
            title = re.sub(r'第([^章]+)章', rf'第{title_number}章', title)

        content = content.replace('    ', '\n')
        content = content.replace('  ', '')
        content = content.replace(' ', '')
        content = content.replace('&nbs', '\n')
        content = content.replace('&nbsp', '\n')
        if '_' not in content_url:
            content = content[:-1] if content.endswith('\n') else content
            content = content[:-3] if content.endswith('...') else content
            both = '\n' + title + '\n' + content + '（***此处翻页***）'
        else:
            both = content + '\n'

        with lock:
            if content_url not in visited_urls:
                visited_urls.add(content_url)
                print(both, file=f)
                print("已下载 第" + str(count) + "章")
                count += 1

        if next_url.split('/')[3] != 'book':
            return
        getContent(session, next_url)
    except Exception as e:
        print(f"Error fetching {content_url}: {e}")


def download_novels(start_url, thread_num=8):
    with requests.Session() as session:
        session.headers.update(header)
        with ThreadPoolExecutor(max_workers=thread_num) as executor:
            futures = [executor.submit(getContent, session, start_url) for _ in range(thread_num)]
            for future in futures:
                future.result()


if __name__ == '__main__':
    f = open(file_name, 'a+', encoding='utf-8')
    download_novels(start_url)
    f.close()
    print('小说下载完成!')
