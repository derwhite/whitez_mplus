#!/usr/bin/python3
import types, sys
import json
import rio, lists, html
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

MAX_ILVL = 315

def cleanLists(players, hidden):
	for x in reversed(players):
		if f'{x.json()["name"]}-{x.json()["realm"]}' in hidden:
			players.remove(x)
	return players

def exportDatatoJson(players, alts):
	# Takes alle Pulled Players and writes it to an Json file !
	now = datetime.now()
	date = now.strftime('%Y-%m-%d')

	dump = {'Players': [],
			'Alts': [],
			}
	for i in players:
		dump['Players'].append(i.json())
	for i in alts:
		dump['Alts'].append(i.json())

	with open(f'json/{date}.json', 'w', encoding="utf8") as f:
		f.write(json.dumps(dump, sort_keys=True))
	# --------------------

def clear_low_ilevel_chars(players):
	for x in reversed(players):
		if x.json()['gear']['item_level_equipped'] < MAX_ILVL:
			players.remove(x)
	return players


def cli():
	parser = ArgumentParser(description='Pulls infomation about M+ runs from a custom list of wow players via Raider.io '
										'and Battle.net API.',
							formatter_class=ArgumentDefaultsHelpFormatter)
	parser.add_argument('--mains', help='mains file path', default='lists/players.txt')  # TODO: Change file name to mains.txt for consistencie
	parser.add_argument('--alts', help='alts file path', default='lists/alts.txt')

	args = vars(parser.parse_args())
	return args


def main():
	args = cli()

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
	urls, hidden_players = rio.getAPI_List(lists.get_players(args['mains']))
	players = rio.sort_players_by_ilvl(rio.pull(urls, proxy))
	# ---------------------
	
	# Load Player Alts ---	
	urls, hidden_alts = rio.getAPI_List(lists.get_players(args['alts']))
	alts = rio.sort_players_by_ilvl(rio.pull(urls, proxy))
	# --------------------

	# Sortiere Players by ilvl
	players = rio.sort_players_by_score(players)
	alts = rio.sort_players_by_score(alts)
	#----------------------
	
	# Remove low Item level Chars (because Raider.io API dont gives me Char Levels. Its to remove alts thats not 70)
	players = clear_low_ilevel_chars(players)
	alts = clear_low_ilevel_chars(alts)
	# --------------------
	
	exportDatatoJson(players, alts)

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

	myhtml = html.gen_site(affixe, tables, sname, tyrannical)
	
	with open(out_to_file, "w", encoding="utf8") as text_file:
		text_file.write(myhtml)
	
	quit()


if __name__ == "__main__":
	main()
