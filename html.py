import rio
from datetime import datetime, timezone

# WREWARD=[0,0,278,278,278,281,281,285,288,288,291,294,298,298,301,304] # Season 4
WREWARD=[0,0,382,385,385,389,389,392,395,395,398,402,405,408,408,411,415,415,418,418,421] # Season 1 DF

CLASS_COLOR={
	'Death Knight': '#C41F3B',
	'Demon Hunter': '#A330C9',
	'Druid': '#FF7D0A',
	'Hunter': '#ABD473',
	'Mage': '#69CCF0',
	'Monk': '#00FF96',
	'Paladin': '#F58CBA',
	'Priest': '#FFFFFF',
	'Rogue': '#FFF569',
	'Shaman': '#0070DE',
	'Warlock': '#9482C9',
	'Warrior': '#C79C6E',
	'Evoker': '#33937F',
	}

def getInstance_from_player(player, ini):
	best = {}
	alter = {}
	best.update({'run': 0})
	best.update({'upgrade': 0})
	best.update({'score': 0})
	best.update({'affix': 0})
	alter.update({'run': 0})
	alter.update({'upgrade': 0})
	alter.update({'score': 0})
	alter.update({'affix': 0})
	for x in player['mythic_plus_best_runs']:
		if x['short_name'] == ini:
			best.update({'run':x['mythic_level']})
			best.update({'upgrade':x['num_keystone_upgrades']})
			best.update({'score':x['score']})
			best.update({'affix':x['affixes'][0]['id']})
			break	

	for x in player['mythic_plus_alternate_runs']:
		if x['short_name'] == ini:
			alter.update({'run':x['mythic_level']})
			alter.update({'upgrade':x['num_keystone_upgrades']})
			alter.update({'score':x['score']})
			alter.update({'affix':x['affixes'][0]['id']})
			break
	return best, alter		

def getSterne(upgrade):
	count = upgrade
	stern = ''
	while count > 0:
		stern += f'*'
		count -= 1
	return stern

## SCORE TABLE -------
def gen_ScoreTable(players, inis, colors, isTyrannical):
	html = f'<table width="100%">\n'
	html += f'<tr><th><span style="color:white;background-color:black">Player</span></th><th width=\"8%\"><span style="color:white;background-color:black">Score</span></th>\n'
	for x in inis:
		if x['timer'] == 0:
			ini_timer = ""
		else:
			ini_timer = f'[{int(x["timer"] // 60)}:{str(int(x["timer"] % 60)).zfill(2)}]'

		html += f'<th title="{x["name"]}" width=\"8%\"><span style="white-space:pre-line;color:white;background-color:black">{x["short"]}<br>{ini_timer}</span></th>\n'
	html += f'</tr>\n'
#----------------------------
	high_score = rio.get_highest_score(players)
	for p in players:
		mainSize=17
		secSize=13
		# Last Crawled at
		dt = datetime.strptime(p.json()['last_crawled_at'], '%Y-%m-%dT%H:%M:%S.000Z')
		tday = datetime.now()
		old = tday - dt
		#-----------------------------------------------------------
		# Create Player Line on Website !!
		html += f'<tr>\n'
		html += f'<td title="Last Update: {old.days} days ago&#10;"><a href="{p.json()["profile_url"]}" target="_blank"><img src="{p.json()["thumbnail_url"]}" width="40" height="40" style="float:left"></a><p style="font-size:{mainSize}px;color:{CLASS_COLOR[p.json()["class"]]};padding:10px;margin:0px;text-align:left">&emsp;{p.json()["name"]}&emsp;[{p.json()["gear"]["item_level_equipped"]}]</p></td>\n'
		sum = p.json()['mythic_plus_scores_by_season'][0]['scores']['all'] #Player Score
		color = rio.getColor(colors, sum)
		html += f'<td><span style="font-size:{mainSize}px;color:{color}">{"{:.2f}".format(sum)}</span></td>\n'
		#-----------------------------
		for ini in inis:
			# Iterate Instances:
			best, alter = getInstance_from_player(p.json(),ini['short'])
			best.update({'color': rio.getColor(colors, best['score']*20, high_score)})
			best.update({'sterne': getSterne(best['upgrade'])})
			alter.update({'color': rio.getColor(colors, alter['score']*20, high_score)})
			alter.update({'sterne': getSterne(alter['upgrade'])})
			first = {}
			sec = {}
			if isTyrannical:
				if best['affix'] == 9:
					first = best
					sec = alter
				else:
					sec = best
					first = alter
			else:
				if best['affix'] == 10:
					first = best
					sec = alter
				else:
					sec = best
					first = alter
			html += f'<td title="{first["score"]} / {alter["score"]} / {round(best["score"]*1.5+alter["score"]*0.5,2)}"><span style="font-size:{mainSize}px;color:{first["color"]}">{first["run"]}</span><span style="font-size:{mainSize}px;color:yellow">{first["sterne"]}</span><span style="color:white"> | </span><span style="font-size:{secSize}px;color:{sec["color"]}">{sec["run"]}</span><span style="font-size:{secSize}px;color:yellow">{sec["sterne"]}</span></td>\n'
		html += f'</tr>\n'
	html += f'</table>\n'
	return html

