import urllib.request
import os
import ssl
import shutil

try:
	ssl._create_default_https_context = ssl._create_unverified_context
except:
	pass

handcrab_path = os.environ['HOME'] + "/Desktop/handcrab/"

download = "https://github.com/GardnerLiam/Handcrab/archive/refs/heads/master.zip"
stop = False

try:
	urllib.request.urlretrieve(download, handcrab_path + "updates.zip")
	os.system("unzip " + handcrab_path+"updates.zip")
except:
	stop = True

if not stop:
	files = [handcrab_path + f for f in os.listdir(handcrab_path) if os.path.isfile(handcrab_path + f)]
	try:
		shutil.rmtree(handcrab_path + "build/")
	except:
		pass
	try:
		shutil.rmtree(handcrab_path + "dist/")
	except:
		pass
	try:
		shutil.rmtree(handcrab_path + "Templates/")
	except:
		pass
	try:
		shutil.rmtree(handcrab_path + "HandcrabDocs/")
	except:
		pass

	for i in files:
		try:
			os.remove(i)
		except:
			pass

	master_folder = handcrab_path + "Handcrab-master/"
	
	files = [os.path.join(master_folder, i) for i in os.listdir(master_folder)]
	newFiles = [os.path.join(handcrab_path, i) for i in os.listdir(master_folder)]
	
	for i in range(len(files)):
		shutil.move(files[i], newFiles[i])
	shutil.rmtree(master_folder)
