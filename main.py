#!/usr/bin/python3
import os

import shutil
from pathlib import Path
import json
from datetime import datetime, timedelta, timezone
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import configparser
import subprocess
import sys

import rio
import lists
import html_out
from player import Player
from affix_servant import AffixServant
from bnet import BnetBroker


EXPANSION_ID = 10

def sync_directories(source_dir, dest_dir): #AHAHAHA from ChatGPT ^^
	"""
	Synchronize the contents of two directories, source_dir and dest_dir.
	Create the corresponding directories if necessary.
	Delete content from dest_dir if not present in source_dir.
	Returns a list of changes made.
	"""
	changes = []
	if not os.path.exists(dest_dir):
		os.makedirs(dest_dir)
	# Get a list of all files in source_dir
	source_files = os.listdir(source_dir)
	# Loop through all files in source_dir
	for file in source_files:
		# Get the full path of the file
		source_file_path = os.path.join(source_dir, file)
		dest_file_path = os.path.join(dest_dir, file)
		# If the file is a directory, call the function recursively
		if os.path.isdir(source_file_path):
			changes.extend(sync_directories(source_file_path, dest_file_path))
		# If the file is a file, copy it to dest_dir if it doesn't exist
		elif not os.path.exists(dest_file_path):
			shutil.copy(source_file_path, dest_file_path)
			changes.append("Copied {} to {}".format(source_file_path, dest_file_path))
		# If the file exists in both directories, check if it has been modified
		else:
			source_file_time = os.path.getmtime(source_file_path)
			dest_file_time = os.path.getmtime(dest_file_path)
			# If the file has been modified, copy it to dest_dir
			if source_file_time > dest_file_time:
				shutil.copy(source_file_path, dest_file_path)
				changes.append("Updated {} to {}".format(source_file_path, dest_file_path))
	# Get a list of all files in dest_dir
	dest_files = os.listdir(dest_dir)
	# Loop through all files in dest_dir
	for file in dest_files:
		# Get the full path of the file
		source_file_path = os.path.join(source_dir, file)
		dest_file_path = os.path.join(dest_dir, file)
		# If the file doesn't exist in source_dir, delete it from dest_dir
		if not os.path.exists(source_file_path):
			if os.path.isdir(dest_file_path):
				shutil.rmtree(dest_file_path)
			else:
				os.remove(dest_file_path)
			changes.append("Deleted {}".format(dest_file_path))
	return changes


def get_git_revision_short_hash():
	try:
		sub_output = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], check=True, capture_output=True)
		return sub_output.stdout.decode('ascii').strip()
	except subprocess.CalledProcessError as e:
		print(f"WARNING: {e} {e.output}")
		return ""


def generate_version_string():
	git_short_hash = get_git_revision_short_hash()
	if git_short_hash:
		return f"Version: {git_short_hash}"
	else:
		return ""


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


def parse_config_file(config_file_path):
	config = configparser.ConfigParser()
	config.read(config_file_path)

	min_ilvl = config["DEFAULT"].getint("min_ilvl", 300)
	min_score = config["DEFAULT"].getint("min_score", 1)
	max_inactive_days = config["DEFAULT"].getint("max_inactive_days", 30)

	client_id = config['BNET'].get('client_id', "")
	client_secret = config['BNET'].get('client_secret', "")

	rio_apikey = config['RIO'].get('rio_apikey', "")

	# Fallback
	if client_id == "" or client_secret == "":
		print("INFO: bnet client_id and client_secret not found in config file. File 'bnetkeys' is used instead.")
		print("      Please move the keys to the new settings config file!")
		if os.path.isfile('bnetkeys'):
			with open('bnetkeys') as f:
				lines = f.readlines()
			client_id = lines[0].strip()
			client_secret = lines[1].strip()

	if rio_apikey == "":
		print('INFO: Rio is running without Rio_APIKEY !')

	settings = {
		'min_ilvl': min_ilvl,
		'min_score': min_score,
		'max_inactive_days': max_inactive_days,
		'client_id': client_id,
		'client_secret': client_secret,
		'rio_apikey': rio_apikey
	}

	return settings


def cli():
	parser = ArgumentParser(description='Pulls information about M+ runs from a custom list of wow mains via Raider.io '
										'and Battle.net API.',
							formatter_class=ArgumentDefaultsHelpFormatter)
	# required arguments, e.g.: ./main.py /var/www/html/index.html
	parser.add_argument('outfile', help='output file path with name')
	# optional arguments
	parser.add_argument('--config', help='path to config file', default='lists/settings.conf')
	parser.add_argument('--mains', help='mains file path', default='lists/mains.txt')
	parser.add_argument('--alts', help='alts file path', default='lists/alts.txt')
	parser.add_argument('--no_copy', help='dont copy resources to output directoy', action='store_true')
	parser.add_argument('--backup_requests', help='creates json file from Player datas', action='store_true')
	

	args = vars(parser.parse_args())
	return args

def clean_css_file(file_path):
	"""	 Removes all comments and empty lines from a CSS file."""
	with open(file_path, 'r') as f:
		lines = f.readlines()
	with open(file_path, 'w') as f:
		for line in lines:
			if not line.strip().startswith('/*') and line.strip() != '' and not line.strip().endswith('*/'):
				f.write(line)

