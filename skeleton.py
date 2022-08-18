import re
import os

EXE_LOCATION = os.path.dirname( os.path.realpath( __file__ ) )

# template ==> compile type, contains parameters & such
# skeleton ==> base file, contains HTML preamble.

skeletons = {
	"cccProblem": "CCCProblem.html",
	"cccFull": "CCCSkeletonFull.html",
	"bccTeX": "BCCSkeleton.tex",
	"bccFull": "BCCSkeleton.html",
	"potm": "POTM.html",
	"potw": "POTW.html",
	"mcLesson": "MathCirclesLesson.html",
	"mcProbset": "MathCirclesProblemSet.html",
	"mcSoln": "MathCirclesSolution.html",
	"ctmc": "CTMC.html",
	"gaussTeX": "GaussPCFContest.tex",
	"pcfTeX": "GaussPCFContest.tex",
	"gaussContest": "GaussContest.html",
	"gaussSolnTeX": "GaussPCFSolution.tex",
	"pcfSolnTeX": "GaussPCFSolution.tex",
	"pcfContest":"PCFContest.html", 
	"euclidTeX": "EuclidContest.tex",
	"euclidContest": "EuclidContest.html",
	"tikz": "rendertikz.tex",
	"default": "default.html"
}

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()


def grabBody(text):
	a = re.findall(r"<body>((.|\n)*?)</body>", text)
	return a[0][0]

def grabTeXBody(text):
	if ("{document}" in text):
		start = text.find(r"\begin{document}")+len(r"\begin{document}")
		if r"\bccSep{" in text:
			start = text.find(r"\bccSep{")
		end = text.find(r"\end{document}")
		return text[start:end]
	else:
		return text

'''
- probably path addition required?
'''

# someone remind me to NOT have this here in prod plz
def getFile(skeleton):
	for i in skeletons:
		if skeleton.casefold() == i.casefold():
			return os.path.join(EXE_LOCATION, "skeletons", skeletons[i])
	return skeleton
	raise ValueError("{} is not a valid skeleton".format(skeleton))

def applySkeleton(text, skeleton, config, write=""):
	skfile = getFile(skeleton)
	with open(skfile, 'r') as f:
		temp = f.read()
	if skfile.endswith(".html"):
		temp = temp.replace("<p>Content</p>", grabBody(text))
		if "css" in config and len(config["css"]) > 0:
			temp = re.sub(r'@import url\("(.*?)"\)', r'@import url("{}")'.format(config["css"]), temp)
		if "title" in config and len(config["title"]) > 0:
			temp = re.sub(r"<title>((.|\n)*?)<\/title>",
										"<title>{}</title>".format(config["title"]), temp)
		else:
			title = "TITLE" 
			m1 = re.search(r"<h1(.*?)>(.*?)<\/h1>", text, flags=re.DOTALL)
			if m1 is not None:
				if m1.group(2) is not None:
					title = re.sub(r"(.*?)(?:<.*?>|$)", r"\1", m1.group(2), flags=re.MULTILINE).replace("\n"," ")
			temp = re.sub(r"<title>((.|\n)*?)<\/title>", "<title>{}</title>".format(title), temp)
		if "postskeletonprocessing" in config and len(config["postskeletonprocessing"]) > 0:
			for i in config["postskeletonprocessing"]:
				temp = i(temp)
		temp = re.sub(r"<p>(\s+)?<\/p>", "", temp)
	elif skfile.endswith(".tex"):
		temp = temp.replace("%!CONTENT!%", grabTeXBody(text))
	if len(write) > 0:
		with open(write, 'w') as f:
			f.write(temp)
	else:
		return temp


