import os
import re

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()

def updateImages(text, image_folder=""):
	rl = re.finditer("!IMAGE!((.|\n)*?)!IMAGE!", text)
	for i in rl:
		image = i.group(0)
		if "\\includegraphics" in image:
			info = re.search(r"\\includegraphics\[(.*?)\]{(.*?)}", image)
			size = info.group(1)
			path = info.group(2)
			percentSize = False
			if r"\textwidth" in size or r"\textheight" in size:
				percentSize = True
			size = size.replace(r"\textwidth", "%")
			size = size.replace("=", ":")
			numeral = 0 
			if "in" in size:
				numeral = float(size[size.find(":")+1:size.find("in")])
			else:
				numeral = float(size[size.find(":")+1:-1])
			newNumeral = numeral
			if percentSize:
				newNumeral*=100
			size = size.replace(str(numeral), str(newNumeral))
			image = image.replace(info.group(0), '<img src="{}" style="{}" />'.format(path, size))
		style = re.search(r'style="((.|\n)*?)"', image)
		if (style is not None):
			style = style.group(1)
			if not style.endswith("%"):
				if ("ALTMARKER!" in image):
					image = image.replace("ALTMARKER!", "ALTMARKERS!")
				elif ("NOALT" in image):
					image = image.replace("NOALT!", "NOALTS!")
		if "ALTMARKERS" in image:
			alt = i.group(0)
			alt = alt[alt.find("!ALTMARKERS!")+len("!ALTMARKERS! "):]
			if "</p>" in alt:
				alt = alt[:alt.find("</p>")]
			image = image.replace('alt="image"', 'class="static" alt="{}"'.format(alt))
		elif "ALTMARKER" in image:
			alt = i.group(0)
			alt = alt[alt.find("!ALTMARKER!")+len("!ALTMARKER! "):]
			if "</p>" in alt:
				alt = alt[:alt.find("</p>")]
			image = image.replace('alt="image"', 'alt="{}"'.format(alt))
		elif "NOALT" in image:
			image = image.replace('alt="image"', 'alt=""')
		elif "NOALTS" in image:
			image = image.replace('alt="image"', 'class="static" alt=""')
		else:
			print(i.group(0))
		if "!ALTMARKER" in image:
			image = image[:image.find("!ALTMARKER")]
		else:
			image = image[:image.find("!NOALT")]
		if len(image_folder) > 0 and "/Logos/" not in image:
			if 'src="'+image_folder not in image:
				image = image.replace('src="', 'src="{}/'.format(image_folder))
		image = image.replace("!IMAGE!", "")
		text = text.replace(i.group(0), image)
	return text
