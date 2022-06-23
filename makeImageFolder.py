import os
import sys
extensions = ['.png', '.jpg', '.gif', '.pdf']

imageFiles = [i for i in os.listdir('.') if i[-4:] in extensions]

os.mkdir("images")
for i in imageFiles:
	os.rename(i, "images/"+sys.argv[1]+i)

