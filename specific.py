import re
import os


EXE_LOCATION = os.path.dirname( os.path.realpath( __file__ ) )

getFile = lambda f: os.path.join(EXE_LOCATION, "skeletons", "POTW", f)

def loadText(fname):
	with open(os.path.join(EXE_LOCATION, "skeletons", fname), 'r') as f:
		return f.read()

def fixPOTWInput(text):
	if (text == ""):
		return "fixPOTWInput"	
	text = text.replace("../../Templates/FormatTemplate", getFile("FormatTemplate.tex"))
	text = text.replace("../../Templates/ProblemTemplate", getFile("ProblemTemplate.tex"))
	text = text.replace("../../Templates/SolutionTemplate", getFile("SolutionTemplate.tex"))
	
	text = text.replace(r"\input{\formatTemplate}", r"\input{"+getFile("FormatTemplate.tex")+"}")
	text = text.replace(r"\input{\problemTemplate}", r"\input{"+getFile("ProblemTemplate.tex")+"}")
	text = text.replace(r"\input{\solutionTemplate}", r"\input{"+getFile("SolutionTemplate.tex")+"}")

	return text

def fixPOTWNoImage(text):
	if text == "":
		return "fixPOTWNoInput"
	if 'src="NONE"' in text or 'src=""' in text:
		text = re.sub(r'<img(.*?)src="NONE"(.*?)>(<br(.*?)>)?', "", text)
	return text

def fixPOTWNoTheme(text):
	if text == "":
		return "fixPOTWNoTheme"
	if r"<p><strong>Theme</strong>:</p>" in text:
		text = text.replace(r"<p><strong>Theme</strong>:</p>", "")
	return text

def fixPOTWTheme(text):
	if text == "":
		return "fixPOTWTheme"
	text = re.sub(r"<p><strong>Theme<\/strong>:(.*?)<\/p>", 
								r'<p><span class="smallcaps"><strong>theme:</strong>\1</span></p>',
								text)
	return text

def getStarting(t1, l2, offset=0):
	start = t1.find(l2[0])
	if start == -1:
		return -1
	l2Copy = l2[:]
	textCopy = t1[start:].split("\n")
	for i in range(len(textCopy)):
		textCopy[i] = re.sub(r"^\s+", "", textCopy[i], flags=re.MULTILINE)
	for i in range(len(l2)):
		if textCopy[i] != l2[i]:
			return getStarting(t1[start+len(l2[0]):], l2, offset+start+len(l2[0]))
	return start+offset

def removeCTMCHeader(text):
	if text == "":
		return "removeCTMCHeader"
	htext = loadText("CTMCLogo.txt")
	l2 = htext.split("\n")[:17]
	l3 = htext.split("\n")[18:]
	if l3[-1] == "":
		l3 = l3[:-1]
	clist = l2[:]
	starting = getStarting(text, l2)
	if starting == -1:
		starting = getStarting(text, l3)
		clist = l3[:]
	if starting == -1:
		m = re.findall(r"\\includegraphics\[(.*?)\]{\.\.\/Logos\/CEMC_Banner\.png}", text, flags=re.MULTILINE)
		text = re.sub(r"\\includegraphics\[(.*?)\]{\.\.\/Logos\/CEMC_Banner\.png}", "", text, flags=re.MULTILINE)
		return text
	end = text.find(clist[-1])+len(clist[-1])
	body = text[starting:end+1]
	text = text.replace(body, "")
	
	m = re.findall(r"\\includegraphics\[(.*?)\]{\.\.\/Logos\/CEMC_Banner\.png}", text, flags=re.MULTILINE)
	text = re.sub(r"\\includegraphics\[(.*?)\]{\.\.\/Logos\/CEMC_Banner\.png}", "", text, flags=re.MULTILINE)
	return text


def fixCTMCRelayCommand(text):
	if text == "":
		return "fixCTMCRelayCommand"

	ntext = re.sub("(^|\s)%(.*)$", "", text, flags=re.MULTILINE)

	match = r"\newcommand{\relay}[4]{"
	start = ntext.find(match)
	end = start
	
	count = 1
	for i in range(start+len(match), len(ntext)):
		if count == 0:
			end = i+1
			break
		if ntext[i] == "{":
			count+=1
		elif ntext[i] == "}":
			count-=1
	if start == -1 or end == -1:
		return text
	before = text[:start]
	after = text[end+1:]
	with open(os.path.join(EXE_LOCATION, "skeletons", "ctmcRelayTex.txt"), 'r') as f:
		ctmcRelay = f.read()
	return text.replace(text[start:end], ctmcRelay)


def fixCTMCSolutions(text):
	if text == "":
		return "fixCTMCSolutions"
	if r"newcommand{\ans}" in text:
		preface = ["\\documentclass[a4paper]{article}",
							 "\\begin{document}",
							 "\\newcommand{\\ans}[1]{"+"\n\n"+"Answer: #1\n}\n"]
		preface = "\n".join(preface)
		text = preface + re.sub(r"(.*?)newcommand{\\ans}(.*?)$", "", text, flags=re.MULTILINE)
	return text
