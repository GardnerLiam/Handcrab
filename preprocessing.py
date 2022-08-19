from tikz import renderTikz, removeTikz
from findLists import surroundQuestion, updateTeXLists 
from skeleton import applySkeleton
from findTables import updateLaTeXTables

import os
import re
import sys
import copy
import time
import random
import subprocess
from subprocess import DEVNULL, STDOUT

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()

def tmpWrite(text, path=""):
	base_name = str(random.randint(100000,999999))+".tex"
	while os.path.isfile(os.path.join("", base_name)):
		base_name = str(random.randint(100000,999999))+".tex"
	with open(os.path.join(path, base_name), 'w') as f:
		f.write(text)
	return os.path.join(path, base_name)

applyWhenMerge = ["fixPOTWInput", "removeCTMCHeader"]
applyPreMerge = ["gaussPostdocPreambleKiller", "gaussSolnFixer", "frontCoverRemover", "euclidSolnFixer"]


def merge(fname, functions=[], imageDir="."):
	if not fname.endswith(".tex"):
		fname = fname + ".tex"
	text = loadText(fname)

	text = re.sub(r"(^|\s)%(.*)$", '', text, flags=re.MULTILINE)
	subFiles = re.findall(r"\\input{(.*?)}", text)

	for i in functions:
		if i('') in applyWhenMerge:
			text = i(text)

	subFiles = re.findall(r"\\input{(.*?)}", text)
	for i in subFiles:
		text = text.replace(r"\input{"+i+"}", "\n"+merge(i, functions, imageDir)+"\n")
	return text

def parseBoxes(text):
	boxName = r"\box{"
	start = text.find(boxName)
	if start == -1:
		return text
	end = start
	count = 1
	saveString = ""
	for i in range(start+len(boxName), len(text)):
		saveString+=text[i]
		if text[i] == "{":
			count+=1
		if text[i] == "}":
			count-=1
		if count == 0:
			end = i
			break
	saveString = saveString[:-1]
	return parseBoxes(text.replace(text[start:end+1], saveString))

def mergeAll(filename, config):
	imdir = "." if config["image-folder"] is None else config["image-folder"]
	if config["preprocessing"] is not None:
			text = merge(filename, config["preprocessing"], imdir) 
	else: 
		text = merge(filename, imageDir=imdir)
	while len(re.findall(r"\\input{(.*?)}", text)) != 0:
		tmpName = tmpWrite(text)
		if config["preprocessing"] is not None:
			text = merge(tmpName, config["preprocessing"])
		else:
			text = merge(tmpName)
		os.remove(tmpName)
	return text

