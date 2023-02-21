import rio
import uuid
from datetime import datetime, timezone

# WREWARD=[0,0,278,278,278,281,281,285,288,288,291,294,298,298,301,304] # Season 4
WREWARD=[0,0,382,385,385,389,389,392,395,395,398,402,405,408,408,411,415,415,418,418,421] # Season 1 DF
DUNGEONS_BACKGROUND = {
	"AA": "resources/dungeons/DF/AA.png",
	"COS": "resources/dungeons/DF/COS.png",
	"HOV": "resources/dungeons/DF/HOV.png",
	"RLP": "resources/dungeons/DF/RLP.png",
	"SBG": "resources/dungeons/DF/SBG.png",
	"TJS": "resources/dungeons/DF/TJS.png",
	"AV": "resources/dungeons/DF/AV.png",
	"NO": "resources/dungeons/DF/NO.png",
}


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
	table_id = uuid.uuid4().hex
	str_html = f'<table id="{table_id}">\n'
	str_html += f'<tr><th>Player</th>\n'
	str_html += f'<th onclick="sortTable(1, \'{table_id}\')" class="ilvl">ilvl</th>\n'
	str_html += f'<th onclick="sortTable(2, \'{table_id}\')" class="score">Score</th>\n'
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
			
		str_html += f'<th class="dungeon {x["short"]}" title="{x["name"]}{str_keystone_upgrade_timer}">{x["short"]}<br>{ini_timer}</th>\n'
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
		str_html += f'<tr onclick="highlightRow(this)">\n'
		str_html += f'<td title="Last Update: {p.days_since_last_update()} days ago&#10;{tier}"><a href="{p.profile_url()}" target="_blank"><img src="{p.thumbnail_url()}" width="35" height="35" style="float:left"></a><p style="font-size:{mainSize}px;color:{p.class_color};padding:6px;margin:0px;text-align:left">&emsp;{p.name}</p></td>\n'
		str_html += f'<td><span style="color: {p.class_color}">{p.ilvl}</span></td>'
		sum = p.score  # Player Score
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
	str_html = f'<table>\n'
	str_html += f'<tr><th>Player</th>'
	str_html += f'<th class="ilvl">ilvl</th>'
	str_html += f'<th class="twenty">+20</th><th class="rewards">Rewards</th>'
	for i in range(0,8):
		str_html += f'<th class="runs_weekly"></th>'
	str_html += f'</tr>\n'
	for p in players:
		# ------------ PLAYER and SCORE -----------
		# Count Tier Items an Build a string
		tier = p.get_tier_items()
		# ----------------------------------
		str_html += f'<tr onclick="highlightRow(this)">\n'
		str_html += f'<td title="Last Update: {p.days_since_last_update()} days ago&#10;{tier}"><a href="{p.profile_url()}" target="_blank"><img src="{p.thumbnail_url()}" width="35" height="35" style="float:left"></a><p style="color:{p.class_color};padding:6px;margin:0px;text-align:left;">&emsp;{p.name}</p></td>\n'
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
		str_html += f'<td>'
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
		str_html += f'</td>'
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
				## TODO Maybe we want to Add instance Picture to Weekly runs, too. 
				str_html += f'<td title="{p._data[weekly][i]["score"]} | {run_time}"><span style="color:{color}">{p._data[weekly][i]["short_name"]} (<a href="{p._data[weekly][i]["url"]}" style="color:{rio.get_color(colors, p._data[weekly][i]["score"] * 20, high)}">{p._data[weekly][i]["mythic_level"]}{stern}</a>)</span></td>\n'
			else:
				str_html += f'<td><span style="color:{color}">-</span></td>\n'
		str_html += '</tr>\n'

	str_html += '</table>\n'
	return str_html


def gen_affixes_html(affixes):
	tweek_affixes_html = []
	for a in affixes['this_week']:
		affix_html = f'<td class=\"tbl_affixe\"><a class="icontiny" ' \
					 f'data-game="wow" data-type="affix" href="{a["wowhead_url"]}">' \
					 f'<img src="https://wow.zamimg.com/images/wow/icons/tiny/{a["icon"]}.gif" ' \
					 f'style="vertical-align: middle;" loading="lazy">' \
					 f'<span class="tinycontxt"> {a["name"]}</span></a></td>'
		tweek_affixes_html.append(affix_html)
	tweek_affixes_out = "<td class=\"tbl_affixe\">This Week:</td>" + ''.join(tweek_affixes_html)

	if affixes['next_week'] is None:
		return tweek_affixes_out + "\n"

	nweek_affixes_html = []
	for a in affixes['next_week']:
		affix_html = f'<td class=\"tbl_affixe\"><a class="icontiny" ' \
					 f'data-game="wow" data-type="affix" href="{a["wowhead_url"]}">' \
					 f'<img src="https://wow.zamimg.com/images/wow/icons/tiny/{a["icon"]}.gif" ' \
					 f'style="vertical-align: middle;" loading="lazy">' \
					 f'<span class="tinycontxt"> {a["name"]}</span></a></td>'
		nweek_affixes_html.append(affix_html)
	nweek_affixes_out = "<td class=\"tbl_affixe\">Next Week:</td>" + ''.join(nweek_affixes_html)

	affixes_out = "<table><tr><th class=\"tbl_affixe\" spancol=5 style=\"font-size: 20px;\">Affixes:</th></tr>\n<tr>" + tweek_affixes_out + "\n" + "</tr><tr>" + nweek_affixes_out + "</tr></table>"
	return affixes_out


def gen_site(affixes, all_tables, season_name, version_string):
	now = datetime.now()
	now = now.strftime("%d.%m.%Y %H:%M:%S")

	if affixes['tyrannical']:
		legend = "[Tyrannical | Fortified]"
	else:
		legend = "[Fortified | Tyrannical]"

	affixes_html = gen_affixes_html(affixes)

	# Building Website !!
	with open('./templates/main.html', 'r', encoding='utf8') as f:
		myhtml = f.read()

		dynamic_css = "\n"		## Maybe you want to Change this to a cleaner way ^_-
		for k, v in DUNGEONS_BACKGROUND.items():
			dynamic_css += ".mytabs ." + k + " {\n"
			dynamic_css += f"background-image: url({v});\n"
			dynamic_css += "}\n"

		with open('./static/style.css', 'r', encoding="utf8") as f2:
			css = f2.read()
			css += dynamic_css
			myhtml = myhtml.replace('{% stylesheet_content %}', css)

		myhtml = myhtml.replace('{% season_name %}', season_name)
		myhtml = myhtml.replace('{% now %}', now)
		myhtml = myhtml.replace('{% legend %}', legend)
		myhtml = myhtml.replace('{% affixes %}', affixes_html)

		myhtml = myhtml.replace('{% main_tracker_content %}', all_tables['main_score'])
		myhtml = myhtml.replace('{% main_weekly_content %}', all_tables['main_weekly'])
		myhtml = myhtml.replace('{% alts_tracker_content %}', all_tables['alts_score'])
		myhtml = myhtml.replace('{% alts_weekly_content %}', all_tables['alts_weekly'])
		myhtml = myhtml.replace('{% main_prev_weekly_content %}', all_tables['main_pweek'])
		myhtml = myhtml.replace('{% alts_prev_weekly_content %}', all_tables['alts_pweek'])
		myhtml = myhtml.replace('{% version_string %}', version_string)

		return myhtml
