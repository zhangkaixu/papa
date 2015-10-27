#!/usr/bin/env python2
#coding:utf8
from __future__ import print_function
import sys
import pybloomfilter as pybf
import requests
import threading
import Queue
import json
import time
from lxml import etree
from io import StringIO
import os

class Rule:
    def gen_seeds(self):
        pass

    def parse(self, url, content, tree):
        pass

class BaiduNews(Rule) :
    def gen_seeds(self):
        yield ('sleep', 10)
        yield ('forget',)
        yield ('dynamic', 'http://news.baidu.com/', 2)

    def parse(self, url, content, tree):
        for e in tree.xpath('//a[@href]'):
            url = e.get('href')
            url = url.partition('?')[0]
            url = url.partition('#')[0]

            if e.text and len(e.text) > 10 and url.startswith('http://'):
                yield ('save', url)
                continue
            if url.startswith('http://news.baidu.com/'):
                yield ('dynamic', url)
                continue

class NetEase(Rule) :
    def gen_seeds(self):
        yield ('sleep', 300) # rest for 300 seconds
        yield ('forget',) # forget all the dynamic 
        yield ('dynamic', 'http://news.163.com/', 2)

    def parse(self, url, content, tree):
        for e in tree.xpath('//a[@href]'):
            url = e.get('href')
            if not url.startswith('http://news.163.com/') :continue
            url = url.partition('?')[0]
            url = url.partition('#')[0]
            if url.endswith('.html') :
                yield ('save', url)
                yield ('static', url, 0)
            else :
                yield ('dynamic', url)

def quickstart(rule, data_dir = '.'):
    Scheduler(data_dir, rule).run()


class Scheduler :
    def __init__(self, data_dir, rule):
        self.data_dir = data_dir
        self.rule = rule
        os.system('mkdir -p ' + data_dir)

        url_file = os.path.join(data_dir, 'urls.urls')
        savefile = open(url_file, 'a' if os.path.exists(url_file) else 'w')


        parsed_ff = os.path.join(data_dir, 'parsed.bloomfilter')
        parsed_filter = pybf.BloomFilter(
                pybf.BloomFilter.ReadFile if os.path.exists(parsed_ff) else 10000000, 
                0.0001, parsed_ff)

        saved_ff = os.path.join(data_dir, 'saved.bloomfilter')
        saved_filter = pybf.BloomFilter(
                pybf.BloomFilter.ReadFile if os.path.exists(saved_ff) else 10000000, 
                0.0001, saved_ff)

        
        self.dyn_filter = set()
        self.queue = Queue.LifoQueue()
        if os.path.exists(os.path.join(self.data_dir, 'queue.json')):
            for item in reversed([json.loads(line) for line in open(os.path.join(self.data_dir,
                'queue.json'))]):
                self.queue.put(item)
            os.remove(os.path.join(self.data_dir, 'queue.json'))
        self.saved_filter = saved_filter
        self.parsed_filter = parsed_filter
        self.savefile = savefile

    def __del__(self):
        f = open(os.path.join(self.data_dir, 'queue.json'), 'w')
        while not self.queue.empty():
            s = json.dumps(self.queue.get()).encode('utf8')
            print(s, file =f)
        f.close()
        print('bye~')
    
    def run(self):
        while True:
            if self.queue.empty():
                for cmd in self.rule.gen_seeds():
                    self.deal_cmd(('', 1), cmd)
            if self.queue.empty():
                self.savefile.flush()
                print('nothing to do')
                return
            item = self.queue.get()
            self.savefile.flush()

            if item[0] == 'sleep' :
                try :
                    for i in range(item[1]) :
                        time.sleep(1)
                        print('sleep %d of %d seconds'%(i, item[1]), end = '\r', file = sys.stderr)
                        sys.stderr.flush()
                except KeyboardInterrupt, e:
                    self.savefile.flush()
                    print('do some saving')
                    return
                continue
            if item[0] == 'forget' :
                self.dyn_filter.clear()
                continue
            try :
                if item[0] in self.parsed_filter : continue
                print('queuesize', self.queue.qsize(), 'fetching', *item)

                if item[1] >= 0 :
                    res = self.fetch(item[0])
                    if res != None :
                        cmds = self.rule.parse(*res)
                        for cmd in cmds:
                            self.deal_cmd(item, cmd)
                    self.parsed_filter.add(item[0])
                if self.queue.empty():
                    print('queue is empty')
            except KeyboardInterrupt, e:
                print(e)
                print('do some saving')
                self.savefile.flush()
                return
                pass

    def fetch(self, url):
        p = etree.HTMLParser()
        try:
            cont = requests.get(url, timeout = 3).content
        except Exception, e:
            return 
        for codec in ['utf8', 'gb18030'] :
            try :
                content = cont.decode(codec)
                break
            except :
                continue
        else :
            return

        try :
            tree = etree.parse(StringIO(content), p)
        except :
            return
        return url, content, tree

    def deal_cmd(self, poped, cmd):
        deg = poped[1]
        action = cmd[0]
        url = None
        if len(cmd) > 1 :
            url = cmd[1]

        if action == 'forget':
            self.queue.put(('forget',))
            return
        if action == 'sleep' :
            self.queue.put(('sleep', url))
            return

        ### save url
        if action == 'save' :
            if not self.saved_filter.add(url):
                print(*cmd[1:], sep = '\t', file = self.savefile)
                print('save', url)
            return

        c_deg = deg - 1
        if len(cmd) > 2 :
            c_deg = cmd[2] - 1
        ### dynamic
        if action == 'dynamic' :
            if url not in self.dyn_filter and c_deg >= 0 :
                self.dyn_filter.add(url)
                print('push dynamic', url, c_deg)
                if self.queue.qsize() < 100000 :
                    self.queue.put((url, c_deg))
            return

        if action == 'static' :
            if url not in self.parsed_filter and url not in self.dyn_filter and c_deg >= 0 :
                if self.queue.qsize() < 100000 :
                    self.queue.put((url, c_deg))
            return

#if __name__ == '__main__':
#    data_dir = 'netease'
#    sch = Scheduler(data_dir, NetEase())
#    sch.run()
