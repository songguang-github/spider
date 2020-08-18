# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# author: songguang    time: 2020-8-18    version: 1.0
import time
import datetime
import requests
import json
import jsonpath
import math
import random
from Crypto.Cipher import AES  # 采用这里使用pycryptodemo库
import codecs
import base64
from urllib.parse import quote
import hashlib
from prettytable import PrettyTable
from savefile import save_file


'''
*******************************************************QQ音乐************************************************************
'''


class QQMusic(object):

    def __init__(self):
        self.qqmusic_search_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?'
        self.qqmusic_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        }

    def get_qqmusic_mid(self, name):
        # url--> __init__
        # 设置header--> __init__
        # 发送请求，获取响应
        params = {"p": 1,
                  "n": 20,
                  "w": name,
                  "format": "json",
                  }
        try:  # 解决text乱码及url不响应问题
            response = requests.get(url=self.qqmusic_search_url, params=params, headers=self.headers,
                                    verify=True, timeout=10)  # 获得服务器response
            response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
            response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
        except requests.RequestException:
            print("request error: {}".format(self.qqmusic_search_url))  # 打印错误信息
            # raise Exception("request error: {}".format(self.qqmusic_search_url))  # 抛出异常错误
        song_list = jsonpath.jsonpath(response.json(), '$..song.list')[0]
        return [x['songmid'] for x in song_list], list(
            map(lambda x: ['QQ', ''.join(x['songname'].split()), ' & '.join([i['name'] for i in x['singer']]),
                           int(x['interval'])], song_list))

    def get_qqmusic_url(self, name):
        songmids, informations = self.get_qqmusic_mid(name)
        for songmid, information in zip(songmids, informations):
            params = {'-': 'getplaysongvkey1764431205985313',
                      'g_tk': 5381,
                      'sign': 'zza70qt35l5s26283ba78ea2226694a1df5fd291df139b',
                      'loginUin': 0,
                      'hostUin': 0,
                      'format': 'json',
                      'inCharset': 'utf8',
                      'outCharset': 'utf-8',
                      'notice': 0,
                      'platform': 'yqq.json',
                      'needNewCode': 0,
                      'data': '{"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"3167447995","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"3167447995","songmid":["%s"],"songtype":[0],"uin":"0","loginflag":1,"platform":"20"}},"comm":{"uin":0,"format":"json","ct":24,"cv":0}}' % songmid
                      }

            try:  # 解决text乱码及url不响应问题
                response = requests.get(url=self.qqmusic_url, params=params, headers=self.headers, verify=True,
                                        timeout=10)  # 获得服务器response
                response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
                response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
            except requests.RequestException:
                print("request error: {}".format(self.qqmusic_url))  # 打印错误信息
                # raise Exception("request error: {}".format(self.qqmusic_url))  # 抛出异常错误
            response_data = response.json()['req_0']['data']
            if response_data['midurlinfo'][0]['purl'] != '':
                URL = response_data['sip'][0] + response_data['midurlinfo'][0]['purl']
                information.append(URL)
            else:
                information.append('-' * 180)
        return informations


'''
*******************************************************网易云音乐************************************************************
'''


class CloudMusic(object):

    def __init__(self):
        self.cloudmusic_search_url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        self.cloudmusic_url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token='
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Referer": "https://music.163.com/search/",
            "content-type": "application/x-www-form-urlencoded"
        }

    def get_cloudmusic_id(self, name):
        # 构造 Form  Data
        d = '{"hlpretag":"<span class=\\"s-fc7\\">","hlposttag":"</span>","s":"%s","type":"1","offset":"0","total":"true","limit":"30","csrf_token":""}' % name
        wyy = DecryptMusic(d)
        data = wyy.get_data()
        # 发送post请求，获取响应
        try:  # 解决text乱码及url不响应问题
            response = requests.post(self.cloudmusic_search_url, data=data, headers=self.headers,
                                     verify=True, timeout=10)  # 获得服务器response
            response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
            response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
        except requests.RequestException:
            print("request error: {}".format(self.cloudmusic_search_url))  # 打印错误信息
            # raise Exception("request error: {}".format(self.cloudmusic_search_url))  # 抛出异常错误
        song_list = response.json()['result']['songs']
        return [x['id'] for x in song_list], list(
            map(lambda x: ['网易云', x['name'], ' & '.join([i['name'] for i in x['ar']]), int(x['dt']) / 1000], song_list))

    def get_cloudmusic_url(self, name):
        ids, informations = self.get_cloudmusic_id(name)
        for id, information in zip(ids, informations):
            d = '{"ids":"[%s]","level":"standard","encodeType":"aac","csrf_token":""}' % id
            wyy = DecryptMusic(d)
            data = wyy.get_data()
            try:  # 解决text乱码及url不响应问题
                response = requests.post(self.cloudmusic_url, data=data, headers=self.headers,
                                         verify=True, timeout=10)  # 获得服务器response
                response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
                response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
            except requests.RequestException:
                print("request error: {}".format(self.cloudmusic_url))  # 打印错误信息
                # raise Exception("request error: {}".format(self.cloudmusic_url))  # 抛出异常错误
            response_data = response.json()['data'][0]['url']
            if response_data != '':
                information.append(response_data)
            else:
                information.append('-' * 180)
        return informations


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