def main():
	args = cli()

	if Path(args['outfile']).is_dir():
		print(f"ERROR: outfile '{args['outfile']}' isn't a valid file path!")
		exit(1)

	## Copy Resources to Output Directory
	if not args['no_copy']:
		if os.path.dirname(Path(args['outfile']).absolute()) == os.getcwd():
			print(f"ERROR: Your output path matches your script path !")
			print(f"try to use a different output path or use the --no_copy flag to disable copying resources.")
			exit(1)
		sync_directories('resources', os.path.join(os.path.dirname(Path(args['outfile']).absolute()), 'resources'))
		sync_directories('static', os.path.join(os.path.dirname(Path(args['outfile']).absolute()), 'static'))
		clean_css_file(os.path.join(os.path.dirname(Path(args['outfile']).absolute()), 'static', 'style.css'))
		# TODO Minify CSS and JS
	## ---------------------------------------

	settings = parse_config_file(args['config'])
	# initialize BnetBroker singleton
	bnet_broker = BnetBroker(settings['client_id'], settings['client_secret'])
	Rio_APIKEY = settings['rio_apikey']
	RaiderIO = rio.RaiderIO(Rio_APIKEY)

	# SET PROXY ---
	proxy = lists.get_proxy()
	# --------------------

	season, season_end = RaiderIO.get_current_season(EXPANSION_ID)
	if not season:
		print("Couldn't find an active Season")
		sys.exit(1)

	players = []

	# Load Player Mains ---
	player_list = lists.read_players_file(args['mains'], alts=False)
	RaiderIO.append_api_requests(player_list, season)
	urls = [p['url'] for p in player_list]
	responses = RaiderIO.pull(urls)
	players.extend(Player.create_players(player_list, responses))
	# ---------------------
	
	# Load Player Alts ---
	player_list = lists.read_players_file(args['alts'], alts=True)
	RaiderIO.append_api_requests(player_list, season)
	urls = [p['url'] for p in player_list]
	responses = RaiderIO.pull(urls)
	players.extend(Player.create_players(player_list, responses))
	# --------------------
	
	# RaiderIO.extract_player_ids(players)
	runs_dict = RaiderIO.get_run_details(players)

	if args['backup_requests']:
		export_data_to_json(players)

	# sort Players
	ilvl_sorted_players = list(sorted(players, key=lambda player: player.ilvl, reverse=True))
	score_sorted_players = list(sorted(ilvl_sorted_players, key=lambda p: p.score, reverse=True))
	# --------------------

	# Filter low iLvl and inactive players
	inactive_filtered_players = list(filter(lambda player: player.days_since_last_update() < settings['max_inactive_days'], score_sorted_players))
	ilvl_filtered_players = list(filter(lambda player: player.ilvl >= settings['min_ilvl'], inactive_filtered_players))
	score_filtered_players = list(filter(lambda player: player.score >= settings['min_score'], ilvl_filtered_players))
	# --------------------

	# remove hidden mains
	hidden_filtered_players = list(filter(lambda player: not player._is_hidden, score_filtered_players))
	mplus_players = hidden_filtered_players
	general_players = inactive_filtered_players  # show all active chars in general tab regardless of their score or ilvl
	# ---------------------

	affix_s = AffixServant(RaiderIO)
	affixes = affix_s.get_affixes()

	# get Instances and Season Name
	# set bnet client_ID and client_secret to get Instance Timers
 
	inis, sname = RaiderIO.get_instances(EXPANSION_ID, season)
	# --------------------
 
	season_ends_str = ""
	if season_end and season_end - datetime.now(tz=timezone.utc) < timedelta(days=30):
		season_ends_str = f"{sname} ends on {season_end.strftime('%d.%m.%Y %H:%M')}"

	# get Score_colors from API (if failed from File)
	scolors = RaiderIO.get_score_colors()
	# --------------------

	mains = [p for p in mplus_players if not p._is_alt]
	alts = [p for p in mplus_players if p._is_alt]
	# Generate Tables
	tables = {}
	# General overview
	tables.update({'general': html_out.gen_general_tab(general_players)})
	# Mains
	tables.update({'main_score': html_out.gen_score_table(mains, inis, scolors)})
	tables.update({'main_weekly': html_out.gen_weekly(mains, inis, scolors, 'mythic_plus_weekly_highest_level_runs', runs_dict)})
	tables.update({'main_pweek': html_out.gen_weekly(mains, inis, scolors, 'mythic_plus_previous_weekly_highest_level_runs', runs_dict)})
	# Alts
	tables.update({'alts_score': html_out.gen_score_table(alts, inis, scolors)})
	tables.update({'alts_weekly': html_out.gen_weekly(alts, inis, scolors, 'mythic_plus_weekly_highest_level_runs', runs_dict)})
	tables.update({'alts_pweek': html_out.gen_weekly(alts, inis, scolors, 'mythic_plus_previous_weekly_highest_level_runs', runs_dict)})

	myhtml = html_out.gen_site(affixes, tables, sname, season_ends_str,generate_version_string())
	
	with open(args['outfile'], "w", encoding="utf8") as text_file:
		text_file.write(myhtml)


if __name__ == "__main__":
	main()
