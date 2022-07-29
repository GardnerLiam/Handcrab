import re


def updateLongdesc(text):
	rl = re.finditer(r"<p>!LONGDESC!((.|\n)*?)!LONGDESC!<\/p>", text)
	c = 0
	for i in rl:
		name = "longdesc{}".format(c)
		s = i.group(0)
		buttonText = s[s.find("!LONGDESC! ")+len("!LONGDESC! "):]
		buttonText = buttonText[:buttonText.find("<")]
		contents = i.group(1)
		if buttonText+"</p>" in contents:
			r = buttonText+"</p>"
			contents = contents[contents.find(r)+len(r):]
		if contents.endswith("<p>"):
			contents = contents[:-3]
		longdesc = '<button onclick="hideSeek(\'{}\')" style="box-shadow: none;">{}</button>'.format(name, buttonText)
		longdesc += "\n"
		longdesc += '<div id="{}" style="display: none;">'.format(name)
		longdesc += "\n"+contents+"<hr /></div>"
		text = text.replace(s, longdesc)
		c+=1
	return text
