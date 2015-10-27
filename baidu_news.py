#!/usr/bin/env python2
#coding:utf8
from __future__ import print_function
import papa
import json
import datetime

class BaiduNews() :
    def gen_seeds(self):
        yield ('sleep', 300)
        yield ('forget',)
        yield ('dynamic', 'http://news.baidu.com/', 1)

    def parse(self, url, content, tree):
        for e in tree.xpath('//a[@href]'):
            url = e.get('href')
            url = url.partition('?')[0]
            url = url.partition('#')[0]

            if e.text and len(e.text) > 10 and url.startswith('http://'):
                data = {'url':url.encode('utf8'), 'title':e.text.encode('utf8'), 
                        'extract_date':str(datetime.date.today()) }
                yield ('save', url, json.dumps(data, ensure_ascii = False))

if __name__ == '__main__':
    papa.quickstart(BaiduNews(), 'baidu_news')
