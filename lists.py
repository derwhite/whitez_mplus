from pathlib import Path
import random
import rio


def get_players(file_path):
	if not Path(file_path).exists():
		print(f"WARNING: file {file_path} doesn't exist!")
		return []
	with open(file_path, encoding="utf8") as f:
		return f.readlines()


def getProxy():
	try:
		with open('lists/proxy.txt', encoding="utf8") as f:
			ips = f.readlines()
			index = random.randint(0,len(ips)-1)
			#test Proxy
			try:
				rio.pull(['https://checkip.perfect-privacy.com/json'], ips[index].strip())
			except:
				getProxy()
			return ips[index].strip()
	except:
		return ''
