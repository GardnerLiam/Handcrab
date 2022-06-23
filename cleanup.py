import os
import sys
a = [i for i in os.listdir('.') if os.path.isfile(i)]

allowed_extensions = [".jpg", ".png", ".tex", ".pdf"]
remove = [".log", ".aux", ".gz", ".out", ".synctex", ".toc", ".nav", ".snm", ".ai"]
image_extensions = [".jpg", ".png", ".pdf"]

if not os.path.exists("images/"):
	os.makedirs("images/")

for i in a:
	extension = i[i.rfind("."):]
	name = i[:i.rfind(".")]
	if extension in remove:
		os.remove(i)
	elif extension not in allowed_extensions:
		print(i)
	if extension == "pdf" and name+".tex" in a:
		os.remove(i)

a = [i for i in os.listdir(".") if os.path.isfile(i)]
for i in a:
	extension = i[i.rfind("."):]
	name = i[:i.rfind(".")]
	if extension not in allowed_extensions:
		print("Unknown file {}".format(i))
	elif extension in image_extensions:
		os.rename(i, "images/"+sys.argv[1]+i)
