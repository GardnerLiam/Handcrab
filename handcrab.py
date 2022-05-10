import re
import os
import sys

import argparse

import xml.etree.ElementTree as ET

def tableToString(tableData, filename="output.xml"):
	tableData = tableData.replace("><", ">!!!IGNOREME!!!<")
	tree = ET.ElementTree(ET.fromstring(tableData))
	tree.write(filename)
	text = ""
	with open(filename, 'r') as f:
		text = f.read()
	text = text.replace(">!!!IGNOREME!!!<", "><")
	os.remove("output.xml")
	return text

def parseRowTable(substring):
	tableData = substring[substring.find("<table"):substring.find("</table")+8]
	tableData = tableData.replace("<tbody>", "")
	tableData = tableData.replace("</tbody>", "")
	tableData = tableToString(tableData)
	tableData = tableData.split("\n")
	tableData = list(filter(lambda a: a != "", tableData))
	rowTagInstances = [j for j in range(len(tableData)) if "<tr" in tableData[j]]
	for j in rowTagInstances:
		tableData[j+1] = tableData[j+1].replace("<td", '<th scope="row"')
		tableData[j+1] = tableData[j+1].replace("</td", "</th")
	tableData = "\n".join(tableData)
	return tableData

def parseRowColTable(substring):
	tableData = substring[substring.find("<table"):substring.find("</table")+8]
	tableData = tableData.replace("<tbody>", "")
	tableData = tableData.replace("</tbody>", "")
	tableData = tableToString(tableData)
	tableData = tableData.split("\n")
	tableData = list(filter(lambda a: a != "", tableData))
	rowTagInstances = [j for j in range(len(tableData)) if "<tr" in tableData[j]]
	for j in range(rowTagInstances[0]+2, rowTagInstances[1]):
		tableData[j] = tableData[j].replace("<td", '<th scope="col"')
		tableData[j] = tableData[j].replace("</td", "</th")
	rowTagInstances = rowTagInstances[1:]
	for j in rowTagInstances:
		tableData[j+1] = tableData[j+1].replace("<td", '<th scope="row"')
		tableData[j+1] = tableData[j+1].replace("</th", '</th')
	tableData = '\n'.join(tableData)
	return tableData

def parseAltText(substring):
	imageStringBegin = substring.find("<img")
	imageStringEnd = imageStringBegin + substring[imageStringBegin:].find("/>")+2
	imageString = substring[imageStringBegin:imageStringEnd]
	comment = ""
	if ("!ALTMARKER!" in substring):
		commentBegin = substring.find("!ALTMARKER!")
		comment = substring[commentBegin+12:-4]
		comment = comment.replace("\t", " ")
		comment = comment.replace("\n", " ")
	newString = imageString.replace('alt="image"', 'alt="{}"'.format(comment))
	return newString

def longDescHandler(substring, buttonText):
	substring = substring.replace(buttonText, "")
	substring = substring.replace("LONGDESC ", "LONGDESC")
	substring = substring.replace("<p>;;;;LONGDESC</p>", "")
	substring = substring.replace("<p>;;;;</p>", "")
	substring = [i for i in substring.split("\n") if i != ""]
	substring[0] = '<div id="longdesc{}" style="display:none">'.format(descIndex)
	count = 0
	for j in substring:
		if "div" in j:
			count+=1
	if count%2 == 1:
		substring.append("</div>")
	substring = '\n'.join(substring)
	newString = tableToString(substring)
	button = '<button onclick=hideSeek('+"'longdesc{}'".format(descIndex)+') style="box-shadow:none">'
	button += "{}</button>\n".format(buttonText)
	newString = button + newString
	return newString

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="path to input file")
parser.add_argument("-o", "--output", help="path to output file")
parser.add_argument("-rt", "--resource-template", default="HTML/Files/ResourceTemplate.html",
										help="path to resource template")
parser.add_argument("-s", "--save-pandoc", default="testfile.html", 
										help="Saves the raw pandoc output file to given path")

args = parser.parse_args()

