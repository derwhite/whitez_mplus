import re
import requests
import json
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from bnet import BnetBroker
from dateutil.parser import parse


def extract_player_ids(players, proxy='') -> None:
	run_id_pattern = re.compile(r'\/(\d+)')
	run_ids = [run_id_pattern.findall(p._data['mythic_plus_best_runs'][0]['url'])[0] for p in players if len(p._data['mythic_plus_best_runs']) > 0]
	season_slug = players[0]._data['mythic_plus_scores_by_season'][0]['season']
	pull_urls = [f'https://raider.io/api/v1/mythic-plus/run-details?season={season_slug}&id={run_id}' for run_id in run_ids]
	runs_response = pull(pull_urls, proxy)
	list_player_ids = []
	dict_player_ids = {}
	for p in players:
		for r in runs_response:
			player_found = False
			if r.ok and is_json(r.text):
				for char in r.json()['roster']:
					if char['character']['name'] == p.name and char['character']['realm']['name'] == p.realm:
						player_dict = dict()
						player_dict['name'] = p.name
						player_dict['realm'] = p.realm
						player_dict['id'] = char['character']['id']
						list_player_ids.append(player_dict)
						if p.name.startswith("Käse"):
							dict_player_ids[f'{p.name}-{p.realm}'] = char['character']['id']
						else:
							dict_player_ids[p.name] = char['character']['id']
						player_found = True
						break
			if player_found:
				break
	with open('player_ids.json', 'w') as f:
		json.dump(dict_player_ids, f)
	with open('player_ids_with_realm.json', 'w') as f:
		json.dump(list_player_ids, f)


def get_run_details(players, proxy=''):
	urls = []
	for p in players:
		urls.extend([p['url'] for p in p._data['mythic_plus_weekly_highest_level_runs'] if p['url'] not in urls])
		urls.extend([p['url'] for p in p._data['mythic_plus_previous_weekly_highest_level_runs'] if p['url'] not in urls])
	pattern = re.compile(r'\/(\d+)') # regex to extract the run id from the url
	run_ids = [pattern.findall(url)[0] for url in urls]
	season_slug = players[0]._data['mythic_plus_scores_by_season'][0]['season']
	pull_urls = [f'https://raider.io/api/v1/mythic-plus/run-details?season={season_slug}&id={run_id}' for run_id in run_ids]
	runs_response = pull(pull_urls, proxy)
	dict_runs = {}
	for url, r in zip(urls, runs_response):
		if r.ok and is_json(r.text):
			# add tank first
			get_spieler = [f"[{int(spieler['items']['item_level_equipped'])}] {spieler['character']['name']}" for spieler in r.json()['roster'] if spieler['character']['spec']['role'] == 'tank']
			# add healer 2nd
			get_spieler.extend([f"[{int(spieler['items']['item_level_equipped'])}] {spieler['character']['name']}" for spieler in r.json()['roster'] if spieler['character']['spec']['role'] == 'healer'])
			# add dps last
			get_spieler.extend([f"[{int(spieler['items']['item_level_equipped'])}] {spieler['character']['name']}" for spieler in r.json()['roster'] if spieler['character']['spec']['role'] == 'dps'])
			dict_runs[url] = "\n" + "\n".join(get_spieler)
		else:
			dict_runs[url] = "\nERROR:\ndidn't found the run details"
	return dict_runs

def is_json(myjson):
	try:
		json.loads(myjson)
	except ValueError as e:
		return False
	return True


def append_api_requests(players_list, season):
	for player in players_list:
		realm = player['realm']
		name = player['name']
		fields = [
			'talents',
			'mythic_plus_best_runs',
			f'mythic_plus_scores_by_season:{season}',
			'mythic_plus_recent_runs',
			'gear',
			'mythic_plus_weekly_highest_level_runs',
			'mythic_plus_previous_weekly_highest_level_runs'
			]
		fields2 = ','.join(fields)
		url = f'https://raider.io/api/v1/characters/profile?region=eu&realm={realm}&name={name}&fields={fields2}'
		player['url'] = url


