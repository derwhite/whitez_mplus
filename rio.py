from multiprocessing.dummy import Pool as ThreadPool
import requests
import json
import bnet


def get_api_list(player_list):
	request_urls = []		# Erzeuge API Anfrage 	Liste !!
	hidden_players = []
	for player in player_list:
		realm = player['realm']
		name = player['name']
		request_urls.append(f'https://raider.io/api/v1/characters/profile?region=eu&realm={realm}&name={name}&fields=talents,mythic_plus_best_runs,mythic_plus_scores_by_season:current,mythic_plus_alternate_runs,gear,mythic_plus_weekly_highest_level_runs,mythic_plus_previous_weekly_highest_level_runs')
	return request_urls, hidden_players


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
	s.close()
	return results


def get_instances(season, settings, proxy=''):
	tmp = pull(['https://raider.io/api/v1/mythic-plus/static-data?expansion_id=9'], proxy)
	bnet_Token = bnet.create_access_token(settings['client_id'], settings['client_secret'])
	instances = []
	season_name=""
	for sea in tmp[0].json()['seasons']:
		if sea['slug'] == season:
			for ini in sea['dungeons']:
				ini_time = 0
				upgrade_2 = 0
				upgrade_3 = 0
				if bnet_Token is not None:
					try:
						ini_timer = pull([f'https://eu.api.blizzard.com/data/wow/mythic-keystone/dungeon/{ini["challenge_mode_id"]}?namespace=dynamic-eu&locale=en_EN&access_token={bnet_Token}'], proxy)
						ini_time = ini_timer[0].json()['keystone_upgrades'][0]['qualifying_duration'] / 1000
						upgrade_2 = ini_timer[0].json()['keystone_upgrades'][1]['qualifying_duration'] / 1000
						upgrade_3 = ini_timer[0].json()['keystone_upgrades'][2]['qualifying_duration'] / 1000
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


def get_tweek_affixes(proxy=''):  # Affixe ufschreiben
	tmp = pull(['https://raider.io/api/v1/mythic-plus/affixes?region=eu&locale=en'], proxy)
	if tmp[0].status_code == 200:
		r = tmp[0].json()
		tyrannical = False
		affixes_html = []
		for x in r['affix_details']:
			affix_html = f'<a class="icontiny" style="background: left center no-repeat;" ' \
						 f'data-game="wow" data-type="affix" href="{x["wowhead_url"]}">' \
						 f'<img src="https://wow.zamimg.com/images/wow/icons/tiny/{x["icon"]}.gif" ' \
						 f'style="vertical-align: middle;" loading="lazy">' \
						 f'<span class="tinycontxt"> {x["name"]}</span></a>'
			affixes_html.append(affix_html)
			if x['id'] == 9:
				tyrannical = True
		tweek_affixes_out = ', '.join(affixes_html) + "\n"
	else:
		tweek_affixes_out = "RaiderIO Affixes Error"
		tyrannical = False
	return tweek_affixes_out, tyrannical


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
