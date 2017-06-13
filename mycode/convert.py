from simplePDF2html import *

def get_HTML_fname(pdf_name):
	parts = pdf_name.split('.')
	assert len(parts) == 2, "Could Only handle path with one '.'"
	return reduce(lambda x, y: x + y, parts[:-1] + ['_content.html'])

# fname_list = ['data/simple1.PDF', 'data/simple2.PDF', 'data/simple3.PDF']
fname_list = ['data/simple2.PDF']

for fname in fname_list:
	with simplePDF2HTML(fname, get_HTML_fname(fname)) as test:
		print test.pdf_path
		test.convert()