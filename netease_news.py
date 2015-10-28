#!/usr/bin/env python2
#coding:utf8
from __future__ import print_function
import papa
import json
import datetime

class NetEase() :
    def gen_seeds(self):
        yield ('sleep', 300) # rest for 300 seconds
        yield ('forget',) # forget all the dynamic 
        yield ('dynamic', 'http://news.163.com/', 2)

    def parse(self, url, content, tree):
        print(url)
        try :
            for e in tree.xpath('//a[@href]'):
                url = e.get('href')
                if not url.startswith('http://news.163.com/') :continue
                url = url.partition('?')[0]
                url = url.partition('#')[0]

                if 'photo' in url : continue
                if (url.endswith('.html') and e.text is not None):
                    
                    data = {'url':url.encode('utf8'), 'title':e.text.encode('utf8'), 
                            'extract_date':str(datetime.date.today()) }
                    yield ('save', url, json.dumps(data, ensure_ascii = False))

                    if 'editor' in url : continue
                    yield ('static', url, 2)
                else :
                    yield ('dynamic', url)
        except :
            return

if __name__ == '__main__':
    papa.quickstart(NetEase(), 'netease_news')
