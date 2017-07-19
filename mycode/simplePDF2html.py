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
import turtle # 为了可视化显示检测到的布局

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
		self.debug_log = open('debug.log', 'a')
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
		self.debug_log.close()
		if self.device:
			self.device.close()
		sys._clear_type_cache() 
		gc.collect()

	def write(self, content):
		self.writer.write(self.level * self.indent + str(content).encode('utf-8') + '\n')

	def debug_write(self, content):
		self.debug_log.write(str(content).encode('utf-8') + '\n')

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
		'''
		self.write('<style>')
		self.level += 1
		self.write('p {')
		self.level += 1
		self.write('text-indent: 2.0em;')
		self.level -= 1
		self.write('};')
		self.level -= 1
		self.write('</style>')
		'''
		self.level -= 1
		self.write('</head>')

	def writeBody(self):
		self.write('<body>')
		self.level += 1
		# 循环遍历列表，每次处理一个page的内容
		page_idx = 1
		ended = False
		prev_text = None
		prev_size = None
		prev_weight = None
		prev_indent = None
		prev_align = None
		prev_length = None
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
			if len(indent_list) == 0 or len(fontsize_list) == 0: # 空白页
				continue
			content_width = content_xrange[1] - content_xrange[0]
			major_indents, map_indents, major_size = self.get_conclude(indent_list, fontsize_list)
			typical_length = content_width / major_size
			# raw_input()
			# print table_info
			# self.show_page_layout(layout)
			self.get_tables(layout)
			for x in layout:
				if(isinstance(x, LTTextBoxHorizontal)):
					fontname, fontsize, location, line_width = self.get_font(x)
					text=re.sub(self.replace,'',x.get_text())
					# text = x.get_text()
					fontweight = self.fontweight_dict[fontname]
					actual_left = map_indents[location[0]]
					indent = self.get_indent(actual_left, major_indents)
					align = self.get_align(content_xrange, location, line_width, fontsize, major_size, debug=text)
					length = line_width / fontsize
					# print x.x0, x.x1, x.y0, x.y1
					# print text
					# raw_input()
					if (align == 'left'):
						# 检测当前行是否是一行的开头，之前行是否已结尾
						if prev_text == None:
							prev_length = 0
						ended = self.if_para_end(actual_left, major_indents, prev_length / typical_length)
						if ended:
							if prev_text:
								self.write('<p style="font-size:{2}px;font-weight:{3};text-indent:{4}em;" align="{1}">{0}</p>'.format( \
										prev_text, prev_align, prev_size, prev_weight, prev_indent
									))
							prev_text = None
						# 准备传给下一次迭代
						if prev_text:
							prev_text = prev_text + text
							prev_length = length
						else:
							prev_text = text
							prev_size = fontsize
							prev_weight = fontweight
							prev_indent = indent
							prev_align = align
							prev_length = length
					else:
						if prev_text:
							self.write('<p style="font-size:{2}px;font-weight:{3};text-indent:{4}em;" align="{1}">{0}</p>'.format( \
									prev_text, prev_align, prev_size, prev_weight, prev_indent
								))
							prev_text = None
						self.write('<p style="font-size:{2}px;font-weight:{3}text-indent:0.0em;" align="{1}">{0}</p>'.format( \
								text, align, fontsize, fontweight
							))
			page_idx += 1
		
		if prev_text:
			self.write('<p style="font-size:{2}px;font-weight:{3};text-indent:{4}em;" align="{1}">{0}</p>'.format( \
					prev_text, prev_align, prev_size, prev_weight, prev_indent
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

	def get_indent(self, actual_left, major_indents):
		level_indent = max(major_indents[0], major_indents[1])
		if actual_left == level_indent:
			return 2.0
		else:
			return 0.0


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
		threshold = 0.8
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

	def if_para_end(self, actual_left, major_indents, ratio):
		threshold = 0.7
		min_indent = min(major_indents[0], major_indents[1])
		if actual_left == min_indent:
			# 除非此行比较短，否则认定为没有分段
			if ratio < threshold:
				return True
			return False
		else:
			return True

	def is_line(self, rect_elem):
		threshold = 2
		if (rect_elem.x1 - rect_elem.x0) < threshold:
			return "y"
		if (rect_elem.y1 - rect_elem.y0) < threshold:
			return "x"
		return False

	def show_page_layout(self, layout):
		page_range = {
			"left": layout.x0,
			"right": layout.x1,
			"top": layout.y1,
			"bottom": layout.y0
		}
		print "Page Range = left:{0}, right: {1}, top: {2}, bottom: {3}".format(\
			page_range["left"], page_range["right"], page_range["top"], page_range["bottom"])
		offset_x = -1.0 * (page_range["right"] + page_range["left"]) / 2.0
		offset_y = -1.0 * (page_range["top"] + page_range["bottom"]) / 2.0
		size_x = 1.5 * (page_range["right"] - page_range["left"])
		size_y = 1.5 * (page_range["top"] - page_range["bottom"])
		drawer = Draw(size_x, size_y, offset_x, offset_y)
		drawer.set_color("black")
		drawer.square(page_range["left"], page_range["right"], page_range["top"], page_range["bottom"])
		for x in layout:
			isLine = False
			if(isinstance(x, LTTextBoxHorizontal)):
				for line in x:
					# print line # LTTextLine
					for char in line:
						# print char # LTChar / LTAnno
						if isinstance(char, LTChar):
							drawer.set_color("brown")
							drawer.square(char.x0, char.x1, char.y1, char.y0)
						elif isinstance(char, LTChar):
							drawer.set_color("gray")
							drawer.square(char.x0, char.x1, char.y1, char.y0)
				drawer.set_color("black")
			elif(isinstance(x, LTRect)):
				isLine = self.is_line(x)
				if isLine:
					drawer.set_color("orange")
				else:
					drawer.set_color("red")
			else:
				drawer.set_color("blue")
			left = x.x0
			right = x.x1
			top = x.y1
			bottom = x.y0
			print "left:{0}, right: {1}, top: {2}, bottom: {3}".format(left, right, top, bottom)
			if isLine == 'x':
				fixed_y = (top + bottom) / 2.0
				drawer.line(left, fixed_y, right, fixed_y)
			elif isLine =='y':
				fixed_x = (left + right) / 2.0
				drawer.line(fixed_x, top, fixed_x, bottom)
			else:
				drawer.square(left, right, top, bottom)
		raw_input()
		return layout

	def get_tables(self, layout):
		page_range = {
			"left": layout.x0,
			"right": layout.x1,
			"top": layout.y1,
			"bottom": layout.y0
		}
		print "Page Range = left:{0}, right: {1}, top: {2}, bottom: {3}".format(\
			page_range["left"], page_range["right"], page_range["top"], page_range["bottom"])
		offset_x = -1.0 * (page_range["right"] + page_range["left"]) / 2.0
		offset_y = -1.0 * (page_range["top"] + page_range["bottom"]) / 2.0
		size_x = 1.5 * (page_range["right"] - page_range["left"])
		size_y = 1.5 * (page_range["top"] - page_range["bottom"])
		drawer = Draw(size_x, size_y, offset_x, offset_y)
		drawer.set_color("black")
		drawer.square(page_range["left"], page_range["right"], page_range["top"], page_range["bottom"])
		# get the maximum value of the line stroke width
		max_stroke = -1
		for x in layout:
			if(isinstance(x, LTRect)):
				isLine = self.is_line(x)
				if isLine:
					left = x.x0
					right = x.x1
					top = x.y1
					bottom = x.y0
					left = int(left)
					right = int(right)
					top = int(top)
					bottom = int(bottom)
					if isLine == 'x':
						line_stroke = top - bottom
						if line_stroke > max_stroke:
							max_stroke = line_stroke
					elif isLine =='y':
						line_stroke = right - left
						if line_stroke > max_stroke:
							max_stroke = line_stroke
		if max_stroke >= 0:
			bias = 3 * max_stroke
		else:
			bias = 4
		print max_stroke
		# fill in the contents
		table_layout = [] # list of tables; table: {"rows":[], "cols": []}
		for x in layout:
			if(isinstance(x, LTRect)):
				isLine = self.is_line(x)
				# converting them to integers has little side-effect
				# besides, it'll make it much easier to build a dictionary
				left = x.x0
				right = x.x1
				top = x.y1
				bottom = x.y0
				left = int(left)
				right = int(right)
				top = int(top)
				bottom = int(bottom)
				if isLine == 'x':
					fixed_y = int((top + bottom) / 2.0)
					drawer.line(left, fixed_y, right, fixed_y)
				elif isLine =='y':
					fixed_x = int((left + right) / 2.0)
					drawer.line(fixed_x, top, fixed_x, bottom)
				else:
					drawer.square(left, right, top, bottom)
		raw_input()
		return layout

class Draw(object):
	def __init__(self, size_x, size_y, offset_x, offset_y):
		self.offset_x = offset_x
		self.offset_y = offset_y
		turtle.clear()
		turtle.screensize(canvwidth=size_x, canvheight=size_y, bg=None)	
	def set_color(self, color_string):
		turtle.pencolor(color_string)
	def line(self, start_x, start_y, end_x, end_y):
		turtle.penup()
		turtle.goto(start_x + self.offset_x, start_y + self.offset_y)
		turtle.pendown()
		turtle.goto(end_x + self.offset_x, end_y + self.offset_y)
		turtle.penup()
	def square(self, left, right, top, bottom):
		turtle.penup()
		turtle.goto(left + self.offset_x, top + self.offset_y)
		turtle.pendown()
		turtle.goto(right + self.offset_x, top + self.offset_y)
		turtle.goto(right + self.offset_x, bottom + self.offset_y)
		turtle.goto(left + self.offset_x, bottom + self.offset_y)
		turtle.goto(left + self.offset_x, top + self.offset_y)
		turtle.penup()