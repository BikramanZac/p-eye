import subprocess

def speak(string):
	subprocess.call('espeak -v+f3 \"'+ string +'\"', shell = True)