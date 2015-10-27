#!/usr/bin/env python2
#coding:utf8
from __future__ import print_function
import papa


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
                yield ('save', url, e.text.encode('utf8'))

if __name__ == '__main__':
    papa.quickstart(BaiduNews(), 'baidu_news')