'''
*******************************************************酷我音乐************************************************************
'''


class CoolMeMusic(object):

    def __init__(self):
        self.coomemusic_search_url = 'http://www.kuwo.cn/api/www/search/searchMusicBykeyWord?'
        self.coomemusic_url = 'http://www.kuwo.cn/url?'

    def get_coolmemusic_id(self, name):
        params = {"key": name,
                  "pn": 1,
                  "rn": 30,
                  "httpsStatus": 1,
                  "reqId": "",
                  }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            "Referer": "http://www.kuwo.cn/search/list?key=%s" % (quote(name)),
            "csrf": "55J2HNYJ76J",
            "Cookie": "kw_token=55J2HNYJ76J"
        }
        try:  # 解决text乱码及url不响应问题
            response = requests.get(url=self.coomemusic_search_url, params=params, headers=headers, verify=True,
                                    timeout=10)  # 获得服务器response
            response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
            response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
        except requests.RequestException:
            print("request error: {}".format(self.coomemusic_search_url))  # 打印错误信息
            # raise Exception("request error: {}".format(self.coomemusic_search_url))  # 抛出异常错误
        song_list = response.json()['data']['list']
        return [x['rid'] for x in song_list], list(
            map(lambda x: ['酷我', x['name'], x['artist'], int(x['duration'])], song_list))

    def get_coolmemusic_url(self, name):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            "Referer": "http://www.kuwo.cn/search/list?key=%s" % (quote(name)),
            "Cookie": "kw_token=55J2HNYJ76J"
        }
        rids, informations = self.get_coolmemusic_id(name)
        for rid, information in zip(rids, informations):
            params = {
                'format': 'mp3',
                'rid': rid,
                'response': 'url',
                'type': 'convert_url3',
                'br': '128kmp3',
                'from': 'web',
                't': int(time.time() * 1000),
                'httpsStatus': 1,
                'reqId': '',
            }

            try:  # 解决text乱码及url不响应问题
                response = requests.get(url=self.coomemusic_url, params=params, headers=headers, verify=True,
                                        timeout=10)  # 获得服务器response
                response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
                response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
            except requests.RequestException:
                print("request error: {}".format(self.coomemusic_url))  # 打印错误信息
                # raise Exception("request error: {}".format(self.coomemusic_url))  # 抛出异常错误
            response_data = response.json()['url']
            if response_data != '':
                information.append(response_data)
            else:
                information.append('-' * 180)
        return informations


'''
*******************************************************酷狗音乐************************************************************
'''


