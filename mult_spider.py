#!usr/bin/python#coding=utf-8
import threading
import urllib
import sys
from bs4 import BeautifulSoup
import time
import thread
import re
import Queue
import math
import random

mutex = threading.Lock()

#coding:utf8
class Stack:
  """模拟栈"""
  def __init__(self):
    self.items = []
     
  def isEmpty(self):
    return len(self.items)==0
   
  def push(self, item):
    self.items.append(item)
       
  def pop(self):
      return self.items.pop() 
   
  def peek(self):
    if not self.isEmpty():
      return self.items[len(self.items)-1]
 
  def size(self):
    return len(self.items) 
s=Stack()

def getHtml(url):
    #print "主页为:"+url
    page = urllib.urlopen(url)
    html = page.read()
    return html.decode('gbk').encode("utf-8")

def getHtml2(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html  

def getfans(url):
    """
    获取粉丝数量
    """
    mainPage = getHtml(url)
    scdStr = re.findall(r"关注的人.*?_blank\">.*?<", mainPage)    
    if len(scdStr) == 0:
        scdStr = re.findall(r"关注.*?_blank\">.*?<", mainPage)
    if len(scdStr) == 0:
        return 0
    strnum = re.findall(r"_blank\">.*?<", scdStr[0])[0][8:-1]
    num = int(strnum)
    #print "关注数量:"+str(num)
    return num

def getPeoples(url):
    """
    获取所有的关注者的url
    """
    mainPage = getHtml(url)
    scdPageUrl = re.findall(r"关注的人.*?a href=\".*?\"", mainPage)
    if len(scdPageUrl) == 0:
        scdPageUrl = re.findall(r"的人.*?a href=\".*?\"", mainPage)
    if len(scdPageUrl) == 0:
        return 0
    if getfans(url)%20 != 0:
        pagenum = int(getfans(url)/20)+1
    else:
        pagenum = int(getfans(url)) 
    ownername = re.findall(r"<title>.*?</title>", mainPage)[0]
    #print ownername[5:-16]+"关注数量:"+str(pagenum*20)
    scdPage = "" 
    scdPageUrl = scdPageUrl[0]
    scdPageUrl = "http://tieba.baidu.com"+re.findall(r"href=\".*?\"", scdPageUrl)[0][6:-1]
    #print pagenum
    secUrl = re.findall(r"/i/[0-9]{6,10}/concern\?pn=", getHtml2(scdPageUrl))
    if len(secUrl) != 0:
        PageUrl = "http://tieba.baidu.com"+secUrl[0] 
    else:
        PageUrl = scdPageUrl
    for i in range(pagenum):
        #print PageUrl+str(i)
        scdPage += getHtml2(PageUrl+str(i))
    #scdPage = getHtml2(scdPageUrl)
    peoplelist = re.findall(r"<a href=\"[^<\"]*?\" target=\"_blank\">[^>]*?</a></span>&nbsp", scdPage)
    lists = []
    for a in peoplelist:
        url = "http://tieba.baidu.com" + re.findall(r"href=\".*?\"", a)[0][6:-1]
        name = re.findall(r">.*?</a>", a)[0][1:-4]
        lists.append([name, url, '0'])
    return lists

url = "http://tieba.baidu.com/home/main?ie=utf-8&un=FightingTK&fr=itb"
dc = {"FT":{}}
used_list = []
thread_num = 20

list = Stack()
ls1 = getPeoples(url)
for a in ls1:
    print a[0]
    list.push(a)

used_list = []

for i in range(list.size()):
    list.items[i-1][2] = "1"
#####设置初始层深

class thread_tieba(threading.Thread):

    def __init__(self, name, id):
        super(thread_tieba,self).__init__()
        self.id = id
        self.loop = 0
        self.url = url

    def spider(self):
        """
        Push 所有索引,depth+1
        Pop头部索引,depth-1
        加上锁
        """
        depth = 0
        if mutex.acquire():  
            b = list.pop()
        mutex.release()
        depth = int(b[2])
        print " " * 5 * depth + b[0]+"出栈"+" "+str(self.id)  ###输出名字###
        try:
            ls = getPeoples(b[1])
        except Exception as e:
            return 0
        if ls == 0:
            return 0
        if depth<2: 
            for a in ls:
                a[2] = str(depth+1)
                list.push(a)
                print " " * 5 * (depth+1) + a[0]+"入栈"+" "+str(self.id)

    def run(self):
        while(True):
            self.spider()
            if list.size() == 0:
                break
        print "self.id"+str(self.id)+" run"

for i in range(thread_num):
    tt = thread_tieba(str(i), i)
    tt.start()