def gen_weekly(players, inis, colors, weekly):
	players = rio.sort_players_by(players,weekly)
	high = rio.get_highest_score(players)
	html = f'<table width="100%">\n'
	html += f'<tr><th><span style="color:white">Player</span></th><th width="7%"><span style="color:white;">+20</span></th><th width="12%"><span style="color:white">Rewards</span></th>'
	for i in range(0,8):
		html += f'<th width="7%"></th>'
	html += f'</tr>\n'
	for p in players:
		# ------------ PLAYER and SCORE -----------
		dt = datetime.strptime(p.json()['last_crawled_at'], '%Y-%m-%dT%H:%M:%S.000Z')
		tday = datetime.now()
		old = tday - dt
		html += f'<tr>\n'
		html += f'<td title="Last Update: {old.days} days ago&#10;"><a href="{p.json()["profile_url"]}" target="_blank"><img src="{p.json()["thumbnail_url"]}" width="40" height="40" style="float:left"></a><p style="color:{CLASS_COLOR[p.json()["class"]]};padding:10px;margin:0px;text-align:left;">&emsp;{p.json()["name"]}&emsp;[{p.json()["gear"]["item_level_equipped"]}]</p></td>\n'
		
		#--------- Show Left Instances -------#
		count = 0
		for i in p.json()[weekly]:
			if i['mythic_level'] >= 20:
				count += 1
		color = 'red'
		if count > 8:
			count = 8
		elif count == 8:
			color='green'
		html += f'<td><span style="color:{color}">{count-8}</span></td>\n'
		#---------- 0 / 0 / 0 overview -------#
		html += f'<td><span style="color:white">'
		for i in [0,3,7]:
			if i != 0:
				html += f' / '
			if len(p.json()[weekly]) > i:
				if p.json()[weekly][i]['mythic_level'] >= 20:
					reward = WREWARD[20]
				else:
					reward = WREWARD[p.json()[weekly][i]['mythic_level']]
				html += f'{reward}'
			else:
				html += f'-'
				if i == 0:
					break
				else:
					html = html[:-4]
				#continue
		html += f'</span></td>'
		# ------------- Instances ------#
		for i in range(0,8):
			if i == 0 or i == 3 or i == 7:
				color='green'
			else:
				color='white'
			try:
				stern = getSterne(p.json()[weekly][i]['num_keystone_upgrades'])
				dt = datetime.strptime(p.json()[weekly][i]['completed_at'], '%Y-%m-%dT%H:%M:%S.000Z')
				dt = dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
				run_time = dt.strftime('%a %d.%m %H:%M %Z')
				html += f'<td title="{p.json()[weekly][i]["score"]} | {run_time}"><span style="color:{color}">{p.json()[weekly][i]["short_name"]} (<a href="{p.json()[weekly][i]["url"]}" style="color:{rio.getColor(colors, p.json()[weekly][i]["score"]*20,high)}">{p.json()[weekly][i]["mythic_level"]}{stern}</a>)</span></td>\n'
			except:
				html += f'<td><span style="color:{color}">-</span></td>\n'
		html += '</tr>\n'


	html += '</table>\n'
	return html

#-------------------------------------------------------

