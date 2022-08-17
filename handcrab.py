import os
import sys
import copy
import argparse
from datetime import datetime

from onefile import writeOneFile, combineFiles
from specific import * 


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", nargs="+", help="Path to input file(s)")
parser.add_argument("-o", "--output", default="", help="path to output file(s)")
parser.add_argument("-s", "--skeleton", nargs="+", default="default", help="Path to skeleton")
parser.add_argument("-t", "--template", default="default", help="template for file type (if exists)")
parser.add_argument("-hl", "--heading-level", help="shift heading level")
parser.add_argument("-p", "--remove-phantom", help="Removes \phantom", action="store_true")
parser.add_argument("-m", "--keep-minipages", help="Does not remove minipages", action="store_true")
parser.add_argument("-if", "--image-folder", help="Provide location for images")
parser.add_argument("-css", "--css", help="Path for CSS file")
parser.add_argument("-n", "--title", default="", help="change the title tag in HTML")
parser.add_argument("-V", "--verbose", help="Verbose mode", action="store_true")
parser.add_argument("-v", "--version", help="Displays version number", action="store_true")
parser.add_argument("-dhf", "--disable-helper-functions", help="disable template-specific modifications", action='store_true')
parser.add_argument("--docs", help="Opens documentation in browser", action="store_true")
args = parser.parse_args()

config = {
	'input': args.input,
	'output': args.output,
	'template': args.template.lower(),
	'remove-phantom': args.remove_phantom,
	'dhf': args.disable_helper_functions,
	'title': args.title
}

if len(args.skeleton) > 2 and isinstance(args.skeleton, list):
	print("Error: Can only apply one TeX and one HTML skeleton")
	sys.exit(1)
if len(args.skeleton) == 2 and isinstance(args.skeleton, list):
	types = [0,0]
	for i in args.skeleton:
		if "tex" in i.lower():
			types[0] += 1
		else:
			types[1] += 1
	if not (types[0] == 1 and types[1] == 1	):
		print("Error: Can only apply one TeX and one HTML skeleton")
		sys.exit(1)
	for i in args.skeleton:
		if "tex" in i.lower():
			config["TeXSkeleton"] = i
		else:
			config["skeleton"] = i
else:
	if isinstance(args.skeleton, list):
		if "tex" in args.skeleton[0].lower():
			config['TeXSkeleton'] = args.skeleton[0]
			config["skeleton"] = "default"
		else:
			config["skeleton"] = args.skeleton[0]
	else:
		config['skeleton'] = args.skeleton

if (args.keep_minipages):
	config['keep-minipages'] = True
if (args.heading_level is not None):
	config['highest-heading-level'] = int(args.heading_level)
if (args.verbose):
	config["verbose"] = True
if (args.image_folder is not None):
	if args.image_folder[-1] == "/":
		config["image-folder"] = args.image_folder[:-1]
	else:
		config["image-folder"] = args.image_folder
if (args.css is not None):
	config["css"] = args.css

'''
Each template has two dictionaries,
one for parameters, and one for dealing parsing.
'''

params = {
	"default": [
						{
							"highest-heading-level": 0,
							"keep-minipages": False,
							"verbose": False,
						},
						{
							"files": [],
							"output": "",		
							"skeleton": "cccFull"
						}
					],
	"ccc": [
						{
							"highest-heading-level": 1,
							"keep-minipages": False,
							"skeleton": 'cccProblem',
							"verbose": False,
						},
						{
							"files": [],
							"tag": "<h2",
							"output": "",
							"skeleton": "cccFull"
						}
				],
	"potm": [
					{
						"keep-minipages": False,
						"highest-heading-level": 0,
						"skeleton": 'potm',
						"verbose": False
					}
				],
	"bcc": [
					{
						"highest-heading-level": 1,
						"keep-minipages": False,
						"TeXSkeleton": "bccTeX",
						"skeleton": 'bccFull',
						"image-folder": "images",
						"verbose": False,
					},
				],
	"mathcircles": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "images",
			"outbyname": True,
			"verbose": False
		}
	],
	"ctmc": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "../Diagrams/CTMC/",
			"verbose": False,
			"skeleton": "ctmc",
			"preprocessing": [fixCTMCRelayCommand, removeCTMCHeader, fixCTMCSolutions]
		}
	],
	"potw": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "",
			"verbose": False,
			"skeleton": "potw",
			"preprocessing": [fixPOTWInput],
			"postprocessing": [fixPOTWNoTheme, fixPOTWNoImage, fixPOTWTheme]
		}
	],
	"gauss": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "../Diagrams/",
			"verbose": False,
			"skeleton": "gaussContest",
			"TeXSkeleton": "gaussTeX",
			"merge-before": False,
			"preprocessing": [gaussPostdocPreambleKiller, gaussSectionFixer],
			"postskeletonprocessing": [gaussTitleFixer]
		}
	],
	"gausssoln": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "../Diagrams/",
			"verbose": False,
			"skeleton": "gaussContest",
			"TeXSkeleton": "gaussSolnTeX",
			"merge-before": False,
			"preprocessing": [gaussSolnFixer],
			"postskeletonprocessing": [gaussTitleFixer]
		}
	],
	"pcf": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "../Diagrams/",
			"verbose": False,
			"skeleton": "PCFContest",
			"TeXSkeleton": "gaussTeX",
			"merge-before": False,
			"preprocessing": [gaussPostdocPreambleKiller, gaussSectionFixer],
			"postskeletonprocessing": [gaussTitleFixer]
		}
	],
	"pcfsoln": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "../Diagrams/",
			"verbose": False,
			"skeleton": "pcfContest",
			"TeXSkeleton": "pcfSolnTeX",
			"merge-before": False,
			"preprocessing": [euclidSolnFixer],
			"postskeletonprocessing": [gaussTitleFixer]

		}
	],
	"euclid": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "../Diagrams/E/",
			"verbose": False,
			"skeleton": "euclidContest",
			"TeXSkeleton": "euclidTeX",
			"merge-before": False,
			"preprocessing": [frontCoverRemover, euclidItemization],
			"postskeletonprocessing": [gaussTitleFixer]
		}
	],
	"euclidsoln": [
		{
			"highest-heading-level": 0,
			"keep-minipages": False,
			"image-folder": "../Diagrams/E/",
			"verbose": False,
			"skeleton": "euclidContest",
			"TeXSkeleton": "euclidTeX",
			"merge-before": False,
			"preprocessing": [euclidSolnFixer],
			"postskeletonprocessing": [gaussTitleFixer]
		}
	],
}


