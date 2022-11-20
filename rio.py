import random
from multiprocessing.dummy import Pool as ThreadPool
import requests
import json
import lists
import bnet

def getAPI_List(PlayerList):
	request_urls = []		# Erzeuge API Anfrage 	Liste !!
	hidden_players = []
	for player in PlayerList:
		player=player.strip('\n')
		if player[:1] == '#':
			continue
		if player[:1] == '!':
			hidden_players.append(player[1:])
			player = player[1:]
		tmp = player.split('-')
		request_urls.append(f'https://raider.io/api/v1/characters/profile?region=eu&realm={tmp[1]}&name={tmp[0]}&fields=talents,mythic_plus_best_runs,mythic_plus_scores_by_season:current,mythic_plus_alternate_runs,gear,mythic_plus_weekly_highest_level_runs,mythic_plus_previous_weekly_highest_level_runs')
	return request_urls, hidden_players

def pull(URLs, proxy=''):    #sometimes gets stuck if Proxy does not response -.-
	s = requests.Session()
	s.headers.update({'Cache-Control': 'none','Pragma':'ino-cache'})
	pool = ThreadPool(4)
	if proxy != '':
		with open('proxykey') as f:
			key = f.readlines()
			proxies = {
			'http': 'http://' + key[0].strip() + proxy + ':8080',
			'https': 'https://' + key[0].strip() + proxy + ':8080'
			}
			s.proxies.update(proxies)
	results = pool.map(s.get, URLs, chunksize=1) # DL all URLS !!
	pool.close()
	pool.join()
	s.close()
	for r in reversed(results): #bereinige fehlgeschlagene requests
		if r.status_code != 200:
			results.remove(r)
	return results

def get_instances(season, proxy=''):
	tmp = pull(['https://raider.io/api/v1/mythic-plus/static-data?expansion_id=8'], proxy)
	try:
		bnet_Token = bnet.getBnetAccessToken()
	except:
		bnet_Token = ""
	instances = []
	season_name=""
	for sea in tmp[0].json()['seasons']:
		if sea['slug'] == season:
			for ini in sea['dungeons']:
				ini_time = 0
				if bnet_Token != "":
					ini_timer = pull([f'https://eu.api.blizzard.com/data/wow/mythic-keystone/dungeon/{ini["challenge_mode_id"]}?namespace=dynamic-eu&locale=en_EN&access_token={bnet_Token}'], proxy)
					ini_time = ini_timer[0].json()['keystone_upgrades'][0]['qualifying_duration'] / 1000
				instances.append({'short':ini['short_name'], 'name':ini['name'], 'timer': ini_time})
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

def get_tweek_affixes(proxy=''): #Affixe ufschreiben
	tmp = pull(['https://raider.io/api/v1/mythic-plus/affixes?region=eu&locale=en'], proxy)
	if tmp[0].status_code == 200:
		r = tmp[0]
		tweek_affixes_out = ""
		tyrannical = False
		for x in r.json()['affix_details']:
			tweek_affixes_out += x['name'] + ","
			if x['id'] == 9:
				tyrannical = True
		tweek_affixes_out = tweek_affixes_out[:-1] + "\n"
	else:
		tweek_affixes_out = "RaiderIO Affixes Error"
		tyrannical = False
	return tweek_affixes_out, tyrannical

def sort_players_by_score(results):
	i=0
	while i < len(results):
		x=i+1
		while x < len(results):
			sum=results[x].json()['mythic_plus_scores_by_season'][0]['scores']['all']
			sum2=results[i].json()['mythic_plus_scores_by_season'][0]['scores']['all']
			if sum > sum2:
				tmp = results[i]
				results[i]=results[x]
				results[x]=tmp
			x+=1
		i+=1
	return results

def sort_players_by(results, weekly):
	i=0
	while i < len(results):
		x=i+1
		while x < len(results):
			sum=0
			for r in results[x].json()[weekly]:
				if r['mythic_level'] >= 15:
					sum+=300
				sum+=r['mythic_level']
			sum2=0
			for r in results[i].json()[weekly]:
				if r['mythic_level'] >= 15:
					sum2+=300
				sum2+=r['mythic_level']
			if sum > sum2:
				#print(results[i].json()['name'],sum2,results[x].json()['name'],sum)
				tmp = results[i]
				results[i]=results[x]
				results[x]=tmp
			x+=1
		i+=1
	return results

def getColor(score_tier, points, max=0):
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
		for ini in player.json()['mythic_plus_best_runs']:
			if high < ini['score']:
				high = ini['score']
	return high
