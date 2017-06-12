#!/usr/bin/python
#-*- coding: utf-8 -*-

from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import *
import re

# it works!!!
# http://blog.csdn.net/fighting_no1/article/details/51038942
# http://www.cnblogs.com/RoundGirl/p/4979267.html

#打开一个pdf文件
# fp = open(u'../test/simple1.PDF', 'rb') # also works (have to be like this when name include Chinese characters)
fp = open('data/simple1.PDF', 'rb')
ofname = 'data/simple1_content2.txt'
#创建一个PDF文档解析器对象
parser = PDFParser(fp)
#创建一个PDF文档对象存储文档结构
#提供密码初始化，没有就不用传该参数
password = ""
document = PDFDocument(parser, password)
# document = PDFDocument(parser)
#检查文件是否允许文本提取
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed
#创建一个PDF资源管理器对象来存储共享资源
#caching = False不缓存
# rsrcmgr = PDFResourceManager(caching = False)
rsrcmgr = PDFResourceManager()
# 创建一个PDF设备对象
laparams = LAParams()
# 创建一个PDF页面聚合对象
device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#创建一个PDF解析器对象
interpreter = PDFPageInterpreter(rsrcmgr, device)
#处理文档当中的每个页面

# doc.get_pages() 获取page列表
#for i, page in enumerate(document.get_pages()):
#PDFPage.create_pages(document) 获取page列表的另一种方式
replace=re.compile(r'\s+');
# 循环遍历列表，每次处理一个page的内容
page_idx = 1
# with open(ofname, 'a') as of:
with open(ofname, 'w') as of:
    for page in PDFPage.create_pages(document):
        print "****** page " + str(page_idx) + " ******"
        page_idx += 1
        interpreter.process_page(page)
        # 接受该页面的LTPage对象
        layout=device.get_result()
        # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
        # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等

        # print interpreter.textstate
        # print interpreter.fontmap
        '''
        print rsrcmgr.caching
        print rsrcmgr._cached_fonts
        '''
        # raw_input()
        print "page x(" + str(layout.x0) + ", " + str(layout.x1) + ")"
        print "page y(" + str(layout.y0) + ", " + str(layout.y1) + ")"
        for x in layout:
            #如果x是文本对象的话
            # if(isinstance(x, LTTextBoxHorizontal)):
            if(isinstance(x, LTTextBoxHorizontal)):
                
                for line in x:
                    # print line # LTTextLineHorizontal
                    for char in line:
                        if isinstance(char, LTAnno):
                            print char
                        else:
                            print char.size #LTAnno 没有size属性
                            print char.fontname #ABCDEE-黑体 即加粗 ABCDEE-宋体 即不加粗
                            ###
                            print char.adv
                            print char.matrix
                            ###
                            print "x(" + str(char.x0) + ", " + str(char.x1) + ")"
                            print "y(" + str(char.y0) + ", " + str(char.y1) + ")"
                            print "width:" + str(char.width) + ", height:" + str(char.height)
                            # raw_input()
                        break
                
                text=re.sub(replace,'',x.get_text())
                # text = x.get_text()
                if len(text)!=0:
                    #print text
                    #raw_input()
                    of.write(text.encode('utf-8') + '\n')


fp.close()
of.close()