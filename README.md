# Converting Chinese Pdf to HTML

pdfminer-20140328/ & pdftables-0.0.4/: Libraries' source code, could be downloaded from their official websites

test/: something I did when testing the basic functions of pdfminer, might give you an insight on what's going on by providing you with the simple version of the code. They are extended to more complex implementation latter.

mycode/: this is my implementation on converting pdf files to HTML files

mycode/pdfminer/: the necessary files from pdfminer library

mycode/data/: where all input (PDF) & output (HTML) files are located at

mycode/convert.py: this is the file served as the main entrance; you assign the name (and path) of the files you are to convert and then run it to convert the files. A function (get_PDF_fnames) is provided to collect all PDF files that are located under a certain directory.

mycode/simplePDF2html.py: here I implemented a class called simplePDF2HTML, which is capable of extracting text contents from a given PDF file, as well as tables and their contents (it works well for most of the cases), outlines of the file (and I embedded the reference links into the generated HTML files, making the outlines clickable; error-free for most cases).