filein = args.input
fileout = args.output

rawpandoc = args.save_pandoc

restemp = args.resource_template

cmd = 'pandoc -f latex --mathjax -t html "{}" -s -o "{}" --metadata title="..."'.format(filein, rawpandoc)

os.system(cmd)

bodyCode = []
with open(rawpandoc, 'r') as f:
	bodyCode = f.read().split("\n")

if rawpandoc == "testfile.html":
	os.remove(rawpandoc)

pair = []

for i in range(len(bodyCode)):
	if "<body>" in bodyCode[i]:
		pair.append(i)
	if "</body>" in bodyCode[i]:
		pair.append(i)
bodyCode = "\n".join(bodyCode[pair[0]+1:pair[1]])

bodyCode = bodyCode.replace("{aligned}", "{align*}")
bodyCode = bodyCode.replace(".pdf", ".png")
bodyCode = bodyCode.replace('<img src="', '<img src="images/')

newBodyCode = bodyCode[:]

longDescMarkings = [m.start() for m in re.finditer(";;;;", bodyCode)]
descIndex = 0
for i in range(0, len(longDescMarkings), 2):
	start = longDescMarkings[i]-3
	end = longDescMarkings[i+1]
	substring = bodyCode[start:end+8]
	buttonText = bodyCode[start+16:]
	buttonText = buttonText[:buttonText.find("</p>")]
	newString = longDescHandler(substring, buttonText)
	newBodyCode = newBodyCode.replace(substring, newString)
	descIndex+=1

marked = [m.start() for m in re.finditer(",,,,", bodyCode)]
for i in range(0, len(marked), 2):
	start = marked[i]
	end = marked[i+1]
	substring = bodyCode[start:end+4]
	if ("!ALTMARKER!" in substring or "!NOALT!" in substring):
		newString = parseAltText(substring)	
		newBodyCode = newBodyCode.replace(substring, newString)
	if ("!ROWTABLE!" in substring):
		newString = parseRowTable(substring)
		newBodyCode = newBodyCode.replace(substring, newString)
	if ("!ROWCOLTABLE!" in substring):
		newString = parseRowColTable(substring)
		newBodyCode = newBodyCode.replace(substring, newString)
	
bodyCode = newBodyCode[:]

bodyCode = bodyCode.replace("<section", "<div")
bodyCode = bodyCode.replace("</section", "</div")
bodyCode = bodyCode.replace("unnumbered exsoln", "exsoln")

title = filein[filein.rfind('/')+1:filein.rfind(".")]

badTitle = bodyCode.find("<h1 class=")
badTitleEnd = badTitle + bodyCode[badTitle:].find("</h1>")+5
h1TagStart = badTitleEnd + bodyCode[badTitleEnd:].find("<h1")
titleStart = h1TagStart + bodyCode[h1TagStart:].find(">")+1
h1TagEnd = h1TagStart + bodyCode[h1TagStart:].find("</h1")
title = bodyCode[titleStart:h1TagEnd]
titleStripped = title.replace("\n", " ")
titleStripped = titleStripped.replace("<br />", "")

bodyCode = bodyCode[:h1TagStart] + bodyCode[h1TagEnd+5:]
h1TagStart = bodyCode.find("<h1")
h1TagEnd = bodyCode.find("</h1")
titleStart = h1TagStart + bodyCode[h1TagStart:].find(">")
bodyCode = bodyCode[:titleStart+1] + title + bodyCode[h1TagEnd:]

htmlFile = ""

with open(restemp, 'r') as f:
	htmlFile = f.read()


## remove <h1>Title</h1>
htmlFile = htmlFile.replace("<h1>Title</h1>", "")

titleStart = htmlFile.find("<title>")+7
titleEnd = htmlFile.find("</title>")
htmlFile = htmlFile[:titleStart] + titleStripped + htmlFile[titleEnd:]

htmlFile = htmlFile.replace("<p>Content</p>", bodyCode)

with open(fileout, 'w') as f:
	f.write(htmlFile)
