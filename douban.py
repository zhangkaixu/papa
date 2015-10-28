#!/usr/bin/env python2
#coding:utf8
from __future__ import print_function
import papa
import json
import datetime
import time
import re

from lxml import etree
from io import StringIO

class Douban() :
    fetch_timeout = 5
    tag_from_book_anchor = re.compile(u'<a[^>]*href="([^"]*focus=book)">([^<]*)<')
    book_anchor = re.compile(u'<a[^>]*href="(http://book.douban.com/subject/[0-9]*/)"[^>]*>([^<]*)<', 
            re.S)

    book_from_tag_anchor = re.compile(u'<a[^>]*href="(http://book.douban.com/subject/[0-9]*/)[^>]*>([^<]*)<',
            re.S)
    tag_from_tag_anchor = re.compile(u'<a href="(\?start=[0-9]*)"')


    def gen_seeds(self):
        yield ('sleep', 300) # rest for 300 seconds
        yield ('forget',) # forget all the dynamic 
        #yield ('dynamic', 'http://www.douban.com/', 1)
        #yield ('dynamic', 'http://www.douban.com/tag/科幻/book', 1)
        yield ('dynamic', 'http://book.douban.com/subject/4105745/', 1)

        


    def parse(self, url, content, tree):
        p = etree.HTMLParser()
        time.sleep(5)
        print(url)
        urls = []
        root = url
        if type(root) != str:
            root = root.encode('utf8')
        f = open('tmp.html', 'w')

        print(content.encode('utf8'), file =f)
        f.close()

        """bookpage"""
        if 'subject' in root: 
            for x in re.findall(Douban.book_anchor, content):
                url, title = x
                title = title.strip()
                if not title : continue
                data = {'url':url.encode('utf8'), 'title':title.encode('utf8')}
                yield ('save', data['url'], json.dumps(data, ensure_ascii = False))
                yield ('static', url, 2)
                #print(url, title)

            for x in re.findall(Douban.tag_from_book_anchor, content):
                url, title = x
                url = url.partition('?')[0] + 'book'
                #print(url, title)
                data = {'url':url.encode('utf8'), 'title':title.encode('utf8')}
                yield ('save', data['url'], json.dumps(data, ensure_ascii = False))
                yield ('static', url, 2)

            bookinfo = {'url' : root}
            tree = etree.HTML(content)
            for x in tree.xpath('//div[@id="info"]'):
                info = etree.tostring(x, encoding = 'utf8')
                info = info.replace(' ','')
                info = info.replace('\n','')
                bookinfo['info'] = info
                break
            for x in tree.xpath('//span[@property="v:itemreviewed"]'):
                if x.text:
                    print(x.text)
                    bookinfo['title'] = x.text.encode('utf8')

            data = bookinfo

            if len(data) == 3:
                yield ('save', 'parsed:'+data['url'], json.dumps(data, ensure_ascii = False))
            return


        """tagpage"""
        if 'tag' in root:
            related = []
            for x in re.findall(Douban.tag_from_tag_anchor, content):
                url = x.encode('utf8')
                title = root.split('/')[-2]
                url = root.partition('?')[0] + url
                data = {'url':url, 'title':title}
                yield ('save', data['url'], json.dumps(data, ensure_ascii = False))
                yield ('static', url, 2)
            for x in re.findall(Douban.book_from_tag_anchor, content):
                url, title = x
                title = title.strip()
                if not title : continue
                related.append([url.encode('utf8'), title.encode('utf8')])
                #print(url, title)
                data = {'url':url.encode('utf8'), 'title':title.encode('utf8')}
                yield ('save', data['url'], json.dumps(data, ensure_ascii = False))
                yield ('static', url, 2)
            if related :

                data = {'url':root, 'related':related}
                yield ('save', 'parsed:'+data['url'], json.dumps(data, ensure_ascii = False))
            return

        if False:
            yield None


if __name__ == '__main__':
    papa.quickstart(Douban(), 'douban')
