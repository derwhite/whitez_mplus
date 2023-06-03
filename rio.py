import re
import requests
import json
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from bnet import BnetBroker

def extract_player_ids(players, proxy='') -> None:
	run_id_pattern = re.compile('\/(\d+)')
	run_ids = [run_id_pattern.findall(p._data['mythic_plus_best_runs'][0]['url'])[0] for p in players if len(p._data['mythic_plus_best_runs']) > 0]
	season_slug = players[0]._data['mythic_plus_scores_by_season'][0]['season']
	pull_urls = [f'https://raider.io/api/v1/mythic-plus/run-details?season={season_slug}&id={run_id}' for run_id in run_ids]
	runs_response = pull(pull_urls, proxy)
	dict_player_ids = {}
	for p in players:
		for r in runs_response:
			player_found = False
			if r.ok and is_json(r.text):
				for char in r.json()['roster']:
					if char['character']['name'] == p.name:
						dict_player_ids[p.name] = char['character']['id']
						player_found = True
						break
			if player_found:
				break
	with open('player_ids.json', 'w') as f:
		json.dump(dict_player_ids, f)
	

def get_run_details(players, proxy=''):
	urls = []
	for p in players:
		urls.extend([p['url'] for p in p._data['mythic_plus_weekly_highest_level_runs'] if p['url'] not in urls])
		urls.extend([p['url'] for p in p._data['mythic_plus_previous_weekly_highest_level_runs'] if p['url'] not in urls])
	pattern = re.compile('\/(\d+)') # regex to extract the run id from the url
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


def append_api_requests(players_list):
	for player in players_list:
		realm = player['realm']
		name = player['name']
		fields = [
			'talents',
			'mythic_plus_best_runs',
			'mythic_plus_scores_by_season:current',
			'mythic_plus_alternate_runs',
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
		else:
			results = [s_get_with_timeout(urls[0])]
		checked_results = []
		try:
			for r in results:
				for x in range(3):
					if r.ok and is_json(r.text):
						checked_results.append(r)
						break
					else:
						r = s.get(r.url)
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
				instances.append({'short': ini['short_name'], 'name': ini['name'], 'timer': ini_time, 'upgrade_2': upgrade_2, 'upgrade_3': upgrade_3})
			season_name = sea['name']
			break
	return instances, season_name


def get_score_colors(proxy=''):
	tmp = pull(['https://raider.io/api/v1/mythic-plus/score-tiers?season=current'], proxy)
	try:
		r = tmp[0]
		if r.json()['statusCode'] == 200:
			return r.json()
	except:
		with open('color.json') as f:
			return json.load(f)


def sort_players_by(results, weekly):
	i = 0
	while i < len(results):
		x = i+1
		while x < len(results):
			sum = 0
			for r in results[x]._data[weekly]:
				if r['mythic_level'] >= 20:
					sum += 300
				sum += r['mythic_level']
			sum2 = 0
			for r in results[i]._data[weekly]:
				if r['mythic_level'] >= 20:
					sum2 += 300
				sum2 += r['mythic_level']
			if sum > sum2:
				#print(results[i].json()['name'],sum2,results[x].json()['name'],sum)
				tmp = results[i]
				results[i] = results[x]
				results[x] = tmp
			x += 1
		i += 1
	return results


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

def get_season_end(expasion_id, season_slug, proxy = '') -> datetime:
	tmp = pull([f'https://raider.io/api/v1/mythic-plus/static-data?expansion_id={expasion_id}'], proxy)
	for sea in tmp[0].json()['seasons']:
		if sea['slug'] == season_slug:
			if sea['ends']['eu'] != None:
				return datetime.strptime(sea['ends']['eu'], '%Y-%m-%dT%H:%M:%SZ')
			else:
				return None