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
	start = text.find(r"\bccSep{")
	end = text.find(r"\end{document}")
	return text[start:end]

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

# should probably change templates to skeletons here
def applySkeleton(text, skeleton, write="", css=""):
	skfile = getFile(skeleton)
	with open(skfile, 'r') as f:
		temp = f.read()
	if skfile.endswith(".html"):
		#updateCSS would be called here
		temp = temp.replace("<p>Content</p>", grabBody(text))
		if len(css) > 0:
			temp = re.sub(r'@import url\("(.*?)"\)', r'@import url("{}")'.format(css), temp)
	elif skfile.endswith(".tex"):
		temp = temp.replace("%!CONTENT!%", grabTeXBody(text))
	if len(write) > 0:
		with open(write, 'w') as f:
			f.write(temp)
	else:
		return temp
