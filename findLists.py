import re
import string

rreplace = lambda s,old,new,count: new.join(s.rsplit(old,count))

lowerAlpha = string.ascii_lowercase[:8]+string.ascii_lowercase[9:]
upperAlpha = string.ascii_uppercase[:8]+string.ascii_uppercase[8:]
lowerRoman = ["x", "i", "ii", "iii", "iv", "v"]
lowerRoman += [i[::-1] for i in lowerRoman if i[::-1] not in lowerRoman]
upperRoman = ["X", "I", "II", "III", "IV", "V"]
upperRoman += [i[::-1] for i in upperRoman if i[::-1] not in upperRoman]

def int_to_Roman(num):
	val = [1000,900,500,400,100,90,50,40,10,9,5,4,1]
	syb = ["M","CM","D","CD","C","XC","L","XL","X","IX","V","IV","I"]
	roman_num = ''
	i = 0
	while num>0:
		for _ in range(num//val[i]):
			roman_num += syb[i]
			num -= val[i]
		i+=1
	return roman_num

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

def bruteForceRoman(val):
	for i in range(1,1000):
		if int_to_Roman(i).casefold() == val.casefold():
			return i
	return 1

def parseBrackets(bracket):
	enumType = re.search("([^a-zA-Z0-9\n]+)?([a-zA-Z0-9]+)([^a-zA-Z0-9\n]+)?", bracket)
	if enumType is not None:
		enumType = enumType.group(2)
	value = 0
	if enumType in lowerAlpha:
		value = string.ascii_lowercase.find(enumType)+1
		enumType = "a"
	elif enumType in upperAlpha:
		value = string.ascii_uppercase.find(enumType)+1
		enumType = "A"
	elif enumType in lowerRoman:
		value = bruteForceRoman(enumType)
		enumType = "i"
	elif enumType in upperRoman:
		value = bruteForceRoman(enumType)
		enumType = "I"
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
		elif enumType == "i":
			enumType = int_to_Roman(value).lower()
		elif enumType == "I":
			enumType = int_to_Roman(value)
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
	for i in re.finditer(r"<li><p>!VALUE! (.*?) (.*?)( |\n|<)", text, flags=re.DOTALL):
		pos = i.start()
		end = matchString(text, pos, "<li>", "</li>")
		enumType = i.group(1)
		value = i.group(2)
		body = text[pos:end]
		newBody = body.replace("<li><p>!VALUE! {} {}".format(enumType, value),
												'<li value="{}" type="{}"><p>'.format(value, enumType), 1)
		textCopy = textCopy.replace(body, newBody)
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
	rl = re.finditer(r"<p>!OPTIONS!<\/p>((.|\n)*?)<p>!OPTIONS!</p>", text)
	for i in rl:
		newText = i.group(1)
		newText = newText.replace('ol type="A" start="1"', 'ol class="mc"')
		newText = newText.replace("<li><p>", "<li>")
		newText = newText.replace("</p></li>", "</li>")
		text = text.replace(i.group(0), newText)	
	for i in re.finditer(r"<p>!HORIZONTAL!<\/p>(.*?)<p>!HORIZONTAL!<\/p>", text, flags=re.DOTALL):
		newText = i.group(1)
		newText = re.sub("<ol(.*?)>", '<ol class="horizontal">', newText, 1)
		newText = newText.replace("<li><p>", "<li>")
		newText = newText.replace("</p></li>", "</li>")
		text = text.replace(i.group(0), newText)
	return text
