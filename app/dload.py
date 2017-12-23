#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
from app import models
from urllib import request
from django.utils import timezone
from app import epub
import re
import os
import time
import hashlib

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
                  'like Gecko) Chrome/60.0.3112.78 Safari/537.36 OPR/47.0.2631.55',
}


def stringrandom(string):
    """
    将小说名md5加密
    :param string: 小说名
    :return: 加密字符串
    """
    hash1 = hashlib.md5()
    hash1.update(bytes(string, encoding='utf-8'))
    return hash1.hexdigest()


def getnum(href):
    """
    通过正则将传入的url地址获取核心的数字地址
    :param href: url地址
    :return: 返回数字num
    """
    pattern = re.compile(r'.*/(\d+).html')
    match = pattern.match(href)
    if match:
        return match.group(1)


def gethtml(baseurl):
    """
    初始化小说
    通过完整的url，先将小说目录网页下载下来，然后提取网页中所有章节链接，经过getnum函数
    处理，最后取得地址集合并存入数据库。
    :param baseurl: 小说目录网页
    :return: 地址集合
    """
    today = timezone.now()
    urlquery = models.Novel.objects.filter(srcurl=baseurl)
    if urlquery:
        updatetime = urlquery.first().updatetime
        urlquery.update(updatetime=today)
        novelid = urlquery.first().id
        if updatetime == today:
            print('无需下载')
            return novelid
        else:
            try:
                html = pq(baseurl, headers=header, encoding="utf-8")
                # 更新小说章节
                upcontentb(novelid, html)
                return novelid
            except Exception as e:
                return '出现错误：{}'.format(e)
    else:
        html = pq(baseurl, headers=header, encoding="utf-8")
        name = html('h1').text()
        content = html('#intro').text()
        # 小说图片下载
        imgurl = 'static/images/novel/{}.jpg'.format(stringrandom(name))
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.path.normpath(imgurl))
        if not os.path.isfile(filepath):
            imgpath = html('#fmimg img').attr("src")
            if not imgpath:
                imgpath = html("meta[property='og:image']").attr('content')
            request.urlretrieve(imgpath, filepath)

        novel_dict = {'name': name,
                      'content': content,
                      'imgurl': imgurl,
                      'srcurl': baseurl,
                      'updatetime': today,
                      'status': 1
                      }
        obj = models.Novel.objects.create(**novel_dict)
        # 小说编号
        novelid = obj.id
        # 写入小说章节到novelContent表中
        upcontentb(novelid, html)
        return novelid


def upcontentb(novelid, html):
    """
    初始化小说章节到novelContent表格中
    :param novelid: 书籍编号
    :param html: 首页html代码
    :return:
    """
    # 获取这本小说的所有记录
    preresult = models.NovelContent.objects.filter(novelid=novelid)
    lastquery = models.NovelContent.objects.last()
    if preresult:
        # 查询表中最后一条记录
        lastid = lastquery.id
        # 查询这本书的最后一次记录
        preurl = preresult.last().id
        # 获取novelContent中已经存入的章节编号
        storeurl = preresult.values_list('srcnum')
        srclist = [i[0] for i in storeurl]
    else:
        preurl = 0
        srclist = []
        lastid = lastquery.id if lastquery else 0

    chapter = html('#list')('a')
    # 批量插入数据的列表
    novel_content_list_to_insert = list()
    # 遍历所有章节，判断新的章节
    chaplen = len(list(chapter.items()))
    flag = 0
    for i, c in enumerate(chapter.items()):
        srcnum = getnum(c.attr("href"))
        if srcnum in srclist:
            continue
        # 修改上一次下载最后一行的下一页记录,但是只能在第一次添加新章节修改
        if flag == 0:
            models.NovelContent.objects.filter(id=preurl).update(nexturl=lastid + 1)
            flag += 1
        title = c.text()
        # 最后一个添加的页面的下一页url地址为/book/
        if i + 1 == chaplen:
            nexturl = '/book/'
        else:
            nexturl = lastid + 2

        noverconentdict = {'id': lastid + 1,
                           'status': 0,
                           'title': title,
                           'preurl': preurl,
                           'nexturl': nexturl,
                           'srcnum': srcnum,
                           'novelid_id': novelid,
                           }
        lastid += 1
        preurl = lastid
        novel_content_list_to_insert.append(models.NovelContent(**noverconentdict))

    if novel_content_list_to_insert:
        models.NovelContent.objects.bulk_create(novel_content_list_to_insert)


