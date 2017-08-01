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
import copy

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
		self.outlines = None
		self.outlines_dict = None
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
		# 试试看能否直接提取目录
		try:
			raw_outlines = self.document.get_outlines()
		except Exception, e:
			raw_outlines = None

		self.outline_levels = []
		self.outlines_dict = {}
		self.outline_titles = []
		self.drawn_outline = []
		self.outline_ids = []
		if raw_outlines: #pdfpage #pdfdocument #pdftypes
			print "there are outlines included"
			for (level,title,dest,a,se) in raw_outlines:
				'''
				print level
				print title
				raw_input()
				'''
				# print dest
				# print dest[0].resolve()
				# print dest[0].resolve()['Resources']['ExtGState']['GS0'].objid
				# outline_objid = dest[0].resolve()['Resources']['ExtGState']['GS0'].objid
				if 'ExtGState' in dest[0].resolve()['Resources']:
					outline_objid = 0
					for key in dest[0].resolve()['Resources']['ExtGState'].keys():
						if key[:2] == 'GS':
							outline_objid = dest[0].resolve()['Resources']['ExtGState'][key].objid
							break
				self.outline_levels.append(level)
				self.outlines_dict[title] = outline_objid
				self.outline_titles.append(title)
				self.drawn_outline.append(False)
				self.outline_ids.append(outline_objid)
				# print outline_objid
				# print dest[0].resolve()['Parent']
				# print dest[0].resolve()['StructParents']
				# raw_input()
			# print self.document._cached_objs
			# for title in self.outlines_dict:
			# 	print title
			# 	print self.outlines_dict[title]
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
			print "processing page {0}".format(page_idx)
			# print page
			# print page.resources
			# print page.resources['ExtGState']['GS0'].objid
			page_objid = 0
			if 'ExtGState' in page.resources: # and 'GS0' in page.resources['ExtGState']:
				page_objid = 0
				for key in page.resources['ExtGState'].keys():
					if key[:2] == 'GS':
						page_objid = page.resources['ExtGState'][key].objid
						break
			self.write('<div id="{0}">'.format(page_objid))
			self.level += 1
			# print page_objid
			# if page_objid in self.outlines.keys():
				# 是一个目录项的对应页
				# print self.outlines[page_objid]
			# print self.outlines[page_objid]
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
			# get table contents in advance
			# self.show_page_layout(layout)
			table_points_list, bias, table_divider_list = self.get_tables(layout)
			table_frames = []
			in_table = [] # true / false
			table_drawn = [] # true / false
			for i in range(len(table_points_list)):
				table_points = table_points_list[i]
				tmp_frame = self.get_table_frame(table_points, bias, table_divider_list[i])
				if tmp_frame.grids:
					table_frames.append(tmp_frame)
					table_drawn.append(False)
					# print tmp_frame.grids
			# print table_frames
			# 去除嵌套结构以及页码的外框
			i = len(table_frames) - 1
			while i > 0:
				j = i - 1
				while j >= 0:
					# print table_frames[i].grids
					# print table_frames[j].grids
					# print table_frames[i].included_in_table(table_frames[j])
					# print table_frames[j].included_in_table(table_frames[i])
					if table_frames[i].included_in_table(table_frames[j]):
						table_frames.pop(j)
						table_drawn.pop(j)
						break
					elif table_frames[j].included_in_table(table_frames[i]):
						table_frames.pop(i)
						table_drawn.pop(i)
						break
					j -= 1
				i -= 1
			# 将属于表格内的内容填进表格内
			for x in layout:
				if(isinstance(x, LTTextBoxHorizontal)):
					# in_table.append(-1) # -1 for not included in any table; else: the table frame's index
					table_idx = -1
					for line in x:
						if (isinstance(line, LTTextLineHorizontal)):
							for i in range(len(table_frames)):
								# table_frames[i]
								corner1 = (line.x0, line.y0)
								corner2 = (line.x1, line.y1)
								if table_frames[i].is_in_range(corner1) and table_frames[i].is_in_range(corner2):
									table_idx = i
									break
							if table_idx != -1:
								break
					in_table.append(table_idx)
					if table_idx != -1:
						for line in x:
							if (isinstance(line, LTTextLineHorizontal)):
								# table_frames[table_idx]
								parts = {} # location: text
								for char in line:
									if isinstance(char, LTChar):
										text_line = re.sub(self.replace,'', char.get_text())
										if len(text_line):
											corner1 = (char.x0, char.y1)
											corner2 = (char.x1, char.y0)
											location = table_frames[table_idx].locate(corner2)
											# print location, text_line
											# raw_input()
											if (location):
												if location in parts.keys():
													parts[location] += text_line
												else:
													parts[location] = text_line
								for location in parts.keys():
									table_frames[table_idx].add_data(location, parts[location])
									if table_frames[table_idx].font[location[0]][location[1]] == None:
										table_frames[table_idx].font[location[0]][location[1]] = int(line.y1 - line.y0)
			# print in_table
			for i in range(len(table_frames)):
				if len(table_frames[i].data) <= 1:
					# not a real table, dirty data
					for j in range(len(in_table)):
						if in_table[j] == i:
							in_table[j] = -1
			#### 预处理找出目录内容 ###
			# step 1: 先找出每项对应的目录项的坐标和位置
			in_outline = []
			outline_lines = [] # contents: [[y0, y1]], length: outline_lines
			for x in layout:
				if(isinstance(x, LTTextBoxHorizontal)):
					outline_text = x.get_text()
					tmp_outline_idx = self.get_outline_idx(outline_text)
					in_outline.append(tmp_outline_idx)
					tmp_y0 = int(x.y0)
					tmp_y1 = int(x.y1)
					outline_lines.append((tmp_y0, tmp_y1))
					# print re.sub(self.replace,'',outline_text)
					# print tmp_y0, tmp_y1
			# step 2: 再合并同一行的内容
			for i in range(1, len(in_outline)):
				if in_outline[i] == -1:
					if in_outline[i - 1] != -1 and \
					  self.if_close_to(outline_lines[i][0], outline_lines[i-1][0], mode = 'absolute', threshold = 4) and \
					  self.if_close_to(outline_lines[i][1], outline_lines[i-1][1], mode = 'absolute', threshold = 4):
						in_outline[i] = in_outline[i - 1]
			# print in_outline
			# raw_input()
			# step 3: 内容
			outline_content = {}
			tmp_x_idx = 0
			for x in layout:
				if(isinstance(x, LTTextBoxHorizontal)):
					outline_text = x.get_text()
					tmp_outline_idx = in_outline[tmp_x_idx]
					if tmp_outline_idx != -1:
						if tmp_outline_idx in outline_content.keys():
							outline_content[tmp_outline_idx] += outline_text
						else:
							outline_content[tmp_outline_idx] = outline_text
					tmp_x_idx += 1
			# step 4: 去除非目录内容
			
			tmp_outline_list_length = len(in_outline)
			for i in range(tmp_outline_list_length):
				is_real_outline_content = False
				if i > 0 and i < tmp_outline_list_length - 1 and in_outline[i-1] != -1 and in_outline[i+1] != -1:
					is_real_outline_content = True
				elif i > 1 and in_outline[i-1] != -1 and in_outline[i-2] != -1:
					is_real_outline_content = True
				elif i < tmp_outline_list_length - 2 and in_outline[i+1] != -1 and in_outline[i+2] != -1:
					is_real_outline_content = True
				if not is_real_outline_content:
					in_outline[i] = -1
			'''
			print in_outline
			# raw_input()
			for key in outline_content:
				print key
				print re.sub(self.replace,'',outline_content[key])
			raw_input()
			'''
			# 写入表格内容以外的其他内容
			x_idx = -1
			for x in layout:
				if(isinstance(x, LTTextBoxHorizontal)): # if(isinstance(x, LTTextLineHorizontal)):
					# print re.sub(self.replace,'',x.get_text())
					x_idx += 1
					if in_table[x_idx] != -1:
						if not table_drawn[in_table[x_idx]]:
							#########
							if prev_text:
								self.write('<p style="font-size:{2}px;font-weight:{3};text-indent:{4}em;" align="{1}">{0}</p>'.format( \
										prev_text, prev_align, prev_size, prev_weight, prev_indent
									))
							prev_text = None
							#########
							# haven't drawn yet
							self.draw_table(table_frames[in_table[x_idx]], page_xrange)
							table_drawn[in_table[x_idx]] = True
						continue
					fontname, fontsize, location, line_width = self.get_font(x)
					fontweight = self.fontweight_dict[fontname]
					# 如果是outline
					tmp_outline_idx = in_outline[x_idx]
					if tmp_outline_idx != -1:
						if not self.drawn_outline[tmp_outline_idx]:
							#########
							if prev_text:
								self.write('<p style="font-size:{2}px;font-weight:{3};text-indent:{4}em;" align="{1}">{0}</p>'.format( \
										prev_text, prev_align, prev_size, prev_weight, prev_indent
									))
							prev_text = None
							#########
							# print "draw outline here"
							tmp_outline_title = outline_content[tmp_outline_idx]
							self.draw_outline(tmp_outline_idx, tmp_outline_title, fontsize, fontweight)
							self.drawn_outline[tmp_outline_idx] = True
						continue
					# text=re.sub(self.replace,'',x.get_text())
					text = x.get_text()
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
						self.write('<p style="font-size:{2}px;font-weight:{3};text-indent:0.0em;" align="{1}">{0}</p>'.format( \
								text, align, fontsize, fontweight
							))
			page_idx += 1
			self.level -= 1
			self.write('</div>')
		
		if prev_text:
			self.write('<p style="font-size:{2}px;font-weight:{3};text-indent:{4}em;" align="{1}">{0}</p>'.format( \
					prev_text, prev_align, prev_size, prev_weight, prev_indent
				))
		self.level -= 1
		self.write('</body>')

	def draw_outline(self, outline_idx, outline_title, font_size, font_weight):
		ref_id = self.outline_ids[outline_idx]
		level = self.outline_levels[outline_idx]
		'''
		print outline_title
		print outline_idx
		print ref_id
		print level
		print self.outline_titles[outline_idx]
		print self.outlines[ref_id][1]
		raw_input()
		'''
		if level > 0:
			indent = (level - 1) * 2.0
		else:
			indent = 0.0
		self.write('<p style="font-size:{0}px;font-weight:{1};text-indent:{2}em;" align="left">'.format(\
				font_size, font_weight, indent
			))
		self.level += 1
		self.write('<a href="#{1}">{0}</a>'.format(\
				outline_title, ref_id
			))
		self.level -= 1
		self.write('</p>')
		#self.write('<a style="font-size:{2}px;font-weight:{3};text-indent:{4}em;" align="left" href="#{1}">{0}</a>'.format(\
		#		outline_title, ref_id, font_size, font_weight, indent
		#	))

	def get_outline_idx(self, goal_string):
		goal_idx = -1
		outline_length = len(self.outline_titles)
		clean_string = re.sub(self.replace,'', goal_string)
		len_string = len(clean_string)
		for i in range(outline_length):
			title = self.outline_titles[i]
			clean_title = re.sub(self.replace,'', title)
			len_title = len(clean_title)
			if len_title > len_string: continue
			if clean_title == clean_string[:len_title]:
				goal_idx = i
				break
		return goal_idx

	def draw_table(self, table_frame, page_xrange=None):
		# data = table_frame.data
		data, font, rowspan, colspan = table_frame.get_clean_data()
		if page_xrange:
			width_portion = 100.0 * (table_frame.range['max_x'] - table_frame.range['min_x']) / (page_xrange[1] - page_xrange[0])
			self.write('<table border="1" cellspacing="0" align="center" width="{0}%">'.format(int(width_portion)))
		else:
			self.write('<table border="1" cellspacing="0" align="center">')
		self.level += 1
		for i in range(len(data)):
			self.write('<tr>')
			self.level += 1
			for j in range(len(data[i])):
				content = data[i][j]
				fontsize = font[i][j]
				rs = rowspan[i][j]
				cs = colspan[i][j]
				if fontsize:
					self.write('<td style="font-size: {1}px;" rowspan="{2}" colspan="{3}">{0}</td>'.format("<br>".join(content), fontsize, rs, cs))
				else:
					self.write('<td rowspan="{1}" colspan="{2}">{0}</td>'.format("<br>".join(content), rs, cs))
			self.level -= 1
			self.write('</tr>')
		self.level -= 1
		self.write('</table>')

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

	def if_close_to(self, src, dst, mode = 'percent', threshold = 0.1):
		if mode == 'percent':
			if (src >= dst * (1 - threshold)) and (src <= dst * (1 + threshold)):
				return True
			return False
		elif mode == 'absolute':
			if (src >= dst - threshold) and (src <= dst + threshold):
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
		threshold = 3 #2
		x_diff = rect_elem.x1 - rect_elem.x0
		y_diff = rect_elem.y1 - rect_elem.y0
		if x_diff < threshold:
			if y_diff > 3 * threshold:
				return "y"
			else:
				return "point"
		if y_diff < threshold:
			if x_diff > 3 * threshold:
				return "x"
			else:
				return "point"
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
		draw = Draw(size_x, size_y, offset_x, offset_y)
		draw.set_color("black")
		draw.square(page_range["left"], page_range["right"], page_range["top"], page_range["bottom"])
		for x in layout:
			isLine = False
			if(isinstance(x, LTTextBoxHorizontal)):
				for line in x:
					# print line # LTTextLine
					draw.set_color("green")
					draw.square(line.x0, line.x1, line.y1, line.y0)
					for char in line:
						# print char # LTChar / LTAnno
						if isinstance(char, LTChar):
							draw.set_color("brown")
							draw.square(char.x0, char.x1, char.y1, char.y0)
						elif isinstance(char, LTChar):
							draw.set_color("gray")
							draw.square(char.x0, char.x1, char.y1, char.y0)
				draw.set_color("black")
			elif(isinstance(x, LTRect)):
				isLine = self.is_line(x)
				if isLine:
					draw.set_color("orange")
				else:
					draw.set_color("red")
			else:
				# print x
				# raw_input()
				draw.set_color("blue")
			left = x.x0
			right = x.x1
			top = x.y1
			bottom = x.y0
			print "left:{0}, right: {1}, top: {2}, bottom: {3}".format(left, right, top, bottom)
			if isLine == 'x':
				fixed_y = (top + bottom) / 2.0
				draw.line(left, fixed_y, right, fixed_y)
			elif isLine =='y':
				fixed_x = (left + right) / 2.0
				draw.line(fixed_x, top, fixed_x, bottom)
			else:
				draw.square(left, right, top, bottom)
		raw_input()
		return layout

	def get_closest_idx(self, goal_value, lst, threshold):
		closest_idx = -1
		for i in range(len(lst)):
			item = lst[i]
			if abs(item - goal_value) <= threshold:
				closest_idx = i
				break
		return closest_idx
	

	def get_tables(self, layout):
		debug = False #True
		if debug:
			page_range = {
				"left": layout.x0,
				"right": layout.x1,
				"top": layout.y1,
				"bottom": layout.y0
			}
			offset_x = -1.0 * (page_range["right"] + page_range["left"]) / 2.0
			offset_y = -1.0 * (page_range["top"] + page_range["bottom"]) / 2.0
			size_x = 1.5 * (page_range["right"] - page_range["left"])
			size_y = 1.5 * (page_range["top"] - page_range["bottom"])
			draw = Draw(size_x, size_y, offset_x, offset_y)
			draw.square(page_range["left"], page_range["right"], page_range["top"], page_range["bottom"])
		# get the maximum value of the line stroke width
		max_stroke = -1
		raw_lines = [] # contents: ((x1, y1), (x2, y2))
		raw_points = {} # contents: (x, y): [idx1, idx2, ...] - the index of corresponding lines
		raw_points_x = [] # contents: x
		raw_points_y = [] # contents: y
		points_visited = {} # contents: (x, y) : True / False
		# get the max stroke width
		for x in layout:
			# if(isinstance(x, LTRect)):
			if(isinstance(x, LTRect) or isinstance(x, LTFigure)):
				left = x.x0
				right = x.x1
				top = x.y1
				bottom = x.y0
				left = int(left)
				right = int(right)
				top = int(top)
				bottom = int(bottom)
				isLine = self.is_line(x)
				if isLine == 'x' or isLine == 'y': # a line
					# fetch data
					if isLine == 'x':
						line_stroke = top - bottom
					elif isLine =='y':
						line_stroke = right - left
					# update data
					if line_stroke > max_stroke:
						max_stroke = line_stroke

		if max_stroke >= 0:
			bias = 3 * max_stroke
		else:
			bias = 5
		# print "bias={0}".format(bias)
		# the raw lines
		for x in layout:
			# if(isinstance(x, LTRect)):
			if(isinstance(x, LTRect) or isinstance(x, LTFigure)):
				left = x.x0
				right = x.x1
				top = x.y1
				bottom = x.y0
				left = int(left)
				right = int(right)
				top = int(top)
				bottom = int(bottom)
				idx_left = self.get_closest_idx(left, raw_points_x, bias)
				idx_right = self.get_closest_idx(right, raw_points_x, bias)
				idx_top = self.get_closest_idx(top, raw_points_y, bias)
				idx_bottom = self.get_closest_idx(bottom, raw_points_y, bias)
				if idx_left >= 0:
					left = raw_points_x[idx_left]
				if idx_right >= 0:
					right = raw_points_x[idx_right]
				if idx_top >= 0:
					top = raw_points_y[idx_top]
				if idx_bottom >= 0:
					bottom = raw_points_y[idx_bottom]


				isLine = self.is_line(x)
				if isLine: # a line
					# fetch data
					if isLine == 'point':
						continue
					elif isLine == 'x':
						# print 'x'
						if idx_left == -1:
							raw_points_x.append(left)
						idx_right = self.get_closest_idx(right, raw_points_x, bias)
						if idx_right == -1:
							raw_points_x.append(right)
						fixed_y = (top + bottom) / 2.0
						fixed_y = int(fixed_y)
						idx_fixed_y = self.get_closest_idx(fixed_y, raw_points_y, bias)
						if idx_fixed_y >= 0:
							fixed_y = raw_points_y[idx_fixed_y]
						else:
							raw_points_y.append(fixed_y)
						
						pt1 = (left, fixed_y)
						pt2 = (right, fixed_y)
					elif isLine =='y':
						# print 'y'
						if idx_top == -1:
							raw_points_y.append(top)
						idx_bottom = self.get_closest_idx(bottom, raw_points_y, bias)
						if idx_bottom == -1:
							raw_points_y.append(bottom)
						fixed_x = (left + right) / 2.0
						fixed_y = int(fixed_x)
						idx_fixed_x = self.get_closest_idx(fixed_x, raw_points_x, bias)
						if idx_fixed_x >= 0:
							fixed_x = raw_points_x[idx_fixed_x]
						else:
							raw_points_x.append(fixed_x)
						
						pt1 = (fixed_x, top)
						pt2 = (fixed_x, bottom)
					# update data
					if pt1 not in raw_points.keys():
						raw_points[pt1] = []
						points_visited[pt1] = False
					if pt2 not in raw_points.keys():
						raw_points[pt2] = []
						points_visited[pt2] = False
					tmp_idx_line = len(raw_lines)
					if (pt1, pt2) not in raw_lines and (pt2, pt1) not in raw_lines:
						raw_lines.append( (pt1, pt2) )
						raw_points[pt1].append(tmp_idx_line)
						raw_points[pt2].append(tmp_idx_line)
				else: # a rectangle
					if idx_left == -1:
						raw_points_x.append(left)
					if idx_right == -1:
						raw_points_x.append(right)
					if idx_top == -1:
						raw_points_y.append(top)
					if idx_bottom == -1:
						raw_points_y.append(bottom)
					pt1 = (left, top)
					pt2 = (right, top)
					pt3 = (right, bottom)
					pt4 = (left, bottom)
					points_visited[pt1] = False
					points_visited[pt2] = False
					points_visited[pt3] = False
					points_visited[pt4] = False
					if pt1 not in raw_points:
						raw_points[pt1] = []
					if pt2 not in raw_points:
						raw_points[pt2] = []
					if pt3 not in raw_points:
						raw_points[pt3] = []
					if pt4 not in raw_points:
						raw_points[pt4] = []
					# raw_lines.append( (pt1, pt2) )
					tmp_idx_line = len(raw_lines)
					if (pt1, pt2) not in raw_lines and (pt2, pt1) not in raw_lines:
						raw_lines.append( (pt1, pt2) )
						raw_points[pt1].append(tmp_idx_line)
						raw_points[pt2].append(tmp_idx_line)
					# raw_lines.append( (pt2, pt3) )
					tmp_idx_line = len(raw_lines)
					if (pt2, pt3) not in raw_lines and (pt3, pt2) not in raw_lines:
						raw_lines.append( (pt2, pt3) )
						raw_points[pt2].append(tmp_idx_line)
						raw_points[pt3].append(tmp_idx_line)
					# raw_lines.append( (pt3, pt4) )
					tmp_idx_line = len(raw_lines)
					if (pt3, pt4) not in raw_lines and (pt4, pt3) not in raw_lines:
						raw_lines.append( (pt3, pt4) )
						raw_points[pt3].append(tmp_idx_line)
						raw_points[pt4].append(tmp_idx_line)
					# raw_lines.append( (pt4, pt1) )
					tmp_idx_line = len(raw_lines)
					if (pt4, pt1) not in raw_lines and (pt1, pt4) not in raw_lines:
						raw_lines.append( (pt4, pt1) )
						raw_points[pt4].append(tmp_idx_line)
						raw_points[pt1].append(tmp_idx_line)
		# print raw_lines
		# print raw_points
		# calculate the points included in a table, and the grids
		assert len(points_visited.keys()) == len(raw_points.keys()), "points amount and points list length do not match"

		print raw_points
		print points_visited
		print raw_points_x
		print raw_points_y


		
		'''
		if debug:
			point_list = raw_points.copy()
			def debug_walk(tmp_point):
				if points_visited[tmp_point]:
					return
				points_visited[tmp_point] = True
				draw.dot(tmp_point[0], tmp_point[1], size=15, color_string="green")
				next_links = point_list[tmp_point]
				for idx in next_links:
					line = raw_lines[idx]
					debug_walk(line[0])
					debug_walk(line[1])
			test_point = point_list.keys()[0]
			test_value = point_list[test_point]
			debug_walk(test_point)
			print "debug walk done"
		'''
		


		point_list = raw_points.copy()

		def recursively_get_group(tmp_point):
			ret_val = []
			# if the point has already been visited
			if not points_visited[tmp_point]:
				points_visited[tmp_point] = True
				ret_val.append(tmp_point)
				# get the neighbours
				next_idx_lst = point_list.pop(tmp_point)
				for idx in next_idx_lst:
					line = raw_lines[idx]				
					next_point = line[0]
					if next_point == tmp_point:
						next_point = line[1]
					if points_visited[next_point]: 
						continue
					next_list = recursively_get_group(next_point)
					ret_val.extend(next_list)
					# draw.dot(next_point[0], next_point[1], size=15, color_string="green")
						
			return ret_val

		table_list = []
		table_line_list = [] # lines that belong to a specific table
		divider_list = [] # the lines
		while len(point_list.keys()):
			next_starting_point = point_list.keys()[0]
			next_group = recursively_get_group(next_starting_point)
			if len(next_group) > 2: # not a line
				next_group.sort()
				table_list.append(next_group)
				divider_list.append([])
				table_line_list.append([])
		
		# get the lines' list
		for line in raw_lines:
			for i in range(len(table_list)):
				if line[0] in table_list[i] or line[1] in table_list[i]:
					table_line_list[i].append(line)
					break
		# print table_line_list

		# get the regularized lines
		for i in range(len(table_list)):
			tmp_xs = []
			tmp_ys = []
			tmp_table = table_list[i]
			tmp_lines = table_line_list[i]
			# print tmp_table
			for pt in tmp_table:
				pt_x = pt[0]
				pt_y = pt[1]
				if pt_x not in tmp_xs:
					tmp_xs.append(pt_x)
				if pt_y not in tmp_ys:
					tmp_ys.append(pt_y)
			tmp_xs.sort()
			tmp_ys.sort()
			# print tmp_xs
			# print tmp_ys
			for line in tmp_lines:
				pt1 = min(line[0], line[1])
				pt2 = max(line[0], line[1])
				if pt1[0] == pt2[0]: # same x
					start_line_idx = -1
					end_line_idx = -1
					# print pt1, pt2
					for idx in range(len(tmp_ys)):
						if tmp_ys[idx] == pt1[1]:
							start_line_idx = idx
						elif tmp_ys[idx] == pt2[1]:
							end_line_idx = idx
							break # sorted
					assert start_line_idx != -1 and end_line_idx != -1, "error happend when building the frame of the table"
					for idx in range(start_line_idx, end_line_idx):
						tmp_pt1 = (pt1[0], tmp_ys[idx])
						tmp_pt2 = (pt1[0], tmp_ys[idx + 1])
						if (tmp_pt1, tmp_pt2) not in divider_list[i] and (tmp_pt2, tmp_pt1) not in divider_list[i]:
							divider_list[i].append( (tmp_pt1, tmp_pt2) )
				elif pt1[1] == pt2[1]: # same y
					start_line_idx = -1
					end_line_idx = -1
					# print pt1, pt2
					for idx in range(len(tmp_xs)):
						if tmp_xs[idx] == pt1[0]:
							start_line_idx = idx
						elif tmp_xs[idx] == pt2[0]:
							end_line_idx = idx
							break # because it was sorted
					assert start_line_idx != -1 and end_line_idx != -1, "error happend when building the frame of the table"
					for idx in range(start_line_idx, end_line_idx):
						tmp_pt1 = (tmp_xs[idx], pt1[1])
						tmp_pt2 = (tmp_xs[idx + 1], pt1[1])
						if (tmp_pt1, tmp_pt2) not in divider_list[i] and (tmp_pt2, tmp_pt1) not in divider_list[i]:
							divider_list[i].append( (tmp_pt1, tmp_pt2) )
				else:
					assert False, "seems that it is not a regular table"
			# print divider_list[i]


		# test
		'''
		if debug:
			for table in table_list:
				for pt in table:
			 		draw.dot(pt[0], pt[1], size=10, color_string="red")
			 	# raw_input()
			for table in table_list:
				n_pts = len(table)
				draw.dot(table[0][0], table[0][1], size=10, color_string="red")
				draw.dot(table[n_pts - 1][0], table[n_pts - 1][1], size=10, color_string="red")
			for line in raw_lines:
				draw.line(line[0][0], line[0][1], line[1][0], line[1][1])
			# raw_input()
		
		if debug:
			# debug
			for divider in divider_list[0]:
				print divider
				start = divider[0]
				end = divider[1]
				draw.set_color("red")
				print start[0], start[1], end[0], end[1]
				draw.line(start[0], start[1], end[0], end[1])
				raw_input()
		'''
		

		return table_list, bias, divider_list

	def get_table_frame(self, table_points_list, bias, table_divider_list):
		ret_val = TableFrame(table_points_list, bias, table_divider_list)
		return ret_val