ordered = [0,0]
if config["template"] == "mathcircles":
	for filename in config["input"]:
		if 'probset' in filename.lower().replace(" ", "") or 'problemset' in filename.lower().replace(" ", ""):
			ordered[0]+=1
		elif 'soln' in filename.lower().replace(" ", "") or "solution" in filename.lower().replace(" ", ""):
			ordered[1]+=1
if ordered[0] == 1 and ordered[1] == 1:
	ordered = True
else:
	ordered = False

outputFiles = []
count = 0
for filename in config["input"]:
	subConfig = copy.deepcopy(config)
	if "template" in subConfig:
		subConfig.pop("template")
	subConfig["input"] = filename
	subConfig["output"] = "" 
	if config["template"] != None:
		subParams = copy.deepcopy(params[config["template"]][0])
		subConfig = {**subParams, **subConfig}
		if "pcf" in config["template"]:
			subConfig["postskeletonprocessing"].append(pcfTitleSpecifier(filename))

		if (subConfig["dhf"]):
			if "preprocessing" in subConfig:
				subConfig["preprocessing"] = []
			if "postprocessing" in subConfig:
				subConfig["postprocessing"] = []
			if "postskeletonprocessing" in subConfig:
				subConfig["postskeletonprocessing"] = []
		if "skeleton" in subParams and subConfig["skeleton"] == "default" and subParams["skeleton"] != "default":
			subConfig["skeleton"] = subParams["skeleton"]
		
	if ("outbyname" in subConfig and subConfig["outbyname"] == True):
		if ordered:
			if "problemset" in filename.lower().replace(" ", ""):
				subConfig["skeleton"] = "mcProbset"
			elif "soln" in filename.lower().replace(" ", "") or "solution" in filename.lower().replace(" ", ""):
				subConfig["skeleton"] = "mcSoln"
			else:
				subConfig["skeleton"] = "mcLesson"
		else:
			if count == 0:
				subConfig["skeleton"] = "mcLesson"
			elif count == 1:
				subConfig["skeleton"] = "mcProbset"
			elif count == 2:
				subConfig["skeleton"] = "mcSoln"
	writeOneFile(subConfig)
	outputFiles.append(subConfig["output"])
	count+=1

if config["template"] == 'ccc' or (config["template"] == "default" and len(args.input) > 1):
	subConfig = copy.deepcopy(params[config["template"]][1])
	subConfig["files"] = outputFiles
	subConfig["output"] = config["output"]
	combineFiles(subConfig)
elif len(config["output"]) == 0:
	for i in range(len(outputFiles)):
		curOutname = outputFiles[i]
		curInname = config["input"][i]
		newOutname = curInname[:curInname.rfind(".")]+".html"
		os.rename(curOutname, newOutname)
else:
	if len(config["output"]) > 0:
		os.rename(outputFiles[0], config["output"])

today = datetime.today()
sdate = datetime(today.year, 10, 31)

if (sdate.month == today.month and sdate.day == today.day):
	with open("skeletons/CCOTemplate.html", 'r') as f:
		text = f.read()
	print(text)
