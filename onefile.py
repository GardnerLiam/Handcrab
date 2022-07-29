from preprocessing import process
from findLists import updateLists
from findImages import updateImages
from findTables import updateTables
from findLongdesc import updateLongdesc
from skeleton import applySkeleton
from compile import run

import copy
import os

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()

def attemptDelete(filename):
	try:
		os.remove(filename)
	except:
		print("Could not delete {}".format(filename))

def combineFiles(config):
	fileText = []
	for fname in config["files"]:
		text = loadText(fname)
		start = text.find("<body")+6
		if "tag" in config and config["tag"] in text:
			start = text.find(config["tag"])
		end = text.find("</body")
		fileText.append(text[start:end])
	text = "<body>\n"+"\n".join(fileText)+"</body>"
	return applySkeleton(text, config["skeleton"], write=config["output"])
	
def writeOneFile(config):
	preprocessConfig = {
		"input": None,
		"TeXSkeleton": None,
		"keep-minipages": None
	}

	for value in config:
		if value in preprocessConfig:
			preprocessConfig[value] = config[value]
	
	config2 = copy.deepcopy(config)
	configName = process(preprocessConfig)
	config2["input"] = configName

	output = run(config2)
	if len(output) > 0:
		print(output)
	text = loadText(config2["output"])
	
	# the below should really be combined in one file
	text = updateLists(text)
	text = updateTables(text)
	text = updateImages(text)
	text = updateLongdesc(text)
	text = text.replace("{aligned}", "{align*}")

	if config["output"] == "":
		config["output"] = config["input"][:config["input"].rfind(".")]+".html"
	#print(configName)
	attemptDelete(configName)
	attemptDelete(configName[:-4]+".html")
	applySkeleton(text, config["skeleton"], write=config["output"])