class CoolDogMusic(object):

    def __init__(self):
        self.cooldogmusic_search_url = 'https://complexsearch.kugou.com/v2/search/song?'
        self.cooldogmusic_url = 'https://wwwapi.kugou.com/yy/index.php?'

    def get_cooldogmusic_hash(self, name):
        ts = str(int(time.time() * 1000))
        # 获取signature参数
        o = ["NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt",
             "bitrate=0",
             "callback=callback123",
             "clienttime=" + ts,
             "clientver=2000",
             "dfid=-",
             "inputtype=0",
             "iscorrection=1",
             "isfuzzy=0",
             "keyword=" + name,
             "mid=" + ts,
             "page=1",
             "pagesize=30",
             "platform=WebFilter",
             "privilege_filter=0",
             "srcappid=2919",
             "tag=em",
             "userid=-1",
             "uuid=" + ts,
             "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"]
        md5 = hashlib.md5()  # 创建hash对象
        md5.update("".join(o).encode())  # 向hash对象中添加需要做hash运算的字符串
        signature = md5.hexdigest()  # 获取字符串的hash值 十六进制

        params = {'callback': 'callback123',
                  'keyword': name,
                  'page': 1,
                  'pagesize': 30,
                  'bitrate': 0,
                  'isfuzzy': 0,
                  'tag': 'em',
                  'inputtype': 0,
                  'platform': 'WebFilter',
                  'userid': -1,
                  'clientver': 2000,
                  'iscorrection': 1,
                  'privilege_filter': 0,
                  'srcappid': 2919,
                  'clienttime': ts,
                  'mid': ts,
                  'uuid': ts,
                  'dfid': '-',
                  'signature': signature}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            "Referer": "https://www.kugou.com/yy/html/search.html",
            "Cookie": "kg_mid=51c4c082ede4cd8b006589d6a65d87a0",
        }

        try:  # 解决text乱码及url不响应问题
            response = requests.get(url=self.cooldogmusic_search_url, params=params, headers=headers, verify=True,
                                    timeout=10)  # 获得服务器response
            response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
            response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
        except requests.RequestException:
            print("request error: {}".format(self.cooldogmusic_search_url))  # 打印错误信息
            # raise Exception("request error: {}".format(self.cooldogmusic_search_url))  # 抛出异常错误
        song_list = json.loads(response.text.replace('callback123(', '')[0:-2])['data']['lists']
        return [x['FileHash'] for x in song_list], [x['AlbumID'] for x in song_list], list(
            map(lambda x: ['酷狗', x['SongName'].replace('<em>', '').replace('</em>', ''), x['SingerName'],
                           int(x['Duration'])], song_list))

    def get_cooldogmusic_url(self, name):
        hashs, album_ids, informations = self.get_cooldogmusic_hash(name)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
            "Referer": "https://www.kugou.com/song/",
        }
        cookies_str = 'kg_mid=1b577d35afd6f834f70982a68ddb1855; Hm_lvt_aedee6983d4cfc62f509129360d6bb3d=1597668323; kg_mid_temp=1b577d35afd6f834f70982a68ddb1855; Hm_lpvt_aedee6983d4cfc62f509129360d6bb3d=1597670784'
        cookies_dict = {cookie.split('=')[0]: cookie.split('=')[-1] for cookie in cookies_str.split('; ')}
        for hash, album_id, information in zip(hashs, album_ids, informations):
            params = {
                'r': 'play/getdata',
                # 'callback': 'jQuery19105840830020958463_'+ str(int(time.time() * 1000 - 1)),
                'callback': 'jQuery191058408300209' + str(random.randint(10000, 99999)) + '_' + str(
                    int(time.time() * 1000 - 1)),
                'hash': hash,
                'album_id': album_id,
                'dfid': '',
                'mid': '11b577d35afd6f834f70982a68ddb1855',  # fixed
                'platid': 4,
                '_': int(time.time() * 1000),
            }

            try:  # 解决text乱码及url不响应问题
                response = requests.get(url=self.cooldogmusic_url, params=params, headers=headers, verify=True,
                                        cookies=cookies_dict, timeout=10)  # 获得服务器response
                response.raise_for_status()  # 如果status_code不是200，产生异常requests.HTTPError
                response.encoding = response.apparent_encoding  # header中编码方式 = 内容分析出的编码方式
            except requests.RequestException:
                print("request error: {}".format(self.cooldogmusic_url))  # 打印错误信息
                # raise Exception("request error: {}".format(self.cooldogmusic_url))  # 抛出异常错误
            response_data = json.loads(response.text[41:-2])['data']['play_url']
            if response_data != '':
                information.append(response_data)
            else:
                information.append('-' * 180)
        return informations


def seconds2time(seconds):
    """
    秒数转换为时分秒格式h:m:s
    :param seconds: 秒数
    :type seconds: int or float
    :return: 时分秒格式h:m:s
    :rtype: str
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    time_str = "%02d:%02d:%02d" % (h, m, s)
    return time_str


def time2seconds(t):
    """
    时分秒格式h:m:s转换为秒数
    :param t: 时分秒格式h:m:s
    :type t: str
    :return: 秒数
    :rtype: int
    """
    h, m, s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


if __name__ == "__main__":
    print('>> Code execution begins\n')
    start = time.time()
    # 主程序代码
    name = input("请输入你需要下载的歌曲：")
    print('>>开始爬取QQ音乐')
    qqmusic = QQMusic()
    qqmusic_info = qqmusic.get_qqmusic_url(name)
    print('>>开始爬取网易云音乐')
    cloudmusic = CloudMusic()
    cloudmusic_info = cloudmusic.get_cloudmusic_url(name)
    print('>>开始爬取酷我音乐')
    coolmemusic = CoolMeMusic()
    coolmemusic_info = coolmemusic.get_coolmemusic_url(name)
    print('>>开始爬取酷狗音乐')
    cooldogmusic = CoolDogMusic()
    cooldogmusic_info = cooldogmusic.get_cooldogmusic_url(name)

    print('\n>> 全部爬取完成，正在整合数据!')
    music_infos = qqmusic_info + cloudmusic_info + coolmemusic_info + cooldogmusic_info
    table = PrettyTable(['序号', '音乐源', '歌曲名称', '歌手名称', '歌曲时长', '试听链接（打开即可下载）'])
    for num, music_info in enumerate(music_infos):
        music_info.insert(0, num)
        music_info[4] = seconds2time(music_info[4])
        table.add_row(music_info)
    print('\n', '>>>>>>>>>歌曲：%s' % name)
    print(table)
    dir_path = 'music'
    while True:
        index = input("请输入你需要下载歌曲的序号（结束程序请输入Q）：")
        if index == 'q' or index == 'Q':
            break
        elif index.isdecimal():
            url = music_infos[int(index)][5]
            filename = "{0} {1}".format(music_infos[int(index)][2], music_infos[int(index)][3])
            save_file(url, name=filename, dir_path=dir_path)  # 存储文件
        else:
            print("输入有误，请重新输入！")
            continue

    # 主程序代码完成
    print('\n>> Code execution finished within {0:^.4f} seconds'.format(time.time() - start))  # 代码运行时间，以秒计
    print('>> Code execution finished at %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
