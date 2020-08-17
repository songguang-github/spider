# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# author: songguang    time: 2020-08-02    version: 1.0
import time
import datetime
import requests
import math
import random
from Crypto.Cipher import AES  # 采用这里使用pycryptodemo库
import codecs
import base64
import concurrent.futures
from savefile import save_file


class WangYiYun(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Referer": "https://music.163.com/search/",
            "content-type": "application/x-www-form-urlencoded"
        }
        self.start_url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        self.mp3_url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='

    def __get_songs(self, name):
        # 构造 Form  Data
        d = '{"hlpretag":"<span class=\\"s-fc7\\">","hlposttag":"</span>","s":"%s","type":"1","offset":"0","total":"true","limit":"30","csrf_token":""}' % name
        wyy = DecryptMusic(d)
        data = wyy.get_data()
        # 发送post请求，获取响应
        try:  # 解决text乱码及url不响应问题
            response = requests.post(self.start_url, data=data, headers=self.headers,
                                     verify=True, timeout=10)  # 获得服务器response
            response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
            response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
        except requests.RequestException:
            print("request error: {}".format(self.start_url))  # 打印错误信息
            raise Exception("request error: {}".format(self.start_url))  # 抛出异常错误
        return response.json()['result']

    def __get_mp3(self, id):
        d = '{"ids":"[%s]","level":"standard","encodeType":"aac","csrf_token":""}' % id
        wyy = DecryptMusic(d)
        data = wyy.get_data()
        try:  # 解决text乱码及url不响应问题
            response = requests.post(self.mp3_url, data=data, headers=self.headers,
                                     verify=True, timeout=10)  # 获得服务器response
            response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
            response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
        except requests.RequestException:
            print("request error: {}".format(self.mp3_url))  # 打印错误信息
            raise Exception("request error: {}".format(self.mp3_url))  # 抛出异常错误
        return response.json()['data'][0]['url']

    def __download_mp3(self, url, filename):
        # 下载歌曲
        dir_path = 'music'
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        thread_pool.submit(save_file, url, name=filename, dir_path=dir_path)
        thread_pool.shutdown()

    def __print_info(self, songs):
        songs_list = []
        for num, song in enumerate(songs):
            print(num, '歌曲名字', song['name'], '作者：', song['ar'][0]['name'])
            songs_list.append((song['name'], song['id'], song['ar'][0]['name']))
        return songs_list

    def run(self):
        while True:
            name = input('请输入你需要下载的歌曲：')
            songs = self.__get_songs(name)
            if songs['songCount'] == 0:
                print('没有搜到此歌曲，请换个关键字')
            else:
                songs = self.__print_info(songs['songs'])
                num = input('请输入需要下载的歌曲，输入左边对应的数字即可：')
                url = self.__get_mp3(songs[int(num)][1])
                if not url:
                    print('歌曲需要收费， 下载失败')
                else:
                    filename = "{0} {1}".format(songs[int(num)][0], songs[int(num)][2])
                    self.__download_mp3(url, filename)
            flag = input('如需要继续可以按任意键进行搜歌， 否则按0结束程序：')
            if flag == '0':
                break


class DecryptMusic(object):
    def __init__(self, d):
        self.d = d
        self.e = '010001'
        self.f = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.g = '0CoJUm6Qyw8W8jud'
        self.random_text = self.get_random_str()

    def get_random_str(self):  # a(a)函数
        str_temp = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        res = ''
        for x in range(16):
            index = math.floor(random.random() * len(str_temp))
            res = res + str_temp[index]
        return res

    def aes_encrypt(self, text, key):
        iv = '0102030405060708'.encode('utf-8')
        pad = 16 - len(text.encode('utf-8')) % 16
        text = text + pad * chr(pad)
        key = key.encode('utf-8')
        text = text.encode('utf-8')
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        msg = base64.b64encode(encryptor.encrypt(text))
        return msg

    def rsa_encrypt(self, value, text, modulus):
        '''进行rsa加密'''
        text = text[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(value, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)

    def get_data(self):
        params = self.aes_encrypt(self.d, self.g)
        params = self.aes_encrypt(params.decode('utf-8'), self.random_text)
        enc_sec_key = self.rsa_encrypt(self.e, self.random_text, self.f)
        return {
            'params': params,
            'encSecKey': enc_sec_key
        }


if __name__ == "__main__":
    print('Code execution begins\n')
    start = time.time()
    # 主程序代码
    wangyiyun = WangYiYun()
    wangyiyun.run()

    # 主程序代码完成
    print('\nCode execution finished within {0:^.4f} seconds'.format(time.time() - start))  # 代码运行时间，以秒计
    print('Code execution finished at %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
