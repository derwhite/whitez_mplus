import rio
from datetime import datetime, timezone

# WREWARD=[0,0,278,278,278,281,281,285,288,288,291,294,298,298,301,304] # Season 4
WREWARD=[0,0,382,385,385,389,389,392,395,395,398,402,405,408,408,411,415,415,418,418,421] # Season 1 DF


def get_instance_from_player(player, ini):
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
	for x in player.mythic_plus_best_runs():
		if x['short_name'] == ini:
			best.update({'run':x['mythic_level']})
			best.update({'upgrade':x['num_keystone_upgrades']})
			best.update({'score':x['score']})
			best.update({'affix':x['affixes'][0]['id']})
			break	

	for x in player.mythic_plus_alternate_runs():
		if x['short_name'] == ini:
			alter.update({'run':x['mythic_level']})
			alter.update({'upgrade':x['num_keystone_upgrades']})
			alter.update({'score':x['score']})
			alter.update({'affix':x['affixes'][0]['id']})
			break
	return best, alter		


def get_sterne(upgrade):
	return '*' * upgrade


def gen_score_table(players, inis, colors, isTyrannical):
	str_html = f'<table width="100%">\n'
	str_html += f'<tr><th><span style="color:white">Player</span></th>\n'
	str_html += f'<th width=\"5%\"><span style="color:white">ilvl</span></th>\n'
	str_html += f'<th width=\"7%\"><span style="color:white">Score</span></th>\n'
	for x in inis:
		if x['timer'] == 0:
			ini_timer = ""
			str_keystone_upgrade_timer = ""
		else:
			time_format = "%M:%S"
			timer_dt = datetime.fromtimestamp(x['timer'])
			keystone_upgrade_2 = datetime.fromtimestamp(x['upgrade_2'])
			keystone_upgrade_3 = datetime.fromtimestamp(x['upgrade_3'])

			ini_timer = f'[{timer_dt.strftime(time_format)}]'
			str_keystone_upgrade_timer = f'&#10;+2: {keystone_upgrade_2.strftime(time_format)}&#10;+3: {keystone_upgrade_3.strftime(time_format)}'
			
		str_html += f'<th title="{x["name"]}{str_keystone_upgrade_timer}" width=\"8%\"><span style="white-space:pre-line;color:white">{x["short"]}<br>{ini_timer}</span></th>\n'
	str_html += f'</tr>\n'

	high_score = rio.get_highest_score(players)
	for p in players:
		mainSize=17
		secSize=13
		#-----------------------------------------------------------
		# Count Tier Items an Build a string
		tier = p.get_tier_items()
		#----------------------------------
		# Create Player Line on Website !!
		str_html += f'<tr>\n'
		str_html += f'<td title="Last Update: {p.days_since_last_update()} days ago&#10;{tier}"><a href="{p.profile_url()}" target="_blank"><img src="{p.thumbnail_url()}" width="40" height="40" style="float:left"></a><p style="font-size:{mainSize}px;color:{p.class_color};padding:10px;margin:0px;text-align:left">&emsp;{p.name}</p></td>\n'
		str_html += f'<td><span style="color: {p.class_color}">{p.ilvl}</span></td>'
		sum = p._score  # Player Score
		color = rio.get_color(colors, sum)
		str_html += f'<td><span style="font-size:{mainSize}px;color:{color}">{"{:.2f}".format(sum)}</span></td>\n'
		#-----------------------------
		for ini in inis:
			# Iterate Instances:
			best, alter = get_instance_from_player(p, ini['short'])
			best.update({'color': rio.get_color(colors, best['score'] * 20, high_score)})
			best.update({'sterne': get_sterne(best['upgrade'])})
			alter.update({'color': rio.get_color(colors, alter['score'] * 20, high_score)})
			alter.update({'sterne': get_sterne(alter['upgrade'])})
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
			str_html += f'<td title="{first["score"]} / {sec["score"]} / {round(best["score"]*1.5+alter["score"]*0.5,2)}"><span style="font-size:{mainSize}px;color:{first["color"]}">{first["run"]}</span><span style="font-size:{mainSize}px;color:yellow">{first["sterne"]}</span><span style="color:white"> | </span><span style="font-size:{secSize}px;color:{sec["color"]}">{sec["run"]}</span><span style="font-size:{secSize}px;color:yellow">{sec["sterne"]}</span></td>\n'
		str_html += f'</tr>\n'
	str_html += f'</table>\n'
	return str_html


