def read(filein):
	data = ""
	with open(filein, 'r') as f:
		data = f.read().split("\n")

	start = 0
	for i in range(len(data)):
		if "begin{document}" in data[i]:
			start = i
			break
	data = data[i:]
	return (data, start)

def parse(data, start):
	item_forced = set()
	uniitem_list = set()
	multicols = set()
	include_with_scale = set()
	wrapfigure = set()
	minipages = set()
	alph_items = set()
	nestedLists = set()
	urlUsage = set()
	tikz = set()
	fbox = set()

	for i in range(len(data)):
		if data[i].replace(" ", "").replace("\t", "").startswith("%"):
			continue
		if r"\item[" in data[i]:
			find_enumeration = data[:i]
			for j in range(len(find_enumeration)-1, -1, -1):
				if "begin{item" in data[j] or "begin{enum" in data[j]:
					item_forced.add(start+j)
					break
		if r"begin{enumerate" in data[i]:
			count = 0
			for j in range(i+1, len(data)):
				if "end{enumerate" in data[j]:
					break
				if r"\item" in data[j]:
					count+=1
			if count == 1:
				uniitem_list.add(start+i)
		if r"begin{itemize" in data[i]:
			count = 0
			for j in range(i+1, len(data)):
				if "end{itemize" in data[j]:
					break
				if r"\item" in data[j]:
					count+=1
			if count == 1:
				uniitem_list.add(start+i)

		if r"begin{enumerate}" in data[i] and "alph" in data[i]:
			alph_items.add(start+i)
		if r"begin{multicol" in data[i]:
			multicols.add(start+i)
		if r"includegraphics[scale" in data[i] or "includegraphics[height" in data[i]:
			include_with_scale.add(start+i)
		if r"begin{wrapfigure" in data[i]:
			wrapfigure.add(start+i)
		if r"begin{minipage" in data[i]:
			minipages.add(start+i)
		if r"begin{itemize" in data[i] or r"begin{enumerate" in data[i]:
			depth = 1
			for j in range(i+1, len(data)):
				if r"end{itemize" in data[j] or r"end{enumerate" in data[j]:
					depth -= 1
				if r"begin{itemize" in data[j] or "begin{enumerate" in data[j]:
					depth += 1
					if "begin{enumerate" in data[j] and "[" not in data[j]:
						nestedLists.add(start+j+1)
				if depth == 0:
					break
		if r"\url{" in data[i]:
			urlUsage.add(start+i)
		if r"\begin{tikz" in data[i]:
			tikz.add(start+i)
		if r"\fbox" in data[i]:
			fbox.add(start+i)
	data = {
		"URLs": sorted(urlUsage),
		"Scaled graphics": sorted(include_with_scale),
		"Forced Items": sorted(item_forced),
		"Lists with 1 item": sorted(uniitem_list),
		"Alph Items": sorted(alph_items),
		"nested lists": sorted(nestedLists),
		"fbox": sorted(fbox),
		"multicols": sorted(multicols),
		"wrapfigure": sorted(wrapfigure),
		"minipages": sorted(minipages),
		"tikz": sorted(tikz),
	}
	return data

def log(data):
	text = ""
	for i in data:
		if len(data[i]) > 0:
			text += "{} ({})\n".format(i, len(data[i]))
			text += "\t{}\n".format(str(data[i]))
	return text
