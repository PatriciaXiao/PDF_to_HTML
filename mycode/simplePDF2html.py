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

import sys, gc

reload(sys)
sys.setdefaultencoding('utf8') #设置默认编码
# sys.getdefaultencoding() #'ascii'


class PDF2HTML(object):
	def __init__(self, pdf_path, html_path, password="", codec='utf-8'):
		self.pdf_path = pdf_path
		self.html_path = html_path
		self.codec = codec
		self.reader = open(pdf_path, 'rb')
		self.writer = open(html_path, 'w') #'a'
		self.password = password
		self.device = None
		self.indent = '  '
		self.level = 0
		# http://webdesign.about.com/od/styleproperties/p/blspfontweight.htm
		self.fontweight_dict = {
			self.chinese_str('ABCDEE+黑体'): 'bold',
			self.chinese_str('ABCDEE+宋体'): 'normal'
		}
		self.endmark_list = [
			self.chinese_str('：'), 
			self.chinese_str(':'),
			self.chinese_str('。'), 
			self.chinese_str('？'), 
			self.chinese_str('?'),
			self.chinese_str('！'), 
			self.chinese_str('!')
		]
		# print "init"
	def __enter__(self):
		# print "enter"
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		# print "exits"
		return
	def __del__(self):
		# print "deleted"
		self.reader.close()
		self.writer.close()
		if self.device:
			self.device.close()
		sys._clear_type_cache() 
		gc.collect()

	def write(self, content):
		self.writer.write(self.level * self.indent + str(content).encode('utf-8') + '\n')

	def chinese_str(self, content, codec = 'utf-8'):
		return u'{0}'.format(content).encode('gbk')

	def get_last_char(self, content):
		length = len(content)
		return content[length - 2:]

	def convert(self):
		pass

	def writeHTML(self):
		pass
	def writeHead(self):
		pass
	def writeBody(self):
		pass


