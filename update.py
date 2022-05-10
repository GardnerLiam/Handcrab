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
	files = [handcrab_path + f for f in os.listdir(handcrab_path) if f != "update.py"]
	files = [f for f in files if os.path.isfile(f)]
	shutil.rmtree(handcrab_path + "build/")
	shutil.rmtree(handcrab_path + "dist/")

	for i in files:
		os.remove(i)

	master_folder = handcrab_path + "Handcrab-master/"
	
	files = [os.path.join(master_folder, i) for i in os.listdir(master_folder)]
	newFiles = [os.path.join(handcrab_path, i) for i in os.listdir(master_folder)]
	
	for i in range(len(files)):
		shutil.move(files[i], newFiles[i])
	shutil.rmtree(master_folder)