def process(config):
	text = loadText(config["input"])
	if config["merge-before"]:
		fname = tmpWrite(text)
		text = mergeAll(fname, config)
		os.remove(fname)
		if (config["TeXSkeleton"] != None):
			text = applySkeleton(text, config["TeXSkeleton"], config)
	else:
		text = re.sub(r"(^|\s)%(.*)$", '', text, flags=re.MULTILINE)
		for i in config["preprocessing"]:
			if i("") in applyPreMerge:
				text = i(text)
		if (config["TeXSkeleton"] != None):
			text = applySkeleton(text, config["TeXSkeleton"], config)
		if ("\\input" in text):
			fname = tmpWrite(text)
			text = mergeAll(fname, config)
			os.remove(fname)
	if not config["disable-tikz"]:
		filename = os.path.split(fname)[1][:-4]
		if config["image-folder"] is None:
			text = renderTikz(text, filename, "", tizkPDF=config["tikz-pdf"])
		else:
			text = renderTikz(text, filename, config["image-folder"], tikzPDF=config["tikz-pdf"])
	else:
		text = removeTikz(text)
	if not config["keep-minipages"]:
		text = re.sub(r"\\(begin|end){minipage}((\[((.|\n)*?)\])?{((.|\n)*?)})?",
									"", text, flags=re.MULTILINE)
	if config["remove-flush"]:
		text = re.sub(r"\\(begin|end){flush(left|right|top|bottom)}", "", text, flags=re.MULTILINE)

	text = re.sub(r"\\(v|h)space{(.*?)}", " ", text, flags=re.MULTILINE)
	# remove raisebox and fbox
	text = re.sub(r"\\raisebox{(.*?)}(\[(.*?)\])?(\[(.*?)\])?", r"\\box", text, flags=re.DOTALL)
	text = re.sub(r"\\parbox(\[(.*?)\])?{(.*?)}", r"\\box", text, flags=re.DOTALL)
	text = re.sub(r"\\fbox", r"\\box", text)
	text = re.sub(r"\\framebox(\[.*?\])?(\[.*?\])?", r"\\box", text)
	text = re.sub(r"\\item\[\$\\bullet\$.?\]", r"\\item", text)
	
	text = parseBoxes(text)

	for rl in re.finditer(r"\\begin{eqnarray\*}(.*?)\\end{eqnarray\*}", text, flags=re.DOTALL):
		body = rl.group(1)
		m = re.search("&(.*?)&", body, flags=re.DOTALL)
		if m is not None:
			m = m.group(0)
			body = body.replace(m, m[:-1])
		text = text.replace(rl.group(1), body)
	for rl in re.finditer(r"\\begin{eqnarray}(.*?)\\end{eqnarray}", text, flags=re.DOTALL):
		body = rl.group(1)
		m = re.search("&(.*?)&", body, flags=re.DOTALL)
		if m is not None:
			m = m.group(0)
			body = body.replace(m, m[:-1])
		text = text.replace(rl.group(1), body)


	text = re.sub(r"\\\\\[(.*?)\]", "\n\n", text)

	# remove phantom characters
	if config["remove-phantom"]:	
		text = re.sub(r"\\phantom{(.*?)}", "", text, flags=re.MULTILINE)

	# remove graphicspath
	text = re.sub(r"\\graphicspath{(.*)}", "", text, flags=re.MULTILINE)
	# remove aleph listing (forces itemize to enumerate if that was ever an issue)
	text = re.sub(r"\\begin{enumerate}\[label=\(\\alph\*\)\]",
								r"\\begin{enumerate}[a.]",
								text, re.MULTILINE)
	text = re.sub(r"\\begin{enumerate}\[label=\(\\Alph\*\)\]",
								r"\\begin{enumerate}[A.]",
								text, re.MULTILINE)
	
	text = re.sub(r"\\begin{itemize}\[label=\(\\alph\*\)\]",
								r"\\begin{enumerate}[a.]",
								text, re.MULTILINE)
	text = re.sub(r"\\begin{itemize}\[label=\(\\Alph\*\)\]",
								r"\\begin{enumerate}[A.]",
								text, re.MULTILINE)

	for rl in re.finditer(r"\\includegraphics\[(.*?)\]{(.*?)}", text):
		size = rl.group(1)
		if not (size.startswith("width=") or size.startswith("height=")):
			newImage = r"\includegraphics[width=0.3\textwidth]{"+rl.group(2)+"}"
			text = text.replace(rl.group(0), newImage)

	
	text = re.sub(r"\\includegraphics{(.*?)}", r"\\includegraphics[width=0.3\\textwidth]{\1}", text)
	
	## Place images on newline
	text = re.sub(r"(\S+)\\includegraphics\[(.*?)\]{(.*?)}((\s|\n)*?)",
								r"\1\n\\includegraphics[\2]{\3}",
								text, flags=re.MULTILINE)

	## Remove whitespace before image
	text = re.sub(r"[^\S\r\n]+\\includegraphics",
								r"\\includegraphics", text, flags=re.MULTILINE)
		

	# put altmarker on new line
		
		
	text = re.sub(r"\\includegraphics\[(.*?)\]{(.*?)}((\s|\n)*?)!(ALTMARKER|NOALT)",
								r"\\includegraphics[\1]{\2}\n!\5",
								text, flags=re.MULTILINE)
	
# find all non-images and add !NOIMAGE!
	text = re.sub(
		r"\\includegraphics\[(.*?)\]{(.*?)}(?!\n(\s+)?(!ALTMARKER!|!ALTMARKERS!|!NOALT!))",
		r"\\includegraphics[\1]{\2}\n!NOALT! ", text, flags=re.MULTILINE)
	
	text = re.sub(
		r"\\includegraphics{(.*?)}(?!\n(\s+)?(!ALTMARKER!|!ALTMARKERS!|!NOALT!))",
		r"\\includegraphics{\1}\n!NOALT!\n",
		text, flags=re.MULTILINE)

	text = re.sub(r"(.*)$(^|(\s.*?))!ROW(COL)?TABLE!",
								r"\1\n\2\n\n!ROW\4TABLE!", text, flags=re.MULTILINE)
	
	text = re.sub("!ROW(COL)?TABLE!(.*?)\n(.*?)$", r"!ROW\1TABLE!\n\n\2\n\3",
								text, flags=re.MULTILINE)

	text = re.sub(r"(.*)$(^|(\s.*?))!LONGDESC!",
								r"\1\n\n!LONGDESC!",
								text,
								flags=re.MULTILINE)

	text = re.sub(r"!LONGDESC!(.*?)\n(.*?)$",
								r"!LONGDESC! \1\n\n\2",
								text,
								flags=re.MULTILINE)
	for i in config['preprocessing']:
		if i('') not in applyWhenMerge and i('') not in applyPreMerge:
			text = i(text)
	
	text = updateLaTeXTables(text)
	if config["TeXSkeleton"] is not None and "bcc" in config["TeXSkeleton"]:
		text = surroundQuestion(text)

	body = text[text.find("\\begin{document"):text.find("\\end{document")]
	newBody = updateTeXLists(body)
	text = text.replace(body, newBody)

	text = re.sub(r"(\\includegraphics(\[(.*?)\])?{(.*?)}\n!(ALTMARKER|NOALT)(S?)![^}\n\\&]+)",
								r"!IMAGE!\n\1\n!IMAGE!\n", text)

	text = re.sub(r"\\hfill ?{", r"\\box{", text)
	text = parseBoxes(text)

	if "nowrite" in config and config["nowrite"] == True:
		return text
	# generate temp name (probably not a great strategy)
	base_name = str(random.randint(100000,999999))+".tex"
	while (os.path.isfile(base_name)):
		base_name = str(random.randint(100000,999999))+".tex"

	with open(base_name, 'w') as f:
		f.write(text)
	return base_name
