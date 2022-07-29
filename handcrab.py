import os
import sys
import copy
import argparse

from onefile import writeOneFile, combineFiles

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", nargs="+", help="Path to input file(s)")
parser.add_argument("-o", "--output", help="path to output file(s)")
parser.add_argument("-s", "--skeleton", help="Path to skeleton")
parser.add_argument("-t", "--template", default="default", help="template for file type (if exists)")
parser.add_argument("-hl", "--heading-level", help="shift heading level")
parser.add_argument("-m", "--keep-minipages", help="Does not remove minipages", action="store_true")
parser.add_argument("-V", "--verbose", help="Verbose mode", action="store_true")
parser.add_argument("-v", "--version", help="Displays version number", action="store_true")
parser.add_argument("--docs", help="Opens documentation in browser", action="store_true")
args = parser.parse_args()

config = {
	'input': args.input,
	'output': args.output,
	'template': args.template
}

if (args.keep_minipages):
	config['keep-minipages'] = True
if (args.skeleton is not None):
	config['skeleton'] = args.skeleton
if (args.heading_level is not None):
	config['highest-heading-level'] = int(args.heading_level)
if (args.verbose):
	config["verbose"] = True



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
	"bcc": [
					{
						"highest-heading-level": 1,
						"keep-minipages": False,
						"TeXSkeleton": "bccTeX",
						"skeleton": 'bccFull',
						"verbose": False,
					},
				],
	
}


outputFiles = []
for filename in config["input"]:
	subConfig = copy.deepcopy(config)
	if "template" in subConfig:
		subConfig.pop("template")
	subConfig["input"] = filename
	subConfig["output"] = "" 
	if config["template"] != None:
		subParams = copy.deepcopy(params[config["template"]][0])
		subConfig = {**subParams, **subConfig}
	writeOneFile(subConfig)
	outputFiles.append(subConfig["output"])

if config["template"] == 'ccc' or (config["template"] == "default" and len(args.input) > 1):
	subConfig = copy.deepcopy(params[config["template"]][1])
	subConfig["files"] = outputFiles
	subConfig["output"] = config["output"]
	combineFiles(subConfig)
else:
	os.rename(outputFiles[0], config["output"])
