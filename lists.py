from pathlib import Path
import random
import rio


def read_players_file(file_path, alts=False):
	if not Path(file_path).exists():
		print(f"WARNING: file {file_path} doesn't exist!")
		return []

	players = []
	with open(file_path, encoding="utf8") as f:
		lines = f.readlines()
		for line in lines:
			player = {}
			line = line.strip('\n')
			if len(line) == 0:
				continue
			if line[0] == '#':
				continue
			if line[0] == '!':
				player['is_hidden'] = True
				line = line[1:]
			tmp = line.split('-')
			player['name'] = tmp[0]
			player['realm'] = tmp[1]
			player['is_alt'] = alts
			players.append(player)
	return players


def get_proxy():
	try:
		with open('lists/proxy.txt', encoding="utf8") as f:
			ips = f.readlines()
			index = random.randint(0,len(ips)-1)
			#test Proxy
			try:
				rio.pull(['https://checkip.perfect-privacy.com/json'], ips[index].strip())
			except:
				get_proxy()
			return ips[index].strip()
	except:
		return ''
