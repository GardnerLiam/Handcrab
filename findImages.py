from lxml import etree as ET

import os
import re

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()

def updateImages(text):
	rl = re.finditer("!IMAGE!((.|\n)*?)!IMAGE!", text)
	for i in rl:
		image = i.group(0)
		if "ALTMARKERS" in i.group(0):
			alt = i.group(0)
			alt = alt[alt.find("!ALTMARKERS!")+len("!ALTMARKERS! "):]
			image = image.replace('alt="image"', 'class="static" alt="{}"'.format(alt))
		elif "ALTMARKER" in i.group(0):
			alt = i.group(0)
			alt = alt[alt.find("!ALTMARKER!")+len("!ALTMARKER! "):]
			image = image.replace('alt="image"', 'alt="{}"'.format(alt))
		else:
			print(i.group(0))
		image = image[:image.find("!ALTMARKER")]
		image = image.replace("!IMAGE!", "")
		text = text.replace(i.group(0), image)
	return text
