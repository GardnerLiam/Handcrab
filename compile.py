import os
import subprocess

def buildCommand(config):
	if config["output"] == "":
		config["output"] = config["input"][:config["input"].rfind(".")]+".html"

	add = ["--quiet"]
	if config["highest-heading-level"] != 0:
		add.append("--shift-heading-level-by="+str(config["highest-heading-level"]))
	if config["verbose"]:
		add.remove("--quiet")
	cmd = ["pandoc -f latex --mathjax"] + add
	cmd.append("-t html")
	cmd.append('"'+config["input"]+'"')
	cmd.append("-s -o")
	cmd.append('"'+config["output"]+'"')
	return ' '.join(cmd)

def run(config):
	command = buildCommand(config)
	return subprocess.getoutput(command)
