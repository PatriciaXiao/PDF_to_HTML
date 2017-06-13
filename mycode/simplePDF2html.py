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
import operator # 为了排序

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
			self.chinese_str('!'),
			self.chinese_str('；')
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
		return content[length - 1:]

	def sort_dict_by_val(self, dictdata, reverse=True):
		return sorted(dictdata.items(), key=operator.itemgetter(1), reverse=reverse)

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
		self.write('<style>')
		self.level += 1
		self.write('p {')
		self.level += 1
		self.write('text-indent: 2.0em;')
		self.level -= 1
		self.write('};')
		self.level -= 1
		self.write('</style>')
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
			content_xrange, indent_list, fontsize_list = self.get_indent_info(layout, page_xrange)
			content_width = content_xrange[1] - content_xrange[0]
			major_indents, map_indents, major_size = self.get_conclude(indent_list, fontsize_list)
			raw_input()
			for x in layout:
				if(isinstance(x, LTTextBoxHorizontal)):
					fontname, fontsize, location, line_width = self.get_font(x)
					text=re.sub(self.replace,'',x.get_text())
					# text = x.get_text()
					fontweight = self.fontweight_dict[fontname]
					align = self.get_align(content_xrange, location, line_width, fontsize, major_size, debug=text)
					if prev_text:
						last_char = self.get_last_char(prev_text)
						para_end = self.if_para_end(prev_content_width, prev_linewidth, last_char, \
							 prev_size, prev_weight, prev_align, fontsize, fontweight, align, \
							 debug = prev_text)	
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
						prev_content_width = content_width
					else:
						prev_text = text
						prev_size = fontsize
						prev_weight = fontweight
						prev_align = align
						prev_linewidth = line_width
						prev_content_width = content_width
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
			line_height = round(line.height)
			location = (round(line.x0), round(line.x1))
			# print line # LTTextLineHorizontal
			for char in line:
				if isinstance(char, LTAnno):
					continue
				else:
					fontsize = round(char.size)
					fontname = char.fontname #ABCDEE-黑体 即加粗 ABCDEE-宋体 即不加粗
					if fontname in self.fontweight_dict.keys():
						return fontname, fontsize, location, line_width
			return default_fontname, line_height, location, line_width

	def get_indent_info(self, layout, page_xrange):
		most_left = page_xrange[1]
		most_right = page_xrange[0]
		indent_list = {}
		fontsize_list = {}
		for x in layout:
			if(isinstance(x, LTTextBoxHorizontal)):
				fontname, fontsize, location, line_width = self.get_font(x)
				if location[0] < most_left:
					most_left = location[0]
				if location[1] > most_right:
					most_right = location[1]
				if fontsize in fontsize_list.keys():
					fontsize_list[fontsize] += 1
				else:
					fontsize_list[fontsize] = 1
				indent = location[0]
				if indent in indent_list.keys():
					indent_list[indent] += 1
				else:
					indent_list[indent] = 1
		return (most_left, most_right), indent_list, fontsize_list

	def if_close_to(self, src, dst, threshold = 0.1):
		if (src >= dst * (1 - threshold)) and (src <= dst * (1 + threshold)):
			return True
		return False

	def get_conclude(self, indent_list, fontsize_list):
		sorted_indents = self.sort_dict_by_val(indent_list)
		sorted_sizes = self.sort_dict_by_val(fontsize_list)
		mapping_list = {}
		for key in indent_list.keys():
			mapping_list[key] = key
		max_amount_indent = sorted_indents[0][0]
		max_amount_indent_2 = -1
		for item in sorted_indents[1:]:
			if self.if_close_to(item[0], max_amount_indent):
				mapping_list[item[0]] = max_amount_indent
			else:
				if max_amount_indent_2 == -1: # 尚未决定第二缩进
					max_amount_indent_2 = item[0]
				else:
					if self.if_close_to(item[0], max_amount_indent_2):
						mapping_list[item[0]] = max_amount_indent_2
					else:
						break
		max_amount_size = sorted_sizes[0][0]
		return (max_amount_indent, max_amount_indent_2), mapping_list, max_amount_size

	def get_align(self, content_xrange, location, line_width, fontsize, major_size, debug=None):
		threshold = 0.9
		ratio_lim = 0.67
		width_lim = 0.7
		size_threshold = 1.2
		percentage = line_width / (content_xrange[1] - content_xrange[0])
		delta_left = location[0] - content_xrange[0]
		delta_right = content_xrange[1] - location[1]
		delta1 = max(delta_left, delta_right)
		delta2 = min(delta_left, delta_right)
		ratio = None
		if delta1 != 0:
			ratio = delta2 / delta1
		else: # delta2 <= delta1 = 0
			return "left"
		if ratio >= ratio_lim and (percentage < threshold or fontsize > major_size * size_threshold):
			return "center"
		if ratio < ratio_lim and percentage < width_lim:
			if delta_left < delta_right:
				return "left"
			else:
				return "right"
		return "left"

	def if_para_end(self, max_width, line_width, last_char, \
			prev_size, prev_weight, prev_align, fontsize, fontweight, align, \
			debug = None):

		threshold = 0.9

		# 如果是居中或者居右，直接换行
		if prev_align == "center" or prev_align == "right":
			print "location"
			return True
		# 以下居左
		# 如果居左且比较短，直接换行
		if line_width < threshold * max_width:
			print "shorter than usual"
			return True
		# 如果对齐方式不一样，可以直接换行
		if prev_align != align:
			print "alignment difference"
			return True

		# 对齐方式一样，足够长，居左，但是结尾并不是完结符，不换行
		if last_char not in self.endmark_list:
			print "no end mark"
			return False
		
		# 结尾是完结符，对齐方式一样，够长，居左，如果字体大小和粗细不一样可以换行
		if prev_size != fontsize:
			print "size difference"
			return True
		if prev_weight != fontweight:
			print "weight difference"
			return True
		return False
