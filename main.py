#!/usr/bin/python3
from pathlib import Path
import json
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import configparser

import rio
import lists
import html_out
from player import Player


def clean_lists(mains, hidden):
	for x in reversed(mains):
		if f'{x.json()["name"]}-{x.json()["realm"]}' in hidden:
			mains.remove(x)
	return mains


def export_data_to_json(players):
	# Takes all Pulled Players and writes the responses to an Json file !
	now = datetime.now()
	date = now.strftime('%Y-%m-%d')

	dump = {
		'Mains': [],
		'Alts': [],
	}
	for p in players:
		if p._is_alt:
			dump['Alts'].append(p._response.json())
		else:
			dump['Mains'].append(p._response.json())

	with open(f'json/{date}_2.json', 'w', encoding="utf8") as f:
		f.write(json.dumps(dump, sort_keys=True))


def clear_low_ilevel_chars(mains, min_ilvl):
	for x in reversed(mains):
		if x.json()['gear']['item_level_equipped'] < min_ilvl:
			mains.remove(x)
	return mains


def parse_config_file(config_file_path):
	config = configparser.ConfigParser()
	config.read(config_file_path)

	min_ilvl = config["DEFAULT"].getint("min_ilvl", 300)

	return {'min_ilvl': min_ilvl}


def cli():
	parser = ArgumentParser(description='Pulls infomation about M+ runs from a custom list of wow mains via Raider.io '
										'and Battle.net API.',
							formatter_class=ArgumentDefaultsHelpFormatter)
	# required arguments, e.g.: ./main.py /var/www/html/index.html
	parser.add_argument('outfile', help='output file path with name')
	# optional arguments
	parser.add_argument('--config', help='path to config file', default='lists/settings.conf')
	parser.add_argument('--mains', help='mains file path', default='lists/mains.txt')
	parser.add_argument('--alts', help='alts file path', default='lists/alts.txt')

	args = vars(parser.parse_args())
	return args


def main():
	args = cli()

	if Path(args['outfile']).is_dir():
		print(f"ERROR: outfile '{args['outfile']}' isn't a valid file path!")
		exit(1)

	settings = parse_config_file(args['config'])

	#urls.append('https://checkip.perfect-privacy.com/json')  # Test with your Proxy

	# SET PROXY ---
	proxy = lists.get_proxy()
	#proxy = ''	
	# --------------------

	players = []

	# Load Player Mains ---
	player_list = lists.read_players_file(args['mains'], alts=False)
	rio.append_api_requests(player_list)
	urls = [p['url'] for p in player_list]
	responses = rio.pull(urls, proxy)
	players.extend(Player.create_players(player_list, responses))
	# ---------------------
	
	# Load Player Alts ---
	player_list = lists.read_players_file(args['alts'], alts=True)
	rio.append_api_requests(player_list)
	urls = [p['url'] for p in player_list]
	responses = rio.pull(urls, proxy)
	players.extend(Player.create_players(player_list, responses))
	# --------------------

	# sort Players
	ilvl_sorted_players = list(sorted(players, key=lambda player: player.ilvl, reverse=True))
	score_sorted_players = list(sorted(ilvl_sorted_players, key=lambda p: p._score, reverse=True))
	# --------------------

	# Remove low Item level Chars
	ilvl_filtered_players = list(filter(lambda player: player.ilvl >= settings['min_ilvl'], score_sorted_players))
	# --------------------
	
	export_data_to_json(players)

	# remove hidden mains
	hidden_filtered_players = list(filter(lambda player: not player._is_hidden, ilvl_filtered_players))
	players = hidden_filtered_players
	#---------------------

	# Grab Season from a Player (and look it up in Static Values API) to get the Full Name and Instance names
	# set bnet client_ID and client_secret to get Instance Timers
	season = players[0]._data['mythic_plus_scores_by_season'][0]['season']
	inis, sname = rio.get_instances(season, proxy)
	# --------------------
	
	# get Score_colors from API (if failed from File)
	scolors = rio.get_score_colors(proxy)
	affixe, tyrannical = rio.get_tweek_affixes(proxy)
	# --------------------

	mains = [p for p in players if not p._is_alt]
	alts = [p for p in players if p._is_alt]
	# Generate Tables
	tables = {}
	# Mains
	tables.update({'main_score': html_out.gen_score_table(mains, inis, scolors, tyrannical)})
	tables.update({'main_weekly': html_out.gen_weekly(mains, inis, scolors, 'mythic_plus_weekly_highest_level_runs')})
	tables.update({'main_pweek': html_out.gen_weekly(mains, inis, scolors, 'mythic_plus_previous_weekly_highest_level_runs')})
	# Alts
	tables.update({'alts_score': html_out.gen_score_table(alts, inis, scolors, tyrannical)})
	tables.update({'alts_weekly': html_out.gen_weekly(alts, inis, scolors, 'mythic_plus_weekly_highest_level_runs')})
	tables.update({'alts_pweek': html_out.gen_weekly(alts, inis, scolors, 'mythic_plus_previous_weekly_highest_level_runs')})

	myhtml = html_out.gen_site(affixe, tables, sname, tyrannical)
	
	with open(args['outfile'], "w", encoding="utf8") as text_file:
		text_file.write(myhtml)
	
	quit()


if __name__ == "__main__":
	main()
