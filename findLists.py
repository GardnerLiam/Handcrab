import re
import string

rreplace = lambda s,old,new,count: new.join(s.rsplit(old,count))

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

def matchString(text, pos, start, end):
	l1 = len(start)
	l2 = len(end)
	if text[pos:pos+l1] == start:
		pos+=l1+1
	count = 1
	for i in range(pos, len(text)-max(l1,l2)):
		if text[i:i+l1] == start:
			count+=1
		if text[i:i+l2] == end:
			count -= 1
		if count == 0:
			return i+l2
	if text[-l2:] == end and count == 1:
		return len(text)

def parseBrackets(bracket):
	enumType = re.search("([^a-zA-Z0-9\n]+)?([a-zA-Z0-9]+)([^a-zA-Z0-9\n]+)?", bracket)
	if enumType is not None:
		enumType = enumType.group(2)
	value = 0
	if enumType in string.ascii_lowercase:
		value = string.ascii_lowercase.find(enumType)+1
		enumType = "a"
	elif enumType in string.ascii_uppercase:
		value = string.ascii_uppercase.find(enumType)+1
		enumType = "A"
	elif enumType.isnumeric():
		value = enumType[:]
		enumType = "1"
	return (enumType, value)

def getSublists(text):
	'''
	given: \begin{...}(...)\end{...}
	extracts locations of nested enumeration 
	'''
	subLists = []
	for i in re.finditer(r"\\begin{(enumerate|itemize)}", text):
		s = i.start()
		enumType = i.group(1)
		matchStart = "\\begin{"+enumType+"}"
		matchEnd = "\\end{"+enumType+"}"
		e = matchString(text,s,matchStart,matchEnd)
		subLists.append((s,e))
	if subLists[0][0] == 0:
		subLists = subLists[1:]
	return subLists

def fixItemize(text):
	'''
	given \\begin{itemize}(...)\end{itemize}
	if \item[] is found, replace itemize with enumerate
	'''
	beginning = re.search(r"\\begin{itemize}\[(.*?)\]", text)
	if beginning is not None:
		if beginning.start() == 0:
			textCopy = text.replace("\\begin{itemize}", "\\begin{enumerate}", 1)
			textCopy = rreplace(textCopy, "\\end{itemize}", "\\end{enumerate}", 1)
			return textCopy

	subLists = getSublists(text)
	textCopy = text[:]
	for i in re.finditer(r"\\item\[(.*?)\]", text):
		if len(subLists) > 0:
			if True in [a[0] <= i.start() and i.start() <= a[1] for a in subLists]:
				continue
		enumType, value = parseBrackets(i.group(1))
		if enumType == 'a':
			enumType = string.ascii_lowercase[value]
		elif enumType == "A":
			enumType = string.ascii_uppercase[value]
		elif enumType == '1':
			enumType = str(value)
		textCopy = textCopy.replace("\\begin{itemize}", "\\begin{enumerate}", 1)
		textCopy = rreplace(textCopy, "\\end{itemize}", "\\end{enumerate}", 1)
	return textCopy

def modItems(text):
	'''
	given \begin{enumerate}(...)\end{enumerate}
	modifies \item[...]
	'''
	subLists = getSublists(text)
	textCopy = text[:]
	for i in re.finditer(r"\\item\[(.*?)\]", text):
		if len(subLists) > 0:
			if True in [a[0] <= i.start() and i.start() <= a[1] for a in subLists]:
				continue
		enumType, value = parseBrackets(i.group(1))
		textCopy = textCopy.replace(i.group(0), "\\item !VALUE! {} {}".format(enumType, value))
	return textCopy

def modStarts(text):
	'''
	given \begin{enumerate}(...)\end{enumerate}
	adds !STARTENUM!/!ENDENUM! around text if necessary
	'''

	beginning = re.search(r"\\begin{enumerate}\[(.*?)\]", text)
	if beginning is None:
		return text
	if beginning.start() != 0:
		return text
	enumType, value = parseBrackets(beginning.group(1))	
	textCopy = "\n!STARTENUM! {} {}\n".format(enumType, value)+text
	if textCopy[-1] == "\n":
		textCopy += "!ENDENUM!\n"
	else:
		textCopy += "\n!ENDENUM!\n"
	return textCopy

def parseListStarts(text):
	textCopy = text[:]
	for i in re.finditer(r"!STARTENUM!", text):
		s = i.start()
		e = matchString(text, s, "!STARTENUM!", "!ENDENUM!")
		body = text[s:e]
		enumType, value  = body.split("\n")[0].split(" ")[1:]
		value = value[:value.find("<")]
		
		olStart = body.find("<ol")
		if olStart == -1:
			print(body)
			body = body.replace("!STARTENUM! {} {}".format(enumType, value), "", 1)
			body = rreplace(body, "!ENDENUM!", "", 1)

			textCopy = textCopy.replace(text[s:e], body)
			continue

		olEnd = matchString(body[olStart:],	0, "<", ">")+olStart
		ol = body[olStart:olEnd]
		
		body = body.replace(ol, '<ol type="{}" start="{}">'.format(enumType, value), 1)
		body = body.replace("!STARTENUM! {} {}".format(enumType, value), "", 1)
		body = rreplace(body, "!ENDENUM!", "", 1)

		textCopy = textCopy.replace(text[s:e], body)
	return re.sub(r"<p>\s+<\/p>", "", textCopy)

def parseListValues(text):
	textCopy = text[:]
	for i in re.finditer(r"<li><p>!VALUE! (.*?) (.*?) (.*?)<\/p><\/li>", text, flags=re.DOTALL):
		enumType = i.group(1)
		value = i.group(2)
		body = i.group(0)
		body = body.replace("<li><p>!VALUE! {} {}".format(enumType, value),
												'<li value="{}" type="{}"><p>'.format(value, enumType))
		textCopy = textCopy.replace(i.group(0), body)
	return textCopy


def updateTeXLists(text):
	textCopy = text[:]
	for i in re.finditer(r"\\begin{itemize}", text):
		s = i.start()
		end = matchString(text, s, "\\begin{itemize}", "\\end{itemize}")
		textCopy = textCopy.replace(text[s:end], fixItemize(text[s:end]))
	text = textCopy[:]

	textCopy = text[:]
	for i in re.finditer(r"\\begin{enumerate}", text):
		s = i.start()
		end = matchString(text, s, "\\begin{enumerate}", "\\end{enumerate}")
		textCopy = textCopy.replace(text[s:end], modItems(text[s:end]))
	text = textCopy[:]
	textCopy = text[:]
	for i in re.finditer(r"\\begin{enumerate}", text):
		s = i.start()
		end = matchString(text, s, "\\begin{enumerate}", "\\end{enumerate}")
		textCopy = textCopy.replace(text[s:end], modStarts(text[s:end]))
	return textCopy

def updateHTMLLists(text):
	text = parseListValues(parseListStarts(text))
	rl = re.finditer(r"<p>!OPTIONS!</p>((.|\n)*?)<p>!OPTIONS!</p>", text)
	for i in rl:
		newText = i.group(1)
		newText = newText.replace('ol type="A" start="1"', 'ol class="mc"')
		newText = newText.replace("<li><p>", "<li>")
		newText = newText.replace("</p></li>", "</li>")
		text = text.replace(i.group(0), newText)	
	return text
