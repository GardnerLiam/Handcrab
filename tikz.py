from skeleton import applySkeleton 

import re
import os
import shutil
from subprocess import DEVNULL, STDOUT, check_call, Popen

def findPictures(text, start):
	count = 1
	blength = len("\\begin{tikzpicture}")
	elength = len("\\end{tikzpicture}")
	if text[start:start+blength] == "\\begin{tikzpicture}":
		start = start + blength 
	for i in range(start, len(text)-blength):
		if text[i:i+blength] == "\\begin{tikzpicture}":
			count+=1
		if text[i:i+elength] == "\\end{tikzpicture}":
			count-=1
		if count == 0:
			return i+elength
	if text[-elength:] == "\\end{tikzpicture}":
		return len(text)


def parseTikz(text):
	tikz = []
	for i in [m.start() for m in re.finditer(r"\\begin{tikzpicture}", text)]:
		tikz.append(text[i:findPictures(text, i)])
	return tikz

def removeTikz(text):
	tikz = parseTikz(text)
	for i in tikz:
		text = text.replace(i, "")
	return text

def renderTikz(text, prefix, image_folder, tikzPDF=False):
	makeSVG = shutil.which("inkscape") is not None
	if (tikzPDF == True):
		makeSVG = False
	tikz = parseTikz(text)
	if not os.path.isdir("tmp/"):
		os.mkdir("tmp/")
	for i in range(len(tikz)):
		fname = os.path.join("tmp", "{}.tex".format(i))
		applySkeleton(tikz[i], "tikz", {}, "tmp/{}.tex".format(i))
		check_call(["pdflatex", "--output-directory=tmp", fname], stdout=DEVNULL, stderr=STDOUT)
	for i in range(len(tikz)):
		pdfname = os.path.join("tmp", "{}.pdf".format(i))
		check_call(["pdfcrop", "--margins", '3', pdfname], stdout=DEVNULL, stderr=STDOUT)
		incgl_name = os.path.join(image_folder, prefix+"{}".format(i))
		if makeSVG:
			incgl_name += ".svg"
		else:
			incgl_name += ".pdf"
		incgl = "\\includegraphics[width=0.3\\textwidth]{"+incgl_name+"}"
		text = text.replace(tikz[i], incgl)
	for i in [os.path.join("tmp", j) for j in os.listdir("tmp")]:
		if "-crop" not in i:
			os.remove(i)
	#Popen(["inkscape", "--export-type=svg", "tmp/*.pdf"], shell=True)
	if (makeSVG):
		check_call(["inkscape", "--export-type=svg", "tmp/*.pdf"], shell=True)
		for i in [os.path.join("tmp", j) for j in os.listdir("tmp")]:
			if not i.endswith(".svg"):
				os.remove(i)
			else:
				name = os.path.split(i)[1]
				os.rename(i, os.path.join(image_folder, prefix+name.replace("-crop", "")))
	else:
		for i in [os.path.join("tmp", j) for j in os.listdir('tmp')]:
			name = os.path.split(i)[1]
			os.rename(i, os.path.join(image_folder, prefix+name.replace("-crop", "")))
	shutil.rmtree("tmp/")
	return text
