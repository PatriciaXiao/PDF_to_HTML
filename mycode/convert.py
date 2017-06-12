from simplePDF2html import *

with simplePDF2HTML('data/simple1.PDF', 'data/simple1_content2.html') as test:
	print test.pdf_path
	test.convert()