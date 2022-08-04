from findLists import updateTeX, surroundQuestion
from skeleton import applySkeleton
from findTables import updateLaTeXTables


import os
import re
import copy
import random

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()

def tmpWrite(text):
	base_name = str(random.randint(100000,999999))+".tex"
	while os.path.isfile(base_name):
		base_name = str(random.randint(100000,999999))+".tex"
	with open(base_name, 'w') as f:
		f.write(text)
	return base_name

applyWhenMerge = ["fixPOTWInput", "removeCTMCHeader"]

def merge(fname, functions=[]):
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
		text = text.replace(r"\input{"+i+"}", "\n"+merge(i, functions)+"\n")
	return text

def process(config):
	if config["preprocessing"] is not None:
		text = merge(config["input"], config["preprocessing"])
	else: 
		text = merge(config["input"])

	while len(re.findall(r"\\input{(.*?)}", text)) != 0:
		tmpName = tmpWrite(text)
		if config["preprocessing"] is not None:
			text = merge(tmpName, config["preprocessing"])
		else:
			text = merge(tmpName)
		os.remove(tmpName)
	
	if (config["TeXSkeleton"] != None):
		text = applySkeleton(text, config["TeXSkeleton"])

	if not config["keep-minipages"]:
		text = re.sub(r"\\(begin|end){minipage}((\[((.|\n)*?)\])?{((.|\n)*?)})?",
									"", text, flags=re.DOTALL)

	# remove raisebox and fbox
	text = re.sub(r"\\raisebox{(.*?)}{((.|\n)*?)}", r"\2", text)
	text = re.sub(r"\\fbox{((.|\n)*?)}", r"\1", text)
	
	# remove phantom characters
	text = re.sub(r"\\phantom{(.*?)}", "", text, flags=re.MULTILINE)

	# remove graphicspath
	text = re.sub(r"\\graphicspath{(.*)}", "", text, flags=re.MULTILINE)
	# remove aleph listing (forces itemize to enumerate if that was ever an issue)
	text = re.sub(r"\\begin{enumerate}\[label=\(\\alph\*\)\]",
								r"\begin{enumerate}[a.]",
								text, re.MULTILINE)
	text = re.sub(r"\\begin{enumerate}\[label=\(\\Alph\*\)\]",
								r"\begin{enumerate}[A.]",
								text, re.MULTILINE)
	
	text = re.sub(r"\\begin{itemize}\[label=\(\\alph\*\)\]",
								r"\begin{enumerate}[a.]",
								text, re.MULTILINE)
	text = re.sub(r"\\begin{itemize}\[label=\(\\Alph\*\)\]",
								r"\begin{enumerate}[A.]",
								text, re.MULTILINE)
	'''	
	text = re.sub(r"(.)\\includegraphics\[((.|\n)*?)\]{((.|\n)*?)}",
								r"\1\n\\includegraphics[\2]{\4}",
								text)
	'''
	
	# put altmarker on new line
	text = re.sub(r"^([^\n]\s+)\\includegraphics",
								r"\\includegraphics", text, flags=re.MULTILINE)
	
	text = re.sub(r"(\s+)?!ALTMARKER",
								"!ALTMARKER", text, re.MULTILINE)
	
	text = re.sub(r"\\includegraphics\[(.*?)\]{(.*?)}((\s|\n)*?)!(ALTMARKER|NOALT)",
								r"\\includegraphics[\1]{\2}\n!\5",
								text, flags=re.MULTILINE)
	
	'''
	text = re.sub(r"\\includegraphics\[(.*?)\]{(.*?)}!ALTMARKER! (.*?)\n", 
								r"\\includegraphics[\1]{\2}\n!ALTMARKER! \3\n",
								text,
								re.MULTILINE)
	text = re.sub(r"\\includegraphics\[(.*?)\]{(.*?)}!ALTMARKERS! (.*?)\n",
								r"\\includegraphics[\1]{\2}\n!ALTMARKERS! \3\n",
								text,
								re.MULTILINE)
	text = re.sub(r"\\includegraphics\[(.*?)\]{(.*?)}!NOALT!(.*?)\n",
								r"\\includegraphics[\1]{\2}\n!NOALT!\3\n",
								text,
								re.MULTILINE)	
	'''
	text = re.sub(r"(.*)$(^|(\s.*?))!LONGDESC!",
								r"\1\n\n!LONGDESC!",
								text,
								flags=re.MULTILINE)

	text = re.sub(r"!LONGDESC!(.*?)\n(.*?)$",
								r"!LONGDESC! \1\n\n\2",
								text,
								flags=re.MULTILINE)
	text = updateTeX(text)
	text = updateLaTeXTables(text)
	for i in config['preprocessing']:
		if i('') not in applyWhenMerge:
			text = i(text)
	if config["TeXSkeleton"] is not None and "bcc" in config["TeXSkeleton"]:
		text = surroundQuestion(text)

	preMarked = []
	for i in re.finditer(r"\\includegraphics(\[(.*?)\])?{(.*?)}\n!ALTMARKERS! (.*)\n", text):
		s = i.group(0)
		preMarked.append(s)
	preMarked = set(preMarked)
	for i in preMarked:
		if i[-1] == "\n":
			text = text.replace(i, "!IMAGE!\n"+i+"!IMAGE!\n")
		else:
			text = text.replace(i, "!IMAGE!\n"+i+"\n!IMAGE!\n")

	# find all non-images and add !NOIMAGE!
	text = re.sub(
		r"\\includegraphics\[(.*?)\]{(.*?)}(?!\n(^|\s+)!ALTMARKER!|(^|\s+)!ALTMARKERS!|(^|\s+)!NOALT!)",
		r"\\includegraphics[\1]{\2}\n!ALTMARKER! image", text, flags=re.DOTALL)
	
	text = re.sub(
		r"\\includegraphics{(.*?)}(?!\n(^|\s+)!ALTMARKER!|(^|\s+)!ALTMARKERS!|(^|\s+)!NOALT!)",
		r"\\includegraphics{\1}\n!NOALT!\n",
		text, flags=re.DOTALL)

	preMarked = []
	for i in re.finditer(r"\\includegraphics(\[(.*?)\])?{(.*?)}\n!ALTMARKER! (.*)\n", text):
		s = i.group(0)
		preMarked.append(s)
	preMarked = set(preMarked)
	for i in preMarked:
		if i[-1] == "\n":
			text = text.replace(i, "!IMAGE!\n"+i+"!IMAGE!\n")
		else:
			text = text.replace(i, "!IMAGE!\n"+i+"\n!IMAGE!\n")

	preMarked = []
	for i in re.finditer(r"\\includegraphics(\[(.*?)\])?{(.*?)}\n!NOALT!(.*)\n", text):
		s = i.group(0)
		preMarked.append(s)
	preMarked = set(preMarked)
	for i in preMarked:
		if i[-1] == "\n":
			text = text.replace(i, "!IMAGE!\n"+i+"!IMAGE!\n")
		else:
			text = text.replace(i, "!IMAGE!\n"+i+"\n!IMAGE!\n")

	if "nowrite" in config and config["nowrite"] == True:
		return text
	# generate temp name (probably not a great strategy)
	base_name = str(random.randint(100000,999999))+".tex"
	while (os.path.isfile(base_name)):
		base_name = str(random.randint(100000,999999))+".tex"

	with open(base_name, 'w') as f:
		f.write(text)
	return base_name
