import re
import os
import sys

import ssl
import urllib.request

import argparse

import xml.etree.ElementTree as ET

try:
	ssl._create_default_https_context = ssl._create_unverified_context
except:
	pass

def get_online_version():
	with urllib.request.urlopen("https://raw.githubusercontent.com/GardnerLiam/Handcrab/master/README.md") as f:
		text = f.read().decode("utf-8").split("\n")
		return text[3]
	return ""

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
	substring = substring[:-1] + ["<hr />"] + substring[-1:]
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
parser.add_argument("--version", help="Displays version number", action="store_true")
parser.add_argument("--update", help="Downloads latest version", action="store_true")
parser.add_argument("--docs", help="Opens documentation in browser", action="store_true")
args = parser.parse_args()


current_version = ""
with open(os.environ["HOME"] + "/Desktop/handcrab/README.md", 'r') as f:
	lines = f.read().split("\n")
	current_version = lines[3].strip()
onlineVersion = current_version[:]
try:
	online_version = get_online_version().strip()
except:
	pass

if current_version != online_version:
	print("An update is available! Run 'handcrab --update' to get the new update")

if args.docs:
	import webbrowser
	url = 'file:///'+os.environ["HOME"]+'/Desktop/handcrab/HandcrabDocs/Docs/Handcrab docs.html'
	webbrowser.open(url)
	sys.exit(0)
if args.version:
	print("Handcrab version {}".format(current_version))
	sys.exit(0)

if args.update:
	os.system("python3 {}".format(os.environ["HOME"]+"/Desktop/handcrab/update.py"))
	sys.exit(0)

handcrab_path = os.environ["HOME"] + "/Desktop/handcrab/"

filein = args.input
fileout = args.output

rawpandoc = args.save_pandoc

restemp = args.resource_template
if restemp.lower() == "lesson":
	restemp = handcrab_path+"Templates/Lesson.html"
elif "problem" in restemp.lower():
	restemp = handcrab_path+"Templates/ProblemSet.html"
elif "solution" in restemp.lower():
	restemp = handcrab_path+"Templates/Solutions.html"
else:
	restemp = handcrab_path+"Templates/Default.html"

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

imageMarkings = [m.start() for m in re.finditer("<img", bodyCode)]
imageEndings = [i + bodyCode[i:].find(">")+1 for i in imageMarkings]
newBodyCode = bodyCode[:]

for i in range(len(imageMarkings)):
	image = bodyCode[imageMarkings[i]:imageEndings[i]]
	nimage = image.replace('<img src="', '<img src="images/')
	nimage = nimage.replace(".pdf", ".png")
	newBodyCode = newBodyCode.replace(image, nimage)

bodyCode = newBodyCode[:]

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
	if ("!UNDERLINE!" in substring):
		location = substring.find("!UNDERLINE!") + len("!UNDERLINE!")
		newString = ""
		if substring[location:] == ",,,," or substring[location:] == " ,,,,":
			newString = r'<span style="border-bottom: 1px solid black; padding-left: 50px">&nbsp;</span>'
		else:
			length = substring[location+1:-4]
			newString = '<span style="border-bottom: 1px solid black; padding-left: {}px">&nbsp;</span>'
			newString = newString.format(length)
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
titleSectioned = titleStripped.replace("<br /> ", "\n").split("\n")
if len(titleSectioned) != 3 or "math circles" not in titleSectioned[0].lower():
	print("Your title formatting is probably wrong :(")
	print("Gonna kill handcrab before something yells loudly")
	sys.exit(1)
	
title = "<br /> ".join(titleSectioned)

level = titleSectioned[0]
lesson = titleSectioned[2]

levelLower = level.lower()
level = level[:levelLower.find("math circ")]
while level[-1] == " ":
	level = level[:-1]

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
htmlFile = htmlFile[:titleStart] + level + " " + lesson + htmlFile[titleEnd:]

htmlFile = htmlFile.replace("<p>Content</p>", bodyCode)

with open(fileout, 'w') as f:
	f.write(htmlFile)
