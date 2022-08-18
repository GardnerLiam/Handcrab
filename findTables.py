import xml.etree.ElementTree as ET

import sys

import re
import os

def tableToString(tableData, filename="output.xml"):
  tableData = tableData.replace("><", ">!!!IGNOREME!!!<")
  tree = ET.ElementTree(ET.fromstring(tableData))
  tree.write(filename)
  text = ""
  with open(filename, 'r') as f:
    text = f.read()
  text = text.replace(">!!!IGNOREME!!!<", "><")
  os.remove("output.xml")
  return text

def parseRowTable(substring):
  tableData = substring[substring.find("<table"):substring.find("</table")+8]
  tableData = tableData.replace("<tbody>", "")
  tableData = tableData.replace("</tbody>", "")
  tableData = tableToString(tableData)
  tableData = tableData.split("\n")
  tableData = list(filter(lambda a: a != "", tableData))
  rowTagInstances = [j for j in range(len(tableData)) if "<tr" in tableData[j]]
  for j in rowTagInstances:
    tableData[j+1] = tableData[j+1].replace("<td", '<th scope="row"')
    tableData[j+1] = tableData[j+1].replace("</td", "</th")
  tableData = "\n".join(tableData)
  return tableData

def parseRowColTable(substring):
  tableData = substring[substring.find("<table"):substring.find("</table")+8]
  tableData = tableData.replace("<tbody>", "")
  tableData = tableData.replace("</tbody>", "")
  tableData = tableToString(tableData)
  tableData = tableData.split("\n")
  tableData = list(filter(lambda a: a != "", tableData))
  rowTagInstances = [j for j in range(len(tableData)) if "<tr" in tableData[j]]
  for j in range(rowTagInstances[0]+2, rowTagInstances[1]):
    tableData[j] = tableData[j].replace("<td", '<th scope="col"')
    tableData[j] = tableData[j].replace("</td", "</th")
  rowTagInstances = rowTagInstances[1:]
  for j in rowTagInstances:
    tableData[j+1] = tableData[j+1].replace("<td", '<th scope="row"')
    tableData[j+1] = tableData[j+1].replace("</td", '</th')
  tableData = '\n'.join(tableData)
  return tableData

def loadText(fname):
	with open(fname, 'r') as f:
		return f.read()

searchTypes = {
	"row": ["<p>!ROWTABLE!<\/p>((.|\n)*?)<p>!ROWTABLE!<\/p>", "<p>!ROWTABLE!</p>"],
	"rowcol": ["<p>!ROWCOLTABLE!<\/p>((.|\n)*?)<p>!ROWCOLTABLE!<\/p>", "<p>!ROWCOLTABLE!</p>"]
}

def updateLaTeXTables(text):
	rl = re.finditer(r"!ROWTABLE!((.|\n)*?)!ROWTABLE!", text)
	for i in rl:
		table = i.group(1)
		newTable = table.replace("\hline", "")
		group = i.group(0)
		newGroup = group.replace(table, newTable)
		text = text.replace(group, newGroup)
	for i in re.finditer(r"!ROWCOLTABLE!((.|\n)*?)!ROWCOLTABLE!", text):
		table = i.group(1)
		newTable = table.replace("\hline", "")
		group = i.group(0)
		newGroup = group.replace(table, newTable)
		text = text.replace(group, newGroup)
	return text


def updateTables(text, tableTypes=searchTypes): 
	for t in tableTypes:
		rl = re.findall(tableTypes[t][0], text)
		for i in rl:
			table = i[0]
			newTable = None
			if t == "row":
				newTable = parseRowTable(table)
			elif t == "rowcol":
				newTable = parseRowColTable(table)
			if newTable == None:
				print("ERROR PARSING TABLE")
				sys.exit(0)
			text = text.replace(table, newTable)
		text = text.replace(tableTypes[t][1], "")
	return text
