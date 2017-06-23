from simplePDF2html import *
import os

def get_HTML_fname(pdf_name):
	parts = pdf_name.split('.')
	assert len(parts) == 2, "Could Only handle path with one '.'"
	return reduce(lambda x, y: x + y, parts[:-1] + ['_content.html'])
 
def get_PDF_fnames(directory):
	fnames = os.listdir(directory)
	PDF_names = []
	for name in fnames:
		if name.split('.')[-1] in ['PDF', 'pdf']:
			PDF_names.append(directory + name)
	return PDF_names


# get_PDF_fnames('data/')

# fname_list = ['data/simple1.PDF', 'data/simple2.PDF', 'data/simple3.PDF']
fname_list = ['data/simple2.PDF']
# fname_list = ['data/2016-01-19-1201924052.PDF']
# fname_list = get_PDF_fnames('data/')
for fname in fname_list:
	with simplePDF2HTML(fname, get_HTML_fname(fname)) as test:
		print test.pdf_path
		test.convert()
		