import rio
import uuid
from datetime import datetime, timezone
from player import Player


WREWARD = [0, 0, 415, 418, 421, 421, 424, 424, 428, 428, 431, 431, 434, 434, 437, 437, 441, 441, 444, 444, 447] # Season 2 DF

DUNGEONS_BACKGROUND = {
	"AA": "resources/dungeons/DF/AA.png",
	"COS": "resources/dungeons/DF/COS.png",
	"HOV": "resources/dungeons/DF/HOV.png",
	"RLP": "resources/dungeons/DF/RLP.png",
	"SBG": "resources/dungeons/DF/SBG.png",
	"TJS": "resources/dungeons/DF/TJS.png",
	"AV": "resources/dungeons/DF/AV.png",
	"NO": "resources/dungeons/DF/NO.png",
	# Season 2
 	"BH": "resources/dungeons/DF/BH.png",
	"FH": "resources/dungeons/DF/FH.png",
	"HOI": "resources/dungeons/DF/HOI.png",
	"NELT": "resources/dungeons/DF/NELT.png",
	"NL": "resources/dungeons/DF/NL.png",
	"ULD": "resources/dungeons/DF/ULD.png",
	"UNDR": "resources/dungeons/DF/UNDR.png",
	"VP": "resources/dungeons/DF/VP.png",
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


def gen_score_tt(scores):
	tt = '<table class="tbl_tt" style="border: none;width:unset;margin-left: auto; margin-right: auto;">'
	for k, v in scores.items():
		tt += '<tr style="background-color: unset">'
		icon = f'<img id="roleicon" src=resources/icons/role_{k}.png>'
		tt += f'<td style="text-align: center;">{icon}</td><td style="text-align: left;">&thinsp;{v}</td>'
		tt += '</tr>'
	tt += '</table>'
	return tt


def gen_general_tab(players):
	table_id = uuid.uuid4().hex
	str_html = f'<table id="{table_id}">\n'
	str_html += f'<tr>'
	str_html += f'<th onclick="sortTable(0, \'td_player\', \'{table_id}\')">Player</th>\n'
	str_html += f'<th onclick="sortTable(0, \'td_ilvl\', \'{table_id}\')" class="ilvl">ilvl</th>\n'
	str_html += f'<th>Embellishments</th>\n'
	str_html += f'<th onclick="sortTable(0, \'td_spec\', \'{table_id}\')">Spec</th>'
	str_html += f'<th onclick="sortTable(0, \'td_achiev\', \'{table_id}\')">Achievement Points</th>'
	str_html += f'<th colspan="2">Professions</th>\n'
	str_html += f'</tr>\n'

	for p in players:
		tier = p.get_tier_items()
		embellishments = p.embellishments()
		embellishments_tt = ', '.join(embellishments)
		str_html += f'<tr class="player_row" onclick="highlightRow(this)">\n'
		str_html += f'<td class="td_player" title="Last Update: {p.days_since_last_update()} days ago"><a href="{p.profile_url()}" target="_blank"><img src="{p.thumbnail_url()}" width="35" height="35" style="float:left"></a><p style="color:{p.class_color};padding:5px 0px 0px 3em;margin:0px;text-align:left">{p.name}</p></td>\n'
		str_html += f'<td class="td_ilvl" title="{tier}"><span style="color: {p.class_color}">{p.ilvl}</span></td>\n'
		str_html += f'<td class="td_embellishments" title="{embellishments_tt}">{len(embellishments)}</td>\n'
		str_html += f'<td class="td_spec"><a href="{p.talents_url()}" target="_blank"><img class="spec_icon" title="{p.spec}" src="{p.spec_icon()}"></a></td>\n'
		str_html += f'<td class="td_achiev">{p.achievement_points}</td>\n'
		str_html += f'<td>{p.profession_string(1)}</td><td>{p.profession_string(2)}</td>\n'
		str_html += f'</tr>\n'
	str_html += f'</table>\n'
	return str_html


def gen_score_table(players, inis, colors, isTyrannical):
	table_id = uuid.uuid4().hex
	str_html = f'<table id="{table_id}">\n'
	str_html += f'<tr><th onclick="sortTable(0, \'td_player\', \'{table_id}\')">Player</th>\n'
	str_html += f'<th onclick="sortTable(0, \'td_ilvl\', \'{table_id}\')" class="ilvl">ilvl</th>\n'
	str_html += f'<th onclick="sortTable(0, \'td_score\', \'{table_id}\')" class="score">Score</th>\n'
	for count, x in enumerate(inis):
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
			
		str_html += f'<th onclick="sortTable({count}, \'td_dungeon\', \'{table_id}\')" '\
			f'class="dungeon" style="background-image: url({DUNGEONS_BACKGROUND[x["short"]]})" ' \
			f'title="{x["name"]}{str_keystone_upgrade_timer}">{x["short"]}<br>{ini_timer}</th>\n'
		
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
		str_html += f'<tr class="player_row" onclick="highlightRow(this)">\n'
		str_html += f'<td class="td_player" title="Last Update: {p.days_since_last_update()} days ago&#10;{tier}"><a href="{p.profile_url()}" target="_blank"><img src="{p.thumbnail_url()}" width="35" height="35" style="float:left"></a><p style="font-size:{mainSize}px;color:{p.class_color};padding:5px 0px 0px 3em;margin:0px;text-align:left">{p.name}</p></td>\n'
		str_html += f'<td class="td_ilvl"><span style="color: {p.class_color}">{p.ilvl}</span></td>'
		score = p.score  # Player Score
		score_tt = gen_score_tt(p.relevant_scores())
		color = rio.get_color(colors, score)
		str_html += f'<td class="td_score">' \
					f'<div class="tooltip">' \
					f'<span style="color:{color}">{score:.1f}</span>' \
					f'<span class="tooltiptext">{score_tt}</span>' \
					f'</div>' \
					f'</td>\n'
		#-----------------------------
		for ini in inis:
			# Iterate Instances:
			best, alter = get_instance_from_player(p, ini['short'])
			best.update({'color': rio.get_color(colors, best['score'] * (len(inis)*2), high_score, len(inis))})
			best.update({'sterne': get_sterne(best['upgrade'])})
			alter.update({'color': rio.get_color(colors, alter['score'] * (len(inis)*2), high_score, len(inis))})
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
			ini_score = round(best["score"] * 1.5 + alter["score"] * 0.5, 1)
			str_html += f'<td class="td_dungeon" title="{first["score"]} | {sec["score"]} &Sigma; {ini_score}">' \
						f'<span style="font-size:{mainSize}px;color:{first["color"]}">{first["run"]}</span>' \
						f'<span style="font-size:{mainSize}px;color:yellow">{first["sterne"]}</span>' \
						f'<span style="color:white"> | </span>' \
						f'<span style="font-size:{secSize}px;color:{sec["color"]}">{sec["run"]}</span>' \
						f'<span style="font-size:{secSize}px;color:yellow">{sec["sterne"]}</span>' \
						f'</td>\n'
		str_html += f'</tr>\n'
	str_html += f'</table>\n'
	return str_html


def gen_weekly(players, inis, colors, weekly, runs_dict):
	players = rio.sort_players_by(players,weekly)
	high = rio.get_highest_score(players)
	table_id = uuid.uuid4().hex
	str_html = f'<table id="{table_id}">\n'
	str_html += f'<tr><th onclick="sortTable(0, \'td_player\', \'{table_id}\')">Player</th>'
	str_html += f'<th onclick="sortTable(0, \'td_ilvl\', \'{table_id}\')" class="ilvl">ilvl</th>'
	str_html += f'<th onclick="sortTable(0, \'td_twenty\', \'{table_id}\')" class="twenty">+20</th>'
	str_html += f'<th onclick="sortTable(0, \'td_rewards\', \'{table_id}\')" class="rewards">Rewards</th>'
	for i in range(0,8):
		str_html += f'<th class="runs_weekly"></th>'
	str_html += f'</tr>\n'
	for p in players:
		# ------------ PLAYER and SCORE -----------
		# Count Tier Items an Build a string
		tier = p.get_tier_items()
		# ----------------------------------
		str_html += f'<tr class="player_row" onclick="highlightRow(this)">\n'
		str_html += f'<td class="td_player" title="Last Update: {p.days_since_last_update()} days ago&#10;{tier}"><a href="{p.profile_url()}" target="_blank"><img src="{p.thumbnail_url()}" width="35" height="35" style="float:left"></a><p style="color:{p.class_color};padding:5px 0px 0px 3em;margin:0px;text-align:left;">{p.name}</p></td>\n'
		str_html += f'<td class="td_ilvl"><span style="color: {p.class_color}">{p.ilvl}</span></td>'
		# --------- Show Left Instances -------
		count = 0
		for i in p._data[weekly]:
			if i['mythic_level'] >= len(WREWARD)-1:
				count += 1
		color = 'red'
		if count >= 8:
			color = 'green'
			count = 8
		str_html += f'<td class="td_twenty"><span style="color:{color}">{count-8}</span></td>\n'
		# ---------- 0 / 0 / 0 Rewards -------
		str_html += f'<td class="td_rewards">'
		for i in [0, 3, 7]:
			if i != 0:
				str_html += f' / '
			if len(p._data[weekly]) > i:
				if p._data[weekly][i]['mythic_level'] >= len(WREWARD)-1:
					reward = WREWARD[len(WREWARD)-1]
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
				run_time = dt.strftime('%a %d.%m %H:%M')
				## TODO Maybe we want to Add instance Picture to Weekly runs, too. 
				str_html += f'<td title="Points: {p._data[weekly][i]["score"]}\n{run_time}\n{runs_dict[p._data[weekly][i]["url"]]}"><span style="color:{color}">{p._data[weekly][i]["short_name"]} (<a href="{p._data[weekly][i]["url"]}" style="color:{rio.get_color(colors, p._data[weekly][i]["score"] * (len(inis)*2), high, len(inis))}">{p._data[weekly][i]["mythic_level"]}{stern}</a>)</span></td>\n'
			else:
				str_html += f'<td><span style="color:{color}">-</span></td>\n'
		str_html += '</tr>\n'

	str_html += '</table>\n'
	return str_html


def gen_affixes_html(affixes):
	affixes_html_table = '<table><tr><th class="tbl_affixe" spancol=5 style="font-size: 20px;">Affixes:</th></tr>\n{rows}</table>'

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
		affix_row = "<tr>" + tweek_affixes_out + "\n" + "</tr>"
		return affixes_html_table.format(rows=affix_row)

	nweek_affixes_html = []
	for a in affixes['next_week']:
		if a['id'] != -1:
			affix_html = f'<td class=\"tbl_affixe\"><a class="icontiny" ' \
						 f'data-game="wow" data-type="affix" href="{a["wowhead_url"]}">' \
						 f'<img src="https://wow.zamimg.com/images/wow/icons/tiny/{a["icon"]}.gif" ' \
						 f'style="vertical-align: middle;" loading="lazy">' \
						 f'<span class="tinycontxt"> {a["name"]}</span></a></td>'
		else:
			affix_html = f'<td class="tbl_affixe"><span class"tinycontxt"> {a["name"]}</span></td>'
		nweek_affixes_html.append(affix_html)
	nweek_affixes_out = "<td class=\"tbl_affixe\">Next Week:</td>" + ''.join(nweek_affixes_html)

	affix_rows = "<tr>" + tweek_affixes_out + "\n" + "</tr><tr>" + nweek_affixes_out + "</tr>"
	return affixes_html_table.format(rows=affix_rows)


def gen_site(affixes, all_tables, season_name, season_end, version_string):
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

		myhtml = myhtml.replace('{% season_name %}', season_name)
		myhtml = myhtml.replace('{% now %}', now)
		myhtml = myhtml.replace('{% legend %}', legend)
		myhtml = myhtml.replace('{% affixes %}', affixes_html)
		myhtml = myhtml.replace('{% season_ends %}', season_end)
		
		myhtml = myhtml.replace('{% general_content %}', all_tables['general'])
		myhtml = myhtml.replace('{% main_tracker_content %}', all_tables['main_score'])
		myhtml = myhtml.replace('{% main_weekly_content %}', all_tables['main_weekly'])
		myhtml = myhtml.replace('{% alts_tracker_content %}', all_tables['alts_score'])
		myhtml = myhtml.replace('{% alts_weekly_content %}', all_tables['alts_weekly'])
		myhtml = myhtml.replace('{% main_prev_weekly_content %}', all_tables['main_pweek'])
		myhtml = myhtml.replace('{% alts_prev_weekly_content %}', all_tables['alts_pweek'])
		myhtml = myhtml.replace('{% version_string %}', version_string)

		return myhtml
