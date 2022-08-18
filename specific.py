import re
import os
import sys


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

def getCloseBracket(text, start):
	count = 1
	for i in range(start, len(text)):
		if text[i] == "{":
			count+=1
		if text[i] == "}":
			count-=1
		if count == 0:
			return i+1
	return -1

def frontCoverRemover(text):
	if text == "":
		return "frontCoverRemover"

	start = text.find("\\begin{document}")
	if start == -1:
		return text
	sub = text[start:]
	q = [m.start() for m in re.finditer(r"{\\.*?front", sub)]
	while len(q) > 0:
		end = getCloseBracket(sub, q[0]+1)
		sub = sub.replace(sub[q[0]:end], "")
		q = [m.start() for m in re.finditer(r"{\\.*?front", sub)]
	text = text.replace(text[start:], sub)


	
	text = re.sub(r"\\ifthenelse.*?$", "", text, flags=re.MULTILINE)
	text = re.sub(r"{\\.*?backcover.*?$", "", text, flags=re.MULTILINE)
	return text

def gaussPostdocPreambleKiller(text):
	if text == "":
		return "gaussPostdocPreambleKiller"
	start = text.find("\\begin{document}")
	if start == -1:
		return text
	text = frontCoverRemover(text)
	
	text = re.sub(r"\\ifthenelse(.*?)$", "", text, flags=re.MULTILINE)
	sectionTemplate = "\\subsection{Part X: Each correct answer is worth Y.}"

	for i in re.finditer(r"{\\part.(.?)}(\n?){\\part(.)}", text):
		partTitle = i.group(3).upper()
		points = {"A":"5", "B":"6", "C":"8"}[partTitle]
		text = text.replace(i.group(0), sectionTemplate.replace("X", partTitle).replace("Y", points))

	if ("\\subsection{Part A" not in text):
		start = text.find("\\mc")
		sc = sectionTemplate.replace("X", "A").replace("Y", "5")+'\n'
		text = text[:start]+sc+text[start:]	
		#text = text[:start] + sectionTemplate.replace("X", "A").replace("Y", "5")+"\n"+text[:start]

	text = text.replace("\\end{MCQ}", "")
	return text

def gaussSectionFixer(text):
	if text == "":
		return "gaussSectionFixer"
	firstTime = True
	count = 1
	for i in re.finditer(r"\\subsection{(.*?)}(.*?)(?=(\\subsection{(.*?)}|\\end{enumerate}))",
					text, flags=re.DOTALL):
		if firstTime:
			text = text.replace(i.group(0), r"\subsection{"+i.group(1)+"}\n\\begin{enumerate}\n"+i.group(2))
			count = i.group(0).count("\\mc")+1
			firstTime = False
			continue
		new = "\\end{enumerate}\n!HRULE!\n"
		new += "\\subsection{"+i.group(1)+"}\n\n\\begin{enumerate}["+str(count)+".]\n\n"+i.group(2)
		count += i.group(0).count("\\mc")
		text = text.replace(i.group(0), new)
	return text

def gaussTitleFixer(text):
	if text == "":
		return "gaussTitleFixer"
	title = re.search(r"<h1(.*?)?>(....) (.*?)<(\/(div|section)|h2)", text, flags=re.DOTALL)
	if title is not None:
		year = title.group(2)
		headerCharacteristic = title.group(1)
		if headerCharacteristic is None:
			headerCharacteristic = ""
		fullTitle = "<h1"+headerCharacteristic+">"+year+" "+title.group(3)
		text = text.replace(fullTitle, "")
		text = text.replace("!!!TITLECONTENT!!!", fullTitle)
		text = text.replace("&copy;YYYY University of Waterloo", "&copy;"+year+" University of Waterloo")
	return text

def pcfTitleFixer(text, currentContest="CURRENTCONTEST", nextContest="NEXTCONTEST"):
	if text == "":
		return "pcfTitleFixer"
	text = text.replace("!CONTESTCURRENT!", currentContest)
	text = text.replace("!CONTESTNEXT!", nextContest)
	return text