class simplePDF2HTML(PDF2HTML):
	# 转换格式主函数
	def convert(self):
		print "initializing the parser setting..."
		self.simpleParse()
		# print "simple convert"
		print "writing to the HTML file..."
		self.writeHTML()
		pass

	def simpleParse(self):
		#创建一个PDF文档解析器对象
		self.parser = PDFParser(self.reader)
		#创建一个PDF文档对象存储文档结构
		self.document = PDFDocument(self.parser, self.password)
		#检查文件是否允许文本提取
		if not self.document.is_extractable:
			raise PDFTextExtractionNotAllowed
		#创建一个PDF资源管理器对象来存储共享资源
		self.rsrcmgr = PDFResourceManager()
		#创建一个PDF设备对象
		self.laparams = LAParams()
		#创建一个PDF页面聚合对象
		self.device = PDFPageAggregator(self.rsrcmgr, laparams=self.laparams)
		#创建一个PDF解析器对象
		self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.device)
		#字符转换规则
		self.replace=re.compile(r'\s+')

	def writeHTML(self):
		# print "write?"
		self.write('<!DOCTYPE html>')
		self.write('<html>')
		self.level += 1
		# write header
		self.writeHead()
		self.writeBody()
		self.level -= 1
		self.write('</html>')

	def writeHead(self):
		self.write('<head>')
		self.level += 1
		self.write('<meta http-equiv="Content-Type" content="text/html; charset=%s">\n' % self.codec)
		self.write('<title>PDF格式转HTML</title>')
		self.level -= 1
		self.write('</head>')

	def writeBody(self):
		self.write('<body>')
		self.level += 1
		# 循环遍历列表，每次处理一个page的内容
		page_idx = 1
		para_end = False
		prev_text = None
		prev_size = None
		prev_weight = None
		prev_align = None
		for page in PDFPage.create_pages(self.document):
			# print "page " + str(page_idx)
			self.interpreter.process_page(page)
			# 接受该页面的LTPage对象
			layout=self.device.get_result()
			# 页面左右上下
			page_xrange = (layout.x0, layout.x1)
			page_yrange = (layout.y0, layout.y1)
			# print page_xrange, page_yrange
			most_left, most_right = self.get_indent_info(layout, page_xrange)
			for x in layout:
				if(isinstance(x, LTTextBoxHorizontal)):
					fontname, fontsize, location, line_width = self.get_font(x)
					text=re.sub(self.replace,'',x.get_text())
					fontweight = self.fontweight_dict[fontname]
					align = self.get_align(page_xrange, location, most_left, most_right, text)
					'''
					print location
					print page_xrange
					print text
					raw_input()
					'''
					if prev_text:
						last_char = self.get_last_char(prev_text)
						para_end = self.if_para_end(page_xrange, prev_linewidth, last_char, \
							 prev_size, prev_weight, prev_align, fontsize, fontweight, align)	
					if para_end:
						# self.write('<p style="font-size:{1}px;font-weight:{2}" align="{3}">{0}</p>'.format( \
						# 		text, fontsize, fontweight, align
						# 	))
						self.write('<p style="font-size:{1}px;font-weight:{2}" align="{3}">{0}</p>'.format( \
								prev_text, prev_size, prev_weight, prev_align
							))
						para_end = False
						prev_text = None
					
					if prev_text:
						prev_text = prev_text + text
						prev_linewidth = line_width
					else:
						prev_text = text
						prev_size = fontsize
						prev_weight = fontweight
						prev_align = align
						prev_linewidth = line_width
			page_idx += 1
		
		if prev_text:
			self.write('<p style="font-size:{1}px;font-weight:{2}" align="{3}">{0}</p>'.format( \
					prev_text, prev_size, prev_weight, prev_align
				))
		self.level -= 1
		self.write('</body>')


	def get_font(self, x):
		default_fontname = self.chinese_str('ABCDEE+宋体')
		for line in x:
			line_width = line.width
			line_height = line.height
			location = (line.x0, line.x1)

			'''
			print line.width
			print line.get_text()
			raw_input()
			'''
			# print line # LTTextLineHorizontal
			# print line.x0, line.x1
			for char in line:
				if isinstance(char, LTAnno):
					continue
				else:
					fontsize = char.size
					fontname = char.fontname #ABCDEE-黑体 即加粗 ABCDEE-宋体 即不加粗
					if fontname in self.fontweight_dict.keys():
						return fontname, fontsize, location, line_width
			return default_fontname, line_height, location, line_width

	def get_indent_info(self, layout, page_xrange):
		most_left = page_xrange[1]
		most_right = page_xrange[0]
		for x in layout:
			if(isinstance(x, LTTextBoxHorizontal)):
				fontname, fontsize, location, line_width = self.get_font(x)
				if location[0] < most_left:
					most_left = location[0]
				if location[1] > most_right:
					most_right = location[1]
		return most_left, most_right

	def get_align(self, page_xrange, location, most_left, most_right, debug=None):
		threshold = 2.
		left_padding = location[0] - page_xrange[0]
		right_padding = page_xrange[1] - location[1]
		delta_left = most_left - page_xrange[0]
		delta_right = page_xrange[1] - most_right
		if left_padding < threshold * delta_left:
			return "left"
		elif right_padding < threshold * delta_right:
			return "right"
		else:
			return "center"

	def if_para_end(self, page_xrange, line_width, last_char, \
			prev_size, prev_weight, prev_align, fontsize, fontweight, align):
		# print prev_size, prev_weight, prev_align, fontsize, fontweight, align
		'''
		print prev_location, page_xrange, most_right
		print debug
		raw_input()
		'''
		# raw_input()
		if prev_align == "center" or prev_align == "right":
			# print "font"
			return True
		total_width = page_xrange[1] - page_xrange[0]
		threshold = 0.5
		if line_width < threshold * total_width:
			# print "shorter than usual"
			return True
		if prev_align != align:
			# print "alignment difference"
			return True
		if last_char not in self.endmark_list:
			return False
		
		if prev_size != fontsize:
			# print "size difference"
			return True
		if prev_weight != fontweight:
			# print "weight difference"
			return True
		
		
		return False
