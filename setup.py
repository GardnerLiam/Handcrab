import os

handcrab_path = os.environ["HOME"]+"/Desktop/handcrab/dist/"
os.system('echo "export PATH=$PATH:{}" >> ~/.bashrc'.format(handcrab_path))
os.system('echo "export PATH=$PATH:{}" >> ~/.zshrc'.format(handcrab_path))