def bookdetail(bookid):
    """
    提取书籍详细信息
    :param bookid: 书籍id编号
    :return: 返回书籍信息字典
    """
    bookdict = models.Novel.objects.filter(id=bookid).values().first()

    chapterquery = models.NovelContent.objects.filter(novelid=bookdict['id']).values_list('title', 'id')
    bookdict['chapterquery'] = chapterquery

    readrec = models.ReadProgress.objects.filter(novelid=bookid).values('chapterid_id').first()
    if not readrec:
        readrec = {'chapterid_id': models.NovelContent.objects.filter(novelid=bookid).first().id}

    bookdict.update(readrec)
    return bookdict


def cachedownload(bookid, start=None, end=None):
    """
    下载全本小说内容存放到数据库中
    :param bookid: 书籍编号id
    :param start 开始下载的编号
    :param end   结束下载的编号
    :return:
    """
    if start and end:
        # 下载指定起始章节
        downquery = models.NovelContent.objects.filter(status=0, novelid=bookid, id__gte=start, id__lte=end
                                                       ).values_list('srcnum')
    elif start:
        downquery = models.NovelContent.objects.filter(status=0, novelid=bookid, id__gte=start).values_list('srcnum')
    else:
        # 从数据库获取所有未下载章节
        downquery = models.NovelContent.objects.filter(status=0, novelid=bookid).values_list('srcnum')
    # 获取源站地址
    baseurl = models.Novel.objects.filter(id=bookid).first().srcurl

    downlist = [i[0] for i in downquery]
    for num in downlist:
        novel = pq('{}{}.html'.format(baseurl, num), headers=header, encoding="utf-8")
        txt = novel('#content')
        if txt:
            models.NovelContent.objects.filter(novelid__srcurl=baseurl, srcnum=num).update(content=txt, status=1)
            time.sleep(3)


def downloadone(bookid, chapterid):
    """
    递归下载指定网页，当访问一个新的网页，默认没有内容，因此调用本函数下载。当然，如果有内容直接返回内容。
    :param bookid: 书籍编号
    :param chapterid: 章节编号
    :return: 返回章节内容
    """
    chapterquery = models.NovelContent.objects.filter(status=1, id=chapterid, novelid=bookid). \
        values('title', 'content', 'preurl', 'nexturl', 'novelid', 'id')

    if chapterquery:
        return chapterquery.first()
    else:
        cachedownload(bookid, chapterid, chapterid)
        return downloadone(bookid, chapterid)


def searchbook(bookname):
    """
    搜索书籍，目前只能搜索一家网站
    :param bookname: 书名
    :return: 返回网页内容
    """
    searchurl = 'http://zhannei.baidu.com/cse/search?s=5199337987683747968&ie=utf-8&q={}'. \
        format(request.quote(bookname))
    html = pq(searchurl, headers=header, encoding="utf-8")
    ret = html('.result-item:first')
    return ret


def readrecord(bookid, chapterid):
    """
    将阅读进度记录下来，以供网页的继续阅读功能使用
    :param bookid:
    :param chapterid:
    :return:
    """
    recordquery = models.ReadProgress.objects.filter(novelid=bookid)
    if recordquery:
        recordquery.update(chapterid_id=chapterid)
    else:
        models.ReadProgress.objects.create(novelid_id=bookid, chapterid_id=chapterid)


def downloadepub(bookid, chapterid):
    """
    提供epub电子书下载
    :param bookid:  书id
    :param chapterid:  章节id
    :return: 返回书名，用于拼接下载地址
    """
    # 从数据库读取需要的小说内容
    htmlquery = models.NovelContent.objects.filter(status=1, novelid=bookid, id__gte=chapterid).values_list('title',
                                                                                                            'content')
    # 读取书名和简介
    (bookname, description) = models.Novel.objects.filter(id=bookid).values_list('name', 'content').first()
    f = epub.Epub(bookname, description, htmlquery)
    f.createpub()
    return bookname
