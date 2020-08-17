# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# author: songguang    time: 2020-07-03    version: 1.0
import time
import datetime
import re
import requests
import os
import socket
import functools
from urllib.request import urlretrieve


def type_check(func):
    @functools.wraps(func)  # 将原始函数func的__name__等属性复制到wrapper()函数中
    def wrapper(*args, **kw):
        if isinstance(args[0], str):
            func(*args, **kw)
        elif isinstance(args[0], list):
            args_temp = args[1:]
            for url in args[0]:
                func(url, *args_temp, **kw)
        return
    return wrapper


@type_check  # url类型判断装饰器
def save_file(url, dir_path=None, name=None, extension_default=None, timeout=5, retry_max=5):
    """从url中存储文件到本地：文件、图片、影音文件，urllib.request.urlretrieve()方法"""
    # check argument type
    if dir_path is None:
        dir_path = os.path.dirname(__file__)  # 获得当前文件目录
    elif not os.path.exists(dir_path):
        os.mkdir(dir_path)  # "./dir"当前目录下dir文件夹
    else:
        if not os.path.isdir(dir_path):  # dir_path路径是否为文件夹
            raise OSError("dir path is not folder")

    if name is not None:  # 给定存储文件名时
        name_extension_temp = url.split('/')[-1].split('?')[0]  # 从url中提取名字+扩展名
        extension_temp = re.findall(r'\.(.*?)$', name_extension_temp[-5:], re.S)  # 从url中提取的文件扩展名
        if extension_default is not None:  # 给定扩展名缺省值时
            if len(extension_temp) == 0:  # url中扩展名不存在时
                name_extension = "{0}.{1}".format(name, extension_default)
            else:  # url中扩展名存在时
                name_extension = "{}.{}".format(name, extension_temp[0])
        else:  # 未给定扩展名缺省值时
            if len(extension_temp) == 0:  # url中扩展名不存在时
                # name_extension = "{}.{}".format(name, 'txt')  # 默认以txt格式保存
                name_extension = name  # 没有扩展名
            else:  # url中扩展名存在
                name_extension = "{}.{}".format(name, extension_temp[0])
    else:  # 未给定存储文件名时
        name_extension_temp = url.split('/')[-1].split('?')[0]  # 从url中提取名字+扩展名
        extension_temp = re.findall(r'\.(.*?)$', name_extension_temp[-5:], re.S)  # 从url中提取的文件扩展名
        if extension_default is not None:  # 给定扩展名缺省值时
            if len(extension_temp) == 0:  # url中扩展名不存在时
                name_extension = "{}.{}".format(name_extension_temp, extension_default)
            else:  # url中扩展名存在时
                name_extension = name_extension_temp
        else:  # 未给定扩展名缺省值时
            name_extension = name_extension_temp
    name_extension = re.sub(r'[?\\*|"<>:/]', ' ', name_extension)  # 清洗掉Windows系统非法文件名的字符串

    # 文件传输时的回调函数 urllib.request.urlretrieve()
    def reporthook(block_num, block_size, total_size):
        """
        文件传输时的回调函数 urllib.request.urlretrieve() 显示下载进度
        :param block_num: 已经下载的数据块
        :param block_size: 数据块的大小
        :param total_size: 远程文件大小
        :return: None
        """
        percent = (100.0 * block_num * block_size / total_size) if (block_num * block_size) < total_size else 100
        print("\rDownloading {0}: {1:^5.1f}%".format(name_extension, percent), end="")
        return None

    # urllib.request.urlretrieve()下载文件，解决下载不完全问题且避免陷入死循环
    socket.setdefaulttimeout(timeout)  # 设置超时时间为timeout
    # noinspection PyBroadException
    try:
        urlretrieve(url, os.path.join(dir_path, name_extension), reporthook=reporthook)
    except socket.timeout:
        count = 1
        while count <= retry_max:
            try:
                urlretrieve(url, os.path.join(dir_path, name_extension), reporthook=reporthook)
                break
            except socket.timeout:
                err_info = '\nReloading for {0} {1}'.format(count, "time" if count == 1 else "times")
                print(err_info)
                count += 1
        if count > retry_max:
            print("Downloading failed!")
    except Exception:
        print("Downloading failed!")
    print('')  # 下载完成换行
    return

@type_check  # url类型判断装饰器
def save_file1(url, dir_path=None, name=None, extension_default=None, mode='wb'):
    """保存图片，requests模块"""
    # check argument type
    if dir_path is None:
        dir_path = os.path.dirname(__file__)  # 获得当前文件目录
    elif not os.path.exists(dir_path):
        os.mkdir(dir_path)  # "./dir"当前目录下dir文件夹
    else:
        if not os.path.isdir(dir_path):  # dir_path路径是否为文件夹
            raise OSError("dir path is not folder")

    if name is not None:  # 给定存储文件名时
        name_extension_temp = url.split('/')[-1].split('?')[0]  # 从url中提取名字+扩展名
        extension_temp = re.findall(r'\.(.*?)$', name_extension_temp[-5:], re.S)  # 从url中提取的文件扩展名
        if extension_default is not None:  # 给定扩展名缺省值时
            if len(extension_temp) == 0:  # url中扩展名不存在时
                name_extension = "{0}.{1}".format(name, extension_default)
            else:  # url中扩展名存在时
                name_extension = "{}.{}".format(name, extension_temp[0])
        else:  # 未给定扩展名缺省值时
            if len(extension_temp) == 0:  # url中扩展名不存在时
                # name_extension = "{}.{}".format(name, 'txt')  # 默认以txt格式保存
                name_extension = name  # 没有扩展名
            else:  # url中扩展名存在
                name_extension = "{}.{}".format(name, extension_temp[0])
    else:  # 未给定存储文件名时
        name_extension_temp = url.split('/')[-1].split('?')[0]  # 从url中提取名字+扩展名
        extension_temp = re.findall(r'\.(.*?)$', name_extension_temp[-5:], re.S)  # 从url中提取的文件扩展名
        if extension_default is not None:  # 给定扩展名缺省值时
            if len(extension_temp) == 0:  # url中扩展名不存在时
                name_extension = "{}.{}".format(name_extension_temp, extension_default)
            else:  # url中扩展名存在时
                name_extension = name_extension_temp
        else:  # 未给定扩展名缺省值时
            name_extension = name_extension_temp
        name_extension = re.sub(r'[?\\*|"<>:/]', ' ', name_extension)  # 清洗掉Windows系统非法文件名的字符串

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        with open(os.path.join(dir_path, "{}".format(name_extension)), mode) as f:
            f.write(response.content)
        print("Image saved successfully".format(" " * 10))
    except requests.RequestException:
        print("request error: {}".format(url))  # 打印错误信息
        # raise Exception("request error: {}".format(img_src))  # 抛出异常错误
    return


if __name__ == '__main__':
    print('Code execution begins\n')
    start = time.time()
    # 主程序代码
    base_url = "http://img.pconline.com.cn/images/upload/upc/tx/wallpaper/1305/24/c1/21266756_1369385228661.jpg"
    path = './image'
    # save_file(base_url, dir_path=path, name=None, extension=None, timeout=5, retry_max=5)
    save_file1(base_url, dir_path=path, name=None, extension_default=None)
    # 主程序代码完成
    print('\nCode execution finished within {0:^.4f} seconds'.format(time.time() - start))  # 代码运行时间，以秒计
    print('Code execution finished at %s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
