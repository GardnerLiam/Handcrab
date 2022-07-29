import string
import re

TYPES = []

def makeType(pre, an, post, index):
	listType = ["lower-alpha", "upper-alpha", "decimal"][an]

	css = "ol.NAME { counter-reset: list list-item; }\n\n"
	css += "ol.NAME li { list-style: none; padding: 7px 0px;}\n\n"
	css += "ol.NAME li:before { \n"
	css += '\tcontent: " {}" counter(list, {}) "{} ";\n'.format(pre, listType, post)
	css += '\tcounter-increment: list;\n}'
	return css.replace("NAME", "CLT{}".format(index))

def makeCSS():
	text = '<style type="text/css">\n'
	for i in range(len(TYPES)):
		pre, an, post = TYPES[i]
		l = makeType(pre, an, post, i)+"\n"
		text += l
	text += "</style>"
	return text

def surroundQuestion(text):
	areas = re.finditer(r"\\bccBox{Question}{((.|\n)*?)\\bccBox", text)
	for e1 in areas:
		area = e1.group(1)
		en = re.search(r"\\begin{enumerate}\[\(.\)\]((.|\n)*?)\\end{enumerate}", area)
		if en is None:
			continue
		en = en.group(0)
		newText = "!OPTIONS!\n"+en
		if newText[-1] != "\n":
			newText += "\n"
		newText += "!OPTIONS!\n"
		text = text.replace(en, newText)
	return text

def updateEnumerate(text):
	rl = re.finditer(r"\\begin{enumerate}\[((.*?)([a-zA-Z0-9]+)(.*?))\]((.|\n)*?)\\end{enumerate}", 
									text)
	for i in rl:
		body = i.group(0)
		preSpecify = i.group(2)
		postSpecify = i.group(4)
		alphaNumeric = i.group(3)

		if alphaNumeric.lower() != "a" or alphaNumeric.lower() != "1":
			index = 1
			header = ""
			if alphaNumeric.isnumeric() and int(alphaNumeric) > 1:
				index = int(alphaNumeric)
				header = "\n!VALUE! {}\n".format(alphaNumeric)
			else:
				if alphaNumeric in string.ascii_lowercase:
					index = string.ascii_lowercase.find(alphaNumeric)+1
				elif alphaNumeric in string.ascii_uppercase:
					index = string.ascii_uppercase.find(alphaNumeric)+1
				if (index != 1):
					header = "\n!VALUE! {}\n".format(index)
			if index != 1:
				if body[-1] == "\n":
					text = text.replace(body, header+body+"!VALUE!\n")
				else:
					text = text.replace(body, header+body+"\n!VALUE!\n")
	return text

def updateOrderedList(text):
	rl = re.finditer(r"<p>!VALUE! (.*?)<\/p>((.|\n)*?)<p>!VALUE!<\/p>", text)
	for i in rl:
		whole = i.group(0)
		ind = i.group(1)
		body = i.group(2)
		newBody = body.replace("<li", '<li value="{}"'.format(ind), 1)
		text = text.replace(whole, newBody)
	rl = re.finditer(r"<p>!CSSTYPE! (.*?)<\/p>((.|\n)*?)<p>!CSSTYPE!<\/p>", text)
	for i in rl:
		whole = i.group(0)
		ind = i.group(1)
		body = i.group(2)
		newBody = re.sub("<ol type=(.*?)>", "<ol>", body)
		newBody = newBody.replace("<ol>", '<ol class="CLT{}">'.format(ind))
		newBody = re.sub(r"<li(.*?)><p>((.|\n)*?)<\/p><\/li>", r"<li\1>\2</li>", newBody, re.MULTILINE)
		text = text.replace(whole, newBody)
	rl = re.finditer(r"<p>!OPTIONS!</p>((.|\n)*?)<p>!OPTIONS!</p>", text)
	for i in rl:
		newText = i.group(1)
		newText = newText.replace('ol type="A"', 'ol class="mc"')
		newText = newText.replace("<li><p>", "<li>")
		newText = newText.replace("</p></li>", "</li>")
		text = text.replace(i.group(0), newText)
	return text

def updateCSS(text):
	if len(TYPES) == 0:
		return text
	css = makeCSS()+"\n</head>"
	return text.replace("</head>", css)

def updateLists(text):
	return updateOrderedList(text)

def updateTeX(text):
	return updateEnumerate(text)

