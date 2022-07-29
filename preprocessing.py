from findLists import updateTeX, surroundQuestion
from skeleton import applySkeleton

import os
import re
import copy
import random

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()

def merge(fname):
	text = loadText(fname)
	
	text = re.sub(r"%(.*)\n", '', text, re.MULTILINE)
	subFiles = re.findall(r"\\input{(.*?)}", text)
	
	for i in subFiles:
		text = text.replace(r"\input{"+i+"}", "\n"+merge(i)+"\n")
	return text

def process(config):
	text = merge(config["input"])

	#text = text.replace(",,,,", "")
	if (config["TeXSkeleton"] != None):
		text = applySkeleton(text, config["TeXSkeleton"])

	if not config["keep-minipages"]:
		text = re.sub(r"(.*?){minipage}(.*?)\n", "", text)

	# remove comments
	text = re.sub(r"%(.*)\n", '', text, re.MULTILINE)
	
		# remove raisebox and fbox
	text = re.sub(r"\\raisebox{(.*?)}{((.|\n)*?)}", r"\2", text)
	text = re.sub(r"\\fbox{((.|\n)*?)}", r"\1", text)
	
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
	text = re.sub(r"\\includegraphics\[(.*?)\]{(.*?)}!ALTMARKER! (.*?)\n", 
								r"\\includegraphics[\1]{\2}\n!ALTMARKER! \3\n",
								text,
								re.MULTILINE)
	text = re.sub(r"\\includegraphics\[(.*?)\]{(.*?)}!ALTMARKERS! (.*?)\n",
								r"\\includegraphics[\1]{\2}\n!ALTMARKERS! \3\n",
								text,
								re.MULTILINE)
	text = updateTeX(text)
	if config["TeXSkeleton"] is not None and "bcc" in config["TeXSkeleton"]:
		text = surroundQuestion(text)

	preMarked = []
	for i in re.finditer(r"\\includegraphics\[(.*?)\]{(.*?)}\n!ALTMARKERS! (.*)\n", text):
		s = i.group(0)
		preMarked.append(s)
	preMarked = set(preMarked)
	for i in preMarked:
		if i[-1] == "\n":
			text = text.replace(i, "!IMAGE!\n"+i+"!IMAGE!\n")
		else:
			text = text.replace(i, "!IMAGE!\n"+i+"\n!IMAGE!\n")

	preMarked = []
	for i in re.finditer(r"\\includegraphics\[(.*?)\]{(.*?)}\n!ALTMARKER! (.*)\n", text):
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
