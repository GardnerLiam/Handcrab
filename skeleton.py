import re
import os
from findLists import updateCSS

EXE_LOCATION = os.path.dirname( os.path.realpath( __file__ ) )

# template ==> compile type, contains parameters & such
# skeleton ==> base file, contains HTML preamble.

skeletons = {
	"cccProblem": "CCCProblemTemplate.html",
	"cccFull": "CCCSkeletonFull.html",
	"bccTeX": "BCCSkeleton.tex",
	"bccFull": "BCCSkeleton.html",
	"potm": "POTM.html",
	"potw": "POTW.html",
	"mcLesson": "MathCirclesLesson.html",
	"mcProbset": "MathCirclesProblemSet.html",
	"mcSoln": "MathCirclesSolution.html",
	"ctmc": "CTMC.html",
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
			title = re.search(r"<h1(.*?)>((.|\n)*?)<(\/h1|br)", text)
			if (title is not None):
				title = title.group(2)
				temp = re.sub(r"<title>((.|\n)*?)<\/title>", "<title>{}</title>".format(title), temp)
	elif skfile.endswith(".tex"):
		temp = temp.replace("%!CONTENT!%", grabTeXBody(text))
	if len(write) > 0:
		with open(write, 'w') as f:
			f.write(temp)
	else:
		return temp

'''
def applySkeleton(text, skeleton, write="", css="", title=""):
	skfile = getFile(skeleton)
	with open(skfile, 'r') as f:
		temp = f.read()
	if skfile.endswith(".html"):
		temp = temp.replace("<p>Content</p>", grabBody(text))
		if len(css) > 0:
			temp = re.sub(r'@import url\("(.*?)"\)', r'@import url("{}")'.format(css), temp)
		if len(title) == 0:
			title = re.search(r"<h1>((.|\n)*?)<(br|\/h1)", text)
			if (title is not None):
				title = title.group(1)
				temp = re.sub(r"<title>((.|\n)*?)<\/title>", "<title>{}</title>".format(title), temp)
		else:
			temp = re.sub(r"<title>((.|\n)*?)<\/title>", "<title>{}</title>".format(title), temp)

	elif skfile.endswith(".tex"):
		temp = temp.replace("%!CONTENT!%", grabTeXBody(text))
	if len(write) > 0:
		with open(write, 'w') as f:
			f.write(temp)
	else:
		return temp
'''