def gaussSolnFixer(text):
	if text == "":
		return "gaussSolnFixer"
	text = re.sub(r"\\input{(.*?)TemplateFiles(.*?)}", "", text)
	text = re.sub(r"\\ifthenelse(.*?)$", "", text, flags=re.MULTILINE)
	text = re.sub(r"\\(begin|end){GA}", "", text)
	start = [m.start() for m in re.finditer(r"(.*?)Grade 7(.*?)$", text, flags=re.MULTILINE)][0]
	potential = [m.start() for m in re.finditer(r"(.*?)7\\ieme(.*?)$", text, flags=re.MULTILINE)]
	potential += [m.start() for m in re.finditer(r"(\\begin{center}(.*?))?\\section{(.*?)}",
																							text, flags=re.DOTALL)]
	if len(potential) > 0:
		start = min(start, potential[0]) 
	end = [m.start()+len(m.group(0)) for m in 
				re.finditer(r"(.*?)\\end{itemize}(.*?)$", text, flags=re.MULTILINE)][-1]
	
	subText = text[start:end+1]
	#subText = re.sub(r"{(.*?)\\(begin|end){itemize}(.*?)}",
	#									r"{\1\n\3}\n\\\2{itemize}", subText, flags=re.DOTALL)
	#subText = re.sub(r"{(\s+)?}", "", subText)

	text = "\\begin{document}\n"+subText+"\n\\end{document}"
	return text

def euclidSolnFixer(text):
	if text == "":
		return "euclidSolnFixer"
	text = re.sub(r"\\input{(.*?)TemplateFiles(.*?)}", "", text)
	text = re.sub(r"\\ifthenelse(.*?)$", "", text, flags=re.MULTILINE)
	
	text = re.sub(r"{\\(begin|end){(enumerate|itemize)}}", r"\\\1{\2}", text)
	text = re.sub(r"{\\(begin|end){GA}}", "", text)

	s1 = text.find("\\begin{center}")
	s2 = text.find("\\begin{itemize}")

	if s1 == -1:
		s1 = len(text)
	if s2 == -1:
		s2 = len(text)

	start = min(s1, s2)
	text = "\\begin{document}\n"+text[start:]
	return text

def euclidItemization(text):
	if text == "":
		return "euclidItemization"
	start = text.find("\\begin{document}")
	body = text[start:]
	body = re.sub(r"\\item\[([0-9]+)\](.*?)(?=((\\item\[[0-9]+\])|\\end{INST}))",
								r"\\item[\1] \n\\begin{enumerate}[a]\n\2\n\\end{enumerate}\n",
								body, flags=re.DOTALL)
	text = text.replace(text[start:], body)
	text = re.sub(r"\\(begin|end){INST}", "", text)

	title = re.search(r"\\begin{center}(.*?)\\section{", text, flags=re.DOTALL)
	if title is not None:
		title = title.start()
		end = title+text[title:].find("\\end{center}")+len("\\end{center}")

		if title > start+text[start:].find("\\begin{enumerate}"):
			fullTitle = text[title:end]
			text = text.replace(fullTitle, "")
			text = text.replace("\\begin{document}", "\\begin{document}\n"+fullTitle)
	

	return text



def pcfTitleSpecifier(filename):
	if "cayley" in filename.lower():
		return lambda text: pcfTitleFixer(text, "Cayley", "Galois")
	elif "pascal" in filename.lower():
		return lambda text: pcfTitleFixer(text, "Pascal", "Fryer")
	elif "fermat" in filename.lower():
		return lambda text: pcfTitleFixer(text, "Fermat", "Hypatia")
	return pcfTitleFixer 


def fixCTMCSolutions(text):
	if text == "":
		return "fixCTMCSolutions"
	if r"newcommand{\ans}" in text:
		rl = re.finditer(r"(.*?)newcommand{\\ans}(.*?){", text, flags=re.MULTILINE)
		for i in rl:
			body = i.group(0)
			start = text.find(body)+len(body)
			end = getCloseBracket(text, start)
			if end == -1:
				print("Skipping:")
				print(body)
				continue
			fullBody = text[text.find(body):end]
			text = text.replace(fullBody, "")

		preface = ["\\documentclass[a4paper]{article}",
							 "\\begin{document}",
							 "\\newcommand{\\ans}[1]{"+"\n\n"+"Answer: #1\n}\n"]
		if "begin{document}" in text:
			preface.pop(1)
		if "documentclass" in text:
			preface.pop(0)
		preface = "\n".join(preface)
		text = preface + re.sub(r"(.*?)newcommand{\\ans}(.*?)$", "", text, flags=re.MULTILINE)
	return text
