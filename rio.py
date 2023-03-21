from multiprocessing.dummy import Pool as ThreadPool
import re
import requests
import json

from bnet import BnetBroker

def get_run_details(players, proxy=''):
	urls = []
	for p in players:
		[urls.append(p['url']) for p in p._data['mythic_plus_weekly_highest_level_runs'] if p['url'] not in urls]
		[urls.append(p['url']) for p in p._data['mythic_plus_previous_weekly_highest_level_runs'] if p['url'] not in urls]
	pattern = re.compile('\/(\d+)') # regex to extract the run id from the url
	run_ids = []
	[run_ids.append(pattern.findall(url)[0]) for url in urls]
	pull_urls = [f'https://raider.io/api/v1/mythic-plus/run-details?season=season-df-1&id={run_id}' for run_id in run_ids]
	runs_response = pull(pull_urls, proxy)
	dict_runs = {}
	for url, r in zip(urls, runs_response):
		get_spieler = []
		for spieler in r.json()['roster']:
			get_spieler.append(spieler['character']['name'])
		dict_runs[url] = "\n".join(get_spieler)
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
	s = requests.Session()
	s.headers.update({'Cache-Control': 'none','Pragma':'ino-cache'})
	pool = ThreadPool(4)
	if proxy != '':
		with open('proxykey') as f:
			key = f.readlines()
			proxies = {
			'http': f'http://{key[0].strip()}@{proxy}:8080',
			'https': f'http://{key[0].strip()}@{proxy}:8080'
			}
			s.proxies.update(proxies)
	results = pool.map(s.get, urls, chunksize=1)  # DL all URLS !!
	pool.close()
	pool.join()
	checked_results = []
	for r in results:
		for x in range(3):
			if r.ok and is_json(r.text):
				checked_results.append(r)
				break
			else:
				r = s.get(r.url)
			if x == 2:
				checked_results.append(r)
	s.close()
	return checked_results


def get_instances(season, proxy=''):
	tmp = pull(['https://raider.io/api/v1/mythic-plus/static-data?expansion_id=9'], proxy)
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


def get_color(score_tier, points, max=0):
	color = "white"
	if max > 0:
		points = points / 20
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
