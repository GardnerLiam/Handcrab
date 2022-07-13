import re
import os
import sys

def getLongest(string, c):
	count = 1
	while c*count in string:
		count+=1
	return count-1

def findAll(string, sub):
	start = 0
	while True:
		start = string.find(sub, start)
		if start == -1:
			return
		yield start
		start += len(sub) or 1


filein = sys.argv[1]
fileout = filein[:filein.rfind(".")] + "_clean"+filein[filein.rfind("."):]


location = os.environ["HANDCRAB_HOME"]+"/"

preamble = ""
with open(location+"Templates/preamble.tex", 'r') as f:
	preamble = f.read()

text = ""

with open(filein, 'r') as f:
	text = f.read()
filestart = text.find("\\begin{document}")
text = preamble + text[filestart:]

text = text.replace("\\begin{frame}", "")
text = text.replace("\\end{frame}", "")
text = text.replace("\\textcolor{NavyBlue}", "\\subsection")

subsections = list(findAll(text, "{\\subsection"))

newText = text[:]

for i in subsections:
	depth = 1
	for j in range(i+1, len(text)):
		if text[j] == "{":
			depth+=1
		if text[j] == "}":
			depth -= 1
		if depth == 0:
			j+=1
			break
	if depth == 0:
		substring = text[i:j]
		newstring = substring[1:-1]
		newText = newText.replace(substring, newstring)
		

text = newText[:]
newText = text[:]
subsections = list(findAll(text, "\\subsection{"))

lookedAt = []
for i in subsections:
	startingIndex = i+12
	for j in range(startingIndex, len(text)):
		if text[j] == "}":
			j+=1
			break
	if text[i:j] not in lookedAt:
		lookedAt.append(text[i:j])

for i in lookedAt:
	while newText.count(i) > 1:
		newText = ''.join(newText.rsplit(i, 1))
	
text = newText[:]

while getLongest(text, "\n") > 2:
	length = getLongest(text, "\n")
	text = text.replace("\n"*length, "\n\n")

text = text.split("\n")
for i in range(len(text)):
	if text[i].startswith(" "):
		text[i] = text[i][1:]
text = "\n".join(text)

with open(fileout, 'w') as f:
	f.write(text)