def gen_weekly(players, inis, colors, weekly):
	players = rio.sort_players_by(players,weekly)
	high = rio.get_highest_score(players)
	str_html = f'<table width="100%">\n'
	str_html += f'<tr><th><span style="color:white">Player</span></th>'
	str_html += f'<th width=\"5%\"><span style="color:white">ilvl</span></th>'
	str_html += f'<th width="5%"><span style="color:white;">+20</span></th><th width="11%"><span style="color:white">Rewards</span></th>'
	for i in range(0,8):
		str_html += f'<th width="7%"></th>'
	str_html += f'</tr>\n'
	for p in players:
		# ------------ PLAYER and SCORE -----------
		# Count Tier Items an Build a string
		tier = p.get_tier_items()
		# ----------------------------------
		str_html += f'<tr>\n'
		str_html += f'<td title="Last Update: {p.days_since_last_update()} days ago&#10;{tier}"><a href="{p.profile_url()}" target="_blank"><img src="{p.thumbnail_url()}" width="40" height="40" style="float:left"></a><p style="color:{p.class_color};padding:10px;margin:0px;text-align:left;">&emsp;{p.name}</p></td>\n'
		str_html += f'<td><span style="color: {p.class_color}">{p.ilvl}</span></td>'
		# --------- Show Left Instances -------
		count = 0
		for i in p._data[weekly]:
			if i['mythic_level'] >= 20:
				count += 1
		color = 'red'
		if count >= 8:
			color = 'green'
			count = 8
		str_html += f'<td><span style="color:{color}">{count-8}</span></td>\n'
		# ---------- 0 / 0 / 0 Rewards -------
		str_html += f'<td><span style="color:white">'
		for i in [0, 3, 7]:
			if i != 0:
				str_html += f' / '
			if len(p._data[weekly]) > i:
				if p._data[weekly][i]['mythic_level'] >= 20:
					reward = WREWARD[20]
				else:
					reward = WREWARD[p._data[weekly][i]['mythic_level']]
				str_html += f'{reward}'
			else:
				str_html += f'-'
				if i == 0:
					break
				else:
					str_html = str_html[:-4]
		str_html += f'</span></td>'
		# ------------- Instances ------
		for i in range(0, 8):
			if i == 0 or i == 3 or i == 7:
				color = 'green'
			else:
				color = 'white'
			if len(p._data[weekly]) > i:
				stern = get_sterne(p._data[weekly][i]['num_keystone_upgrades'])
				dt = datetime.strptime(p._data[weekly][i]['completed_at'], '%Y-%m-%dT%H:%M:%S.000Z')
				dt = dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
				run_time = dt.strftime('%a %d.%m %H:%M %Z')
				str_html += f'<td title="{p._data[weekly][i]["score"]} | {run_time}"><span style="color:{color}">{p._data[weekly][i]["short_name"]} (<a href="{p._data[weekly][i]["url"]}" style="color:{rio.get_color(colors, p._data[weekly][i]["score"] * 20, high)}">{p._data[weekly][i]["mythic_level"]}{stern}</a>)</span></td>\n'
			else:
				str_html += f'<td><span style="color:{color}">-</span></td>\n'
		str_html += '</tr>\n'

	str_html += '</table>\n'
	return str_html


def gen_site(affixes, all_tables, season_name, isTyrannical, version_string):
	now = datetime.now()
	now = now.strftime("%d.%m.%Y %H:%M:%S")
	
	legende = "[Fortified | Tyrannical]"
	if isTyrannical == True:
		legende = "[Tyrannical | Fortified]"

	# Building Website !!
	with open('./templates/main.html', 'r', encoding='utf8') as f:
		myhtml = f.read()

		with open('./static/style.css', 'r', encoding="utf8") as f2:
			css = f2.read()
			myhtml = myhtml.replace('{% stylesheet_content %}', css)

		myhtml = myhtml.replace('{% season_name %}', season_name)
		myhtml = myhtml.replace('{% now %}', now)
		myhtml = myhtml.replace('{% legende %}', legende)
		myhtml = myhtml.replace('{% affixes %}', affixes)

		myhtml = myhtml.replace('{% main_tracker_content %}', all_tables['main_score'])
		myhtml = myhtml.replace('{% main_weekly_content %}', all_tables['main_weekly'])
		myhtml = myhtml.replace('{% alts_tracker_content %}', all_tables['alts_score'])
		myhtml = myhtml.replace('{% alts_weekly_content %}', all_tables['alts_weekly'])
		myhtml = myhtml.replace('{% main_prev_weekly_content %}', all_tables['main_pweek'])
		myhtml = myhtml.replace('{% alts_prev_weekly_content %}', all_tables['alts_pweek'])
		myhtml = myhtml.replace('{% version_string %}', version_string)

		return myhtml
