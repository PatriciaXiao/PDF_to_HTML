#-*- coding=utf-8 -*-

import sys
import codecs
from chardet import detect  # detect(str),参数只能是str,不能是unicode编码的


reload(sys)
sys.setdefaultencoding('utf8') #


fname = 'simple1.PDF'

def unicode_or_str(s):
	if isinstance(s, unicode):
		return "unicode" # to decode
	elif isinstance(s, str):
		return "str" # to encode
	else:
		return "neither"


file = open(fname, 'r')

s = file.read()
print unicode_or_str(s)
print detect(s)
print s.decode(detect(s)['encoding'])

'''
for line in file.readlines():
	# print isinstance(line, unicode)
	# print isinstance(line, str)
	print detect(line)
	print detect(line)['encoding']
	print line.decode(detect(line)['encoding'])
	
	if not isinstance(line, unicode):
		line = line.decode(detect(line)['encoding']).rstrip().lower()
	print line
	
	raw_input()

'''


'''
# with codecs.open(fname, "r", encoding='utf-8', errors='ignore') as file:
with codecs.open(fname, "r", encoding='gbk', errors='ignore') as file:
	for line in file:
		print isinstance(line, unicode)
		print isinstance(line, str)
		print line
		print line.decode('utf-8')
		print line.encode('gbk')
		print line.encode('utf-8')
		print line.decode('gbk')
		print line.decode('gbk').encode('utf-8')
		print line.encode('utf-8').decode('gbk')
		'''

		

		# gbkTypeStr = unicodeTypeStr.encode("GBK", 'ignore');

file.close()