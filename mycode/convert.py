from simplePDF2html import *
import os
import copy

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

# fname_list = ['data/simple1.PDF']
# fname_list = ['data/outline_example_1.pdf']

# fname_list = ['data/table_example_1.pdf', 'data/table_example_2.pdf', 'data/table_example_3.pdf', 'data/table_example_4.pdf', 'data/table_example_5.pdf', 'data/table_example_6.pdf', 'data/table_example_7.pdf', 'data/table_example_8.pdf']
# fname_list = ['data/table_example_8.pdf']
# fname_list = ['data/table_example_5.pdf']
fname_list = ['data/table_example_8.pdf'] #9 # 5 # 11 #12 # 14
#fname_list = ['data/2016-04-27-1202251320.PDF'] # table testcase
# fname_list = ['data/2016-03-26-1202083817.PDF']
# fname_list = ['data/2016-03-12-1202040147.PDF']
# fname_list = ['data/simple1.PDF', 'data/simple2.PDF', 'data/simple3.PDF']
# fname_list = ['data/simple2.PDF']

# fname_list = ['data/2016-03-26-1202083818.PDF']
# fname_list = ['data/2016-01-19-1201924052.PDF']
# fname_list = ['data/2016-01-19-1201924054.PDF']
# fname_list = get_PDF_fnames('data/')
COUNT = True
if COUNT:
	cnt_total = 0
	cnt_success = 0
	unsuccess = []
bias_param_list = [[2, 3], [1.5, 2], [3, 5]]#[[3, 5]] 
for fname in fname_list:
	with simplePDF2HTML(fname, get_HTML_fname(fname)) as test:
		print "trying to convert file {0}".format(test.pdf_path)
		succeed = False
		if COUNT:
			cnt_total += 1
			for bias_param in bias_param_list:
				try:
					print "trying parameter set {0}".format(bias_param)
					test.convert(bias_param)
					cnt_success += 1
					print "succeed"
					succeed = True
					break
				except Exception, e:
					print "didn't succeed"
			if not succeed:
				print "failed to convert file {0}".format(test.pdf_path)
				unsuccess.append(copy.copy(test.pdf_path))
		else:
			for bias_param in bias_param_list:
				print "trying parameter set {0}".format(bias_param)
				test.convert(bias_param)
if COUNT:
	print "successfully converted {0} files out of {1} files".format(cnt_success, cnt_total)
	if cnt_total > cnt_success:
		print "problematic files include: "
		for unsuccess_name in unsuccess:
			print "    {0}".format(unsuccess_name)