class TableFrame(object):
	def __init__(self, table_points_list, bias, table_divider_list):
		# assert len(table_points_list) > 2, "the data passed in is not a table at all"
		self.bias = bias
		self.grids = {"x": [], "y": []}
		self.data = [] # content, [['XXX', 'XXX'],['XXX', 'XXX']...]
		self.font = []
		self.rowspan = []
		self.colspan = []
		self.location_map = {} # content: [(x_location, y_location): (x_data, y_data)]
		self.range = {"max_x": -1, "max_y": -1, "min_x": 0, "min_y": 0}
		for point in table_points_list:
			x = point[0]
			y = point[1]
			if x not in self.grids['x']:
				self.grids['x'].append(x)
			if y not in self.grids['y']:
				self.grids['y'].append(y)
		self.grids['x'].sort()
		self.grids['y'].sort(reverse=True)
		# print self.grids['x']
		# print self.grids['y']
		# assert len(self.grids['x']) > 1 and len(self.grids['y']) > 1, "the table data does not represent an area"
		if len(table_points_list) <= 2 or len(self.grids['x']) <= 1 or len(self.grids['y']) <= 1:
			self.grids = None
		else:
			# get the structure of the table
			# print table_divider_list
			n_rows = len(self.grids['y']) - 1
			n_cols = len(self.grids['x']) - 1
			for i in range(n_rows):
				empty_line = []
				empty_font = []
				empty_rowspan = []
				empty_colspan = []
				tmp_col = 0
				for j in range(n_cols):
					# print "up, down, left, right"
					# print self.grids['y'][i], self.grids['y'][i + 1], self.grids['x'][j], self.grids['x'][j + 1]
					upperleft_corner = (self.grids['x'][j], self.grids['y'][i])
					lowerleft_corner = (self.grids['x'][j], self.grids['y'][i + 1])
					upperright_corner = (self.grids['x'][j + 1], self.grids['y'][i])
					lowerright_corner = (self.grids['x'][j + 1], self.grids['y'][i + 1])
					upper_connected = False
					left_connected = False
					
					if i > 0:
						# possible that rowspan > 0
						if (upperleft_corner, upperright_corner) not in table_divider_list and \
						  (upperright_corner, upperleft_corner) not in table_divider_list:
							# connected to the upper grid
							upper_connected = True
					if j > 0:
						# possible that colspan > 0
						if (lowerleft_corner, upperleft_corner) not in table_divider_list and \
						  (upperleft_corner, lowerleft_corner) not in table_divider_list:
							# connected to the left grid
							left_connected = True

					# print i, j, upper_connected, left_connected

					# upper_connected = False
					# left_connected = False

					if upper_connected and left_connected:
						self.location_map[(i, j)] = self.location_map[(i - 1, j)]
					elif upper_connected:
						self.location_map[(i, j)] = self.location_map[(i - 1, j)]
						representer_i = self.location_map[(i - 1, j)][0]
						representer_j = self.location_map[(i - 1, j)][1]
						self.rowspan[representer_i][representer_j] += 1
						
					elif left_connected:
						self.location_map[(i, j)] = self.location_map[i, (j - 1)]
						representer_i = self.location_map[(i, j - 1)][0]
						representer_j = self.location_map[(i, j - 1)][1]
						# self.colspan[representer_i][representer_j] += 1
						empty_colspan[representer_j] += 1

					else: # the starting grid of an area
						empty_line.append([])
						empty_font.append(None)
						empty_rowspan.append(1)
						empty_colspan.append(1)
						self.location_map[(i, j)] = (i, tmp_col)
						tmp_col += 1
				self.data.append(empty_line)
				self.font.append(empty_font)
				self.rowspan.append(empty_rowspan)
				self.colspan.append(empty_colspan)
			corner1 = table_points_list[0]
			corner2 = table_points_list[len(table_points_list) - 1]
			self.range['max_x'] = max(corner1[0], corner2[0])
			self.range['max_y'] = max(corner1[1], corner2[1])
			self.range['min_x'] = min(corner1[0], corner2[0])
			self.range['min_y'] = min(corner1[1], corner2[1])

	def locate(self, point):
		def greater_than(a, b):
			if a + self.bias > b:
				return True
			return False
		def smaller_than(a, b):
			if a < b + self.bias:
				return True
			return False
		# point: (x, y)
		x = point[0]
		y = point[1]
		x_idx = -1
		y_idx = -1
		n_x = len(self.grids['x'])
		n_y = len(self.grids['y'])
		# print n_x, n_y
		# print self.grids['x']
		# print self.grids['y']
		for i in range(1, n_x):
			# print "compare {0} with {1} and {2}".format(x, self.grids['x'][i - 1], self.grids['x'][i])
			if greater_than(x, self.grids['x'][i - 1]) and smaller_than(x, self.grids['x'][i]):
				x_idx = i - 1
				break
		for i in range(1, n_y):
			# print "compare {0} with {1} and {2}".format(y, self.grids['y'][i - 1], self.grids['y'][i])
			if smaller_than(y, self.grids['y'][i - 1]) and greater_than(y, self.grids['y'][i]):
				y_idx = i - 1
				break
		# print x_idx, y_idx
		if x_idx == -1 or y_idx == -1:
			return None
		(row, col) = self.location_map[(y_idx, x_idx)]
		return (row, col) # row, col

	def get_clean_data(self):
		clean_data = []
		clean_fonts = []
		clean_rowspan = []
		clean_colspan = []
		for i in range(len(self.data)):
			line = self.data[i]
			empty = True
			for elem in line:
				if len(elem):
					empty = False
					break
			if not empty:
				clean_data.append(copy.copy(line))
				clean_fonts.append(copy.copy(self.font[i]))
				clean_rowspan.append(copy.copy(self.rowspan[i]))
				clean_colspan.append(copy.copy(self.colspan[i]))
		return clean_data, clean_fonts, clean_rowspan, clean_colspan


	def is_in_range(self, point):
		def greater_than(a, b):
			if a + self.bias > b:
				return True
			return False
		def smaller_than(a, b):
			if a < b + self.bias:
				return True
			return False
		# point: (x, y)
		x = point[0]
		y = point[1]
		x_idx = -1
		if greater_than(x, self.range['min_x']) and smaller_than(x, self.range['max_x'])\
		  and greater_than(y, self.range['min_y']) and smaller_than(y, self.range['max_y']):
			return True
		return False

	def add_data(self, location, content):
		row = location[0]
		col = location[1]
		self.data[row][col].append(content)

	def included_in_table(self, another_table):
		corner1 = (self.range['min_x'], self.range['min_y'])
		corner2 = (self.range['max_x'], self.range['min_y'])
		return another_table.is_in_range(corner1) and another_table.is_in_range(corner2)

class Draw(object):
	def __init__(self, size_x, size_y, offset_x, offset_y):
		self.offset_x = offset_x
		self.offset_y = offset_y
		turtle.clear()
		turtle.screensize(canvwidth=size_x, canvheight=size_y, bg=None)	
	def set_color(self, color_string):
		turtle.pencolor(color_string)
	def dot(self, x, y, size=3, color_string="purple"):
		# turtle.penup()
		turtle.goto(x + self.offset_x, y + self.offset_y)
		# turtle.pendown()
		turtle.dot(size, color_string)
		# turtle.penup()
	def line(self, start_x, start_y, end_x, end_y):
		turtle.penup()
		turtle.goto(start_x + self.offset_x, start_y + self.offset_y)
		turtle.pendown()
		self.dot(start_x, start_y)
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