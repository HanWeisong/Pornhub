#!/usr/bin/env python
# coding=utf-8

import os
import time
import urllib
import json

import requests
from lxml import etree
import fire


_time = time.strftime("%Y-%m-%d-%H:%M", time.localtime())
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
}


def list_page(url):
    print('crawling : %s' % url)
    resp = requests.get(url, headers=headers)
    html = etree.HTML(resp.text)
    vkeys = html.xpath('//*[@class="phimage"]/div/a/@href')
    gif_keys = html.xpath('//*[@class="phimage"]/div/a/img/@data-mediabook')
    _list = []
    for i in range(len(vkeys)):
        item = {}
        item['vkey'] = vkeys[i].split('=')[-1]
        item['gif_url'] = gif_keys[i]
        _list.append(item)
        try:
            downloadImageFile(item['gif_url'], item['vkey'])
        except Exception as err:
            print(err)
    with open('logs/%s.json' % _time, 'w') as file:
        file.write(json.dumps(_list, ensure_ascii=False, indent=4))


def downloadImageFile(imgUrl, name):
    path = 'logs/%s.webm' % name
    tem = os.path.exists(path)
    if tem:
        print('this had download %s' % name)
        return
    print("Download Image File=", name)
    r = requests.get(imgUrl, stream=True)  # here we need to set stream = True parameter
    with open('webm/%s.webm' % name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        f.close()


def req_detail_page(url):
    s = requests.Session()
    resp = s.get(url, headers=headers)
    html = etree.HTML(resp.content)
    title = ''.join(html.xpath('//h1//text()')).strip()
    js = html.xpath('//*[@id="player"]/script/text()')[0]
    n1 = js.find('{')
    n2 = js.find('var player_mp4_seek')
    tem = js[n1:n2].strip().strip(';')
    # print(tem)
    con = json.loads(tem)
    for _dict in con['mediaDefinitions']:
        if 'quality' in _dict.keys():
            if _dict.get('videoUrl'):
                print(_dict.get('quality'), _dict.get('videoUrl'))
                try:
                    downloadvideo(_dict.get('videoUrl'), title)
                    break
                except Exception as err:
                    print(err)


def downloadvideo(url, title):
    urllib.request.urlretrieve(url, 'mp4/%s.mp4' % title)
    print('download video success ! %s %s' % (url, title))


def run(_list=None):
    paths = ['logs', 'webm', 'mp4']
    for path in paths:
        if not os.path.exists(path):
            os.mkdir(path)
    if _list:
        urls = ['https://www.pornhub.com/video?o=tr',
                'https://www.pornhub.com/video?o=ht']
        for url in urls:
            try:
                list_page(url)
            except Exception as err:
                print(err)
    else:
        with open('download.txt', 'r') as file:
            keys = list(set(file.readlines()))
        for key in keys:
            url = 'https://www.pornhub.com/view_video.php?viewkey=%s' % key.strip()
            print(url)
            req_detail_page(url)
    print('finish !')


if __name__ == '__main__':
    fire.Fire()