def gen_site(affixes, all_tables, season_name, isTyrannical):
	now = datetime.now()
	now = now.strftime("%d.%m.%Y %H:%M:%S")
	
	legende = "[Fortified / Tyrannical]"
	if isTyrannical == True:
		legende = "[Tyrannical / Fortified]"
	
	myhtml = f'<!DOCTYPE html>\n'				# Building Website !!
	myhtml += f'<html><head><meta charset="utf-8"></head><body><h1 style="Color:white;">current Season: "{season_name}"</h1><h2 style="color:white">last Update: {now}&emsp;&emsp;&emsp;{legende}</h2>\n'
	myhtml += f'<h3 style="color:white">Affixe: {affixes}</h3>\n'
	# Open Tab
	myhtml += f'<div class="mytabs"><input type="radio" id="Main" name="mytabs" checked="checked"><label for="Main">Main Tracker</label><div class="tab">\n'
	myhtml += all_tables['main_score']
	myhtml += f'</div>\n'
	# next Tab
	myhtml += f'<input type="radio" id="Thisweek" name="mytabs"><label for="Thisweek">Main Weekly</label><div class="tab">'
	myhtml += all_tables['main_weekly']
	myhtml += f'</div>\n'
	# next Tab
	myhtml += f'<input type="radio" id="prevweek" name="mytabs"><label for="prevweek" style="margin-left: 1%">Alts Tracker</label><div class="tab">'
	myhtml += all_tables['alts_score']
	myhtml += f'</div>\n'
	# next Tab
	myhtml += f'<input type="radio" id="twink" name="mytabs"><label for="twink">Alts Weekly</label><div class="tab">\n'
	myhtml += all_tables['alts_weekly']
	myhtml += f'</div>\n'
	# next Tab
	myhtml += f'<input type="radio" id="TThisweek" name="mytabs"><label for="TThisweek" style="margin-left: 1%">Main prev Weekly</label><div class="tab">'
	myhtml += all_tables['main_pweek']
	myhtml += f'</div>\n'
	# next Tab
	myhtml += f'<input type="radio" id="Tprevweek" name="mytabs"><label for="Tprevweek">Alts prev Weekly</label><div class="tab">'
	myhtml += all_tables['alts_pweek']
	myhtml += '</div>\n'
	myhtml += '</div>\n'
	myhtml += '<br><br><br><p style="color:white">All data provided by <a href="https://raider.io">Raider.io</a> & <a href="https://battle.net">Battle.net</a></p>\n'
	myhtml += '<p style="color:white">This Project source is hosted on <a href="https://github.com/derwhite/whitez_mplus">Github.com</a>\n'

	myhtml += '</body>\n'

	myhtml += '<style>\n'
	myhtml += 'table th {\n'
	myhtml += '	position: sticky; top: 0;\n'
	myhtml += '	padding: 20px;\n'
	myhtml += '	margin: 20px;\n'
	myhtml += '	font-size: 18px;\n'
	myhtml += '}\n'
	myhtml += 'table, th, td {\n'
	myhtml += '	border: 1px solid #383838;border-collapse: collapse;\n'
	myhtml += '}\n'
	myhtml += 'th, td {\n'
	myhtml += '	padding: 2px;text-align:center;\n'
	myhtml += '	font-size: 17px;\n'
	myhtml += '}\n'
	myhtml += 'tr:nth-child(even) {\n'
	myhtml += '	background-color: #181818;\n'
	myhtml += '}\n'
	myhtml += 'tr:not(:first-child):hover {\n'
	myhtml += '     background-color: #012e31;\n'
	myhtml += '}\n'
	myhtml += 'body {\n'
	myhtml += '    background-color: black;\n'
	myhtml += '}\n'
	myhtml += '.mytabs {\n'
	myhtml += '    display: flex;\n'
	myhtml += '    flex-wrap: wrap;\n'
	myhtml += '    max-width: 100%;\n'
	myhtml += '    margin: none;\n'
	myhtml += '    padding: none;\n'
	myhtml += '}\n'
	myhtml += '.mytabs input[type="radio"] {\n'
	myhtml += '    display: none;\n'
	myhtml += '}\n'
	myhtml += '.mytabs label {\n'
	myhtml += '    padding: 10px;\n'
	myhtml += '	width: 85px;\n'
	myhtml += '    background: black;\n'
	myhtml += '    font-weight: bold;\n'
	myhtml += '	color: white;\n'
	myhtml += 'border: 1px solid #383838;\n'
	myhtml += '	text-align: center;\n'
	myhtml += '	font-size: 18px;\n'
	myhtml += '	border-radius: 15px 15px 0px 0px;\n'
	myhtml += '}\n'

	myhtml += '.mytabs .tab {\n'
	myhtml += '    width: 100%;\n'
	myhtml += '    padding: none;\n'
	myhtml += '    background: black;\n'
	myhtml += '    order: 1;\n'
	myhtml += '    display: none;\n'
	myhtml += '}\n'
	myhtml += '.mytabs .tab h2 {\n'
	myhtml += '    font-size: 3em;\n'
	myhtml += '}\n'

	myhtml += '.mytabs input[type=\'radio\']:checked + label + .tab {\n'
	myhtml += '    display: block;\n'
	myhtml += '}\n'

	myhtml += '.mytabs input[type="radio"]:checked + label {\n'
	myhtml += '    background: black;\n'
	myhtml += '	color: red;\n'
	myhtml += '}\n'
	myhtml += '</style>\n'
	myhtml += '</html>\n'

	return myhtml
