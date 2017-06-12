from simplePDF2html import *

with simplePDF2HTML('data/simple2.PDF', 'data/simple2_content1.html') as test:
	print test.pdf_path
	test.convert()