def pull(urls, proxy=''):    #sometimes gets stuck if Proxy does not response -.-
	with requests.Session() as s:
		s.headers.update({'Cache-Control': 'none','Pragma':'ino-cache'})
		if proxy != '':
			with open('proxykey') as f:
				key = f.readlines()
				proxies = {
				'http': f'http://{key[0].strip()}@{proxy}:8080',
				'https': f'http://{key[0].strip()}@{proxy}:8080'
				}
				s.proxies.update(proxies)
		connection_timeout = 90
		read_timeout = 90
		s_get_with_timeout = partial(s.get, timeout=(connection_timeout,read_timeout))
		if len(urls) > 1:
			with ThreadPoolExecutor(max_workers=20) as pool:
				results = pool.map(s_get_with_timeout, urls, chunksize=1)  # DL all URLS !!
		elif len(urls) == 1:
			results = [s_get_with_timeout(urls[0])]
		else:
			return []

		checked_results = []
		try:     #this goes maybe stuck
			for r in results:
				for x in range(3):
					if r.ok and is_json(r.text):
						checked_results.append(r)
						break
					else:
						r = s.get(r.url, timeout=connection_timeout)
					if x == 2:
						checked_results.append(r)
		except requests.exceptions.ReadTimeout as e:
			print(e)
			quit(1)

	return checked_results


def get_instances(expansion_id, season, proxy=''):
	tmp = pull([f'https://raider.io/api/v1/mythic-plus/static-data?expansion_id={expansion_id}'], proxy)
	instances = []
	season_name = ""
	bnet_broker = BnetBroker()
	for sea in tmp[0].json()['seasons']:
		if sea['slug'] == season:
			for ini in sea['dungeons']:
				ini_time = 0
				upgrade_2 = 0
				upgrade_3 = 0
				try:
					if bnet_broker.is_operational():
						url = f'/data/wow/mythic-keystone/dungeon/{ini["challenge_mode_id"]}'
						ini_timer = bnet_broker.pull(url, 'dynamic-eu')
						ini_time = ini_timer['keystone_upgrades'][0]['qualifying_duration'] / 1000
						upgrade_2 = ini_timer['keystone_upgrades'][1]['qualifying_duration'] / 1000
						upgrade_3 = ini_timer['keystone_upgrades'][2]['qualifying_duration'] / 1000
				except Exception as e:
					print(f"ERROR: {e}")
				instances.append({'short': ini['short_name'],
								'name': ini['name'],
								'timer': ini_time,
								'upgrade_2': upgrade_2,
								'upgrade_3': upgrade_3,
								'img_url': ini['background_image_url']})
			season_name = sea['name']
			break
	instances = sorted(instances, key=lambda i: i['short'])
	return instances, season_name


def get_score_colors(proxy=''):
	response_list = pull(['https://raider.io/api/v1/mythic-plus/score-tiers?season=current'], proxy)
	if len(response_list) > 0:
		r = response_list[0]
		if r.status_code == 200:
			return r.json()
	with open('color.json') as f:
		return json.load(f)


def sort_players_by(players, weekly):
	# sorts players by their weekly (current or last) m+ runs
	# sorts the players based on their highest key level. If key levels are the same, sort them based on their
	# second highest key level, etc.

	def kl(player):
		runs = player.weekly_runs(weekly)
		fixed_key_level_list = []
		for i in range(0, 10):
			if i < len(runs):
				fixed_key_level_list.append(runs[i]['mythic_level'])
			else:
				fixed_key_level_list.append(-1)
		return fixed_key_level_list

	players = sorted(players, key=lambda p: (kl(p)[0], kl(p)[1], kl(p)[2], kl(p)[3], kl(p)[4], kl(p)[5], kl(p)[6], kl(p)[7], kl(p)[8], kl(p)[9]), reverse=True)
	return players


def get_color(score_tier, points, max=0, dungeons_count=0):
	color = "white"
	if max > 0:
		points = points / (dungeons_count*2)
		points = points**4/max**4 * (score_tier[0]['score']*1)
	if points == 0:
		return color
	for x in score_tier:
		if x['score'] < points:
			color=x['rgbHex']
			break
	return color


def get_highest_score(players):
	high = 0
	for player in players:
		for ini in player.mythic_plus_best_runs():
			if high < ini['score']:
				high = ini['score']
	return high


def get_current_season(expasion_id,proxy=''):
    down = pull([f'https://raider.io/api/v1/mythic-plus/static-data?expansion_id={expasion_id}'], proxy)[0]
    now = datetime.now(timezone.utc)
    if down.ok:
        for sea in down.json()['seasons']:
            #if re.fullmatch(r'season-\w+?-\d', sea['slug']):
            if "ptr" in sea['slug']:
                continue
            if "beta" in sea['slug']:
                continue
            start = sea['starts']['eu']
            end = sea['ends']['eu']
            if start is None:
                continue
            if now > parse(start):
                if end is None:
                    return sea["slug"], None
                else:
                    if now < parse(end):
                        return sea["slug"], parse(end).astimezone()
    return None, None