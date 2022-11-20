#!/usr/bin/python3
import types, sys
import json
import rio, lists, html
from datetime import datetime

def cleanLists(players, hidden):
	for x in reversed(players):
		if f'{x.json()["name"]}-{x.json()["realm"]}' in hidden:
			players.remove(x)
	return players

if __name__ == "__main__":
	#urls.append('https://checkip.perfect-privacy.com/json')  # Test with your Proxy

	# set the output path as i need (./main.py /var/www/html/index.html)
	out_to_file = 'test.html'
	if len(sys.argv) > 1:
		out_to_file = sys.argv[1]
	# --------------------

	# SET PROXY ---	
	proxy = lists.getProxy()
	#proxy = ''	
	# --------------------

	# Load Player Mains ---
	urls, hidden_players = rio.getAPI_List(lists.getMains())
	players = rio.sort_players_by_score(rio.pull(urls, proxy))
	# ---------------------
	
	# Load Player Alts ---	
	urls, hidden_alts = rio.getAPI_List(lists.getAlts())
	alts = rio.sort_players_by_score(rio.pull(urls, proxy))
	# --------------------

	# Takes alle Pulled Players and writes it to an Json file !
	now = datetime.now()
	date = now.strftime('%Y-%m-%d')
	all_players = players + alts
	dump = []
	for x in all_players:
		dump.append(x.json())
	with open(f'json/{date}.json', 'w', encoding="utf8") as f:
		f.write(json.dumps(dump, sort_keys=True))
	# --------------------

	# remove hidden players
	players = cleanLists(players, hidden_players)
	alts = cleanLists(alts, hidden_alts)
	#---------------------

	# Grab Season from a Player (and look it up in Static Values API) to get the Full Name and Instance names
	# set bnet client_ID and client_secret to get Instance Timers
	season = players[0].json()['mythic_plus_scores_by_season'][0]['season']
	inis,sname = rio.get_instances(season,proxy)
	# --------------------
	
	# get Score_colors from API (if failed from File)
	scolors = rio.get_score_colors(proxy)
	affixe,tyrannical = rio.get_tweek_affixes(proxy)
	# --------------------
	
	# Generate Tables
	tables = {}
	# Mains
	tables.update({'main_score': html.gen_ScoreTable(players, inis, scolors, tyrannical)})
	tables.update({'main_weekly': html.gen_weekly(players, inis, scolors, 'mythic_plus_weekly_highest_level_runs')})
	tables.update({'main_pweek': html.gen_weekly(players, inis, scolors, 'mythic_plus_previous_weekly_highest_level_runs')})
	# Alts
	tables.update({'alts_score': html.gen_ScoreTable(alts, inis, scolors, tyrannical)})
	tables.update({'alts_weekly': html.gen_weekly(alts, inis, scolors, 'mythic_plus_weekly_highest_level_runs')})
	tables.update({'alts_pweek': html.gen_weekly(alts, inis, scolors, 'mythic_plus_previous_weekly_highest_level_runs')})

	html = html.gen_site(affixe, tables, sname, tyrannical)
	
	with open(out_to_file, "w", encoding="utf8") as text_file:
		text_file.write(html)
	
	quit()

