#!/usr/bin/env python
# -*- coding: utf-8 -*-
from zipfile import ZipFile
import os
import shutil
import hashlib


class Epub:
    creator = 'zhangyao'

    def __init__(self, bookname, description, htmlquery):
        self.bookname = bookname
        self.description = description
        self.htmlquery = htmlquery
        self.bookdir = 'static/books/{}'.format(self.bookname)
        self.basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.fullpath = os.path.join(self.basedir, os.path.normpath(self.bookdir), 'tmp')

    def stringrandom(self, string):
        """
        将小说名md5加密
        :param string: 小说名
        :return: 加密字符串
        """
        hash1 = hashlib.md5()
        hash1.update(bytes(string, encoding='utf-8'))
        return hash1.hexdigest()

    def dirinit(self):
        # 小说网页存放目录初始化
        if os.path.exists(self.fullpath):
            shutil.rmtree(self.fullpath)
        os.makedirs(self.fullpath)

    def staticfileinit(self):
        with open('{}/mimetype'.format(self.fullpath), 'w', encoding='utf8') as f:
            f.write('application/epub+zip')

        os.mkdir('{}/META-INF'.format(self.fullpath))

        with open('{}/META-INF/container.xml'.format(self.fullpath), 'w', encoding='utf8') as f:
            f.write('''<?xml version="1.0" encoding="UTF-8" ?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
           <rootfiles> <rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/> </rootfiles>
        </container>
        ''')

        os.mkdir('{}/OPS'.format(self.fullpath))

        imgurl = 'static/images/novel/{}.jpg'.format(self.stringrandom(self.bookname))
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.path.normpath(imgurl))

        if os.path.isfile(filepath):  # 如果有cover.jpg, 用来制作封面
            shutil.copyfile(filepath, '{}/OPS/cover.jpg'.format(self.fullpath))
            print('Cover.jpg found!')

    def dynamicfileinit(self):
        opfcontent = '''<?xml version="1.0" encoding="UTF-8" ?>
            <package version="2.0" unique-identifier="PrimaryID" xmlns="http://www.idpf.org/2007/opf">
            <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
            {metadata:s}
            <meta name="cover" content="cover"/>
            </metadata>
            <manifest>
            {manifest:s}
            <item id="ncx" href="content.ncx" media-type="application/x-dtbncx+xml"/>
            <item id="cover" href="cover.jpg" media-type="image/jpeg"/>
            </manifest>
            <spine toc="ncx">
            {ncx:s}
            </spine>
            </package>
            '''

        dc = '<dc:{name:s}>{value:s}</dc:{name:s}>'
        item = "<item id='{id:s}' href='{url:s}' media-type='application/xhtml+xml'/>"
        itemref = "<itemref idref='{id:s}'/>"

        metadata = '\n'.join([
            dc.format(**{'name': 'title', 'value': self.bookname}),
            dc.format(**{'name': 'creator', 'value': self.creator}),
            dc.format(**{'name': 'description', 'value': self.description}),
        ])

        manifest = []
        ncx = []
        htmllist = []

        for htmlitem in self.htmlquery:
            with open('{}/OPS/{}'.format(self.fullpath, htmlitem[0]), 'w', encoding='utf8') as f:
                htmlcontent = '<h1>{}</h1>{}'.format(*htmlitem)
                f.write(htmlcontent)

            manifest.append(item.format(**{'id': htmlitem[0], 'url': htmlitem[0]}))
            ncx.append(itemref.format(id=htmlitem[0]))
            htmllist.append(htmlitem[0])

        manifest = '\n'.join(manifest)
        ncx = '\n'.join(ncx)

        with open('{}/OPS/content.opf'.format(self.fullpath), 'w', encoding='utf8') as f:
            f.write(opfcontent.format(**{'metadata': metadata, 'manifest': manifest, 'ncx': ncx}))

        ncx = '''<?xml version="1.0" encoding="utf-8"?>
            <!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
            <ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
            <head>
              <meta name="dtb:uid" content=" "/>
              <meta name="dtb:depth" content="-1"/>
              <meta name="dtb:totalPageCount" content="0"/>
              <meta name="dtb:maxPageNumber" content="0"/>
            </head>
             <docTitle><text>{title:s}</text></docTitle>
             <docAuthor><text>{creator:s}</text></docAuthor>
            <navMap>
            {navpoints:s}
            </navMap>
            </ncx>
            '''

        navpoint = '''<navPoint id='{:s}' class='level1' playOrder='{:d}'>
            <navLabel> <text>{:s}</text> </navLabel>
            <content src='{:s}'/></navPoint>'''

        navpoints = []
        for i, item in enumerate(htmllist):
            navpoints.append(navpoint.format(item, i + 1, item, item))

        with open('{}/OPS/content.ncx'.format(self.fullpath), 'w', encoding='utf8') as f:
            f.write(ncx.format(**{
                'title': self.bookname,
                'creator': self.creator,
                'navpoints': '\n'.join(navpoints)}))

    def createpub(self):
        self.dirinit()
        self.staticfileinit()
        self.dynamicfileinit()

        cachedir = os.path.join(self.basedir, os.path.normpath(self.bookdir))
        filename = '{}/{}.epub'.format(cachedir, self.bookname)
        epubfile = ZipFile(filename, 'w')
        os.chdir(self.fullpath)
        for d, ds, fs in os.walk('.'):
            for f in fs:
                epubfile.write(os.path.join(d, f))
        epubfile.close()

        print("Done")
