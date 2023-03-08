import requests
from datetime import datetime
from bnet import BnetBroker


CLASS_DATA = {
    'Death Knight': {
        'color': '#C41F3B',
        'specs': {
            'Blood': 'https://wow.zamimg.com/images/wow/icons/medium/spell_deathknight_bloodpresence.jpg',
            'Frost': 'https://wow.zamimg.com/images/wow/icons/medium/spell_deathknight_frostpresence.jpg',
            'Unholy': 'https://wow.zamimg.com/images/wow/icons/medium/spell_deathknight_unholypresence.jpg',
        },
    },
    'Demon Hunter': {
        'color': '#A330C9',
        'specs': {
            'Havoc': 'https://wow.zamimg.com/images/wow/icons/medium/ability_demonhunter_specdps.jpg',
            'Vengeance': 'https://wow.zamimg.com/images/wow/icons/medium/ability_demonhunter_spectank.jpg',
        },
    },
    'Druid': {
        'color': '#FF7D0A',
        'specs': {
            'Balance': 'https://wow.zamimg.com/images/wow/icons/medium/spell_nature_starfall.jpg',
            'Feral': 'https://wow.zamimg.com/images/wow/icons/medium/ability_druid_catform.jpg',
            'Guardian': 'https://wow.zamimg.com/images/wow/icons/medium/ability_racial_bearform.jpg',
            'Restoration': 'https://wow.zamimg.com/images/wow/icons/medium/spell_nature_healingtouch.jpg',
        },
    },
    'Evoker': {
        'color': '#33937F',
        'specs': {
            'Devastation': 'https://wow.zamimg.com/images/wow/icons/medium/classicon_evoker_devastation.jpg',
            'Preservation': 'https://wow.zamimg.com/images/wow/icons/medium/classicon_evoker_preservation.jpg',
        },
    },
    'Hunter': {
        'color': '#ABD473',
        'specs': {
            'Beast Mastery': 'https://wow.zamimg.com/images/wow/icons/medium/ability_hunter_bestialdiscipline.jpg',
            'Marksmanship': 'https://wow.zamimg.com/images/wow/icons/medium/ability_hunter_focusedaim.jpg',
            'Survival': 'https://wow.zamimg.com/images/wow/icons/medium/ability_hunter_camouflage.jpg',
        },
    },
    'Mage': {
        'color': '#69CCF0',
        'specs': {
            'Arcane': 'https://wow.zamimg.com/images/wow/icons/medium/spell_holy_magicalsentry.jpg',
            'Fire': 'https://wow.zamimg.com/images/wow/icons/medium/spell_fire_firebolt02.jpg',
            'Frost': 'https://wow.zamimg.com/images/wow/icons/medium/spell_frost_frostbolt02.jpg',
        },
    },
    'Monk': {
        'color': '#00FF96',
        'specs': {
            'Brewmaster': 'https://wow.zamimg.com/images/wow/icons/medium/spell_monk_brewmaster_spec.jpg',
            'Mistweaver': 'https://wow.zamimg.com/images/wow/icons/medium/spell_monk_mistweaver_spec.jpg',
            'Windwalker': 'https://wow.zamimg.com/images/wow/icons/medium/spell_monk_windwalker_spec.jpg',
        },
    },
    'Paladin': {
        'color': '#F58CBA',
        'specs': {
            'Holy': 'https://wow.zamimg.com/images/wow/icons/medium/spell_holy_holybolt.jpg',
            'Protection': 'https://wow.zamimg.com/images/wow/icons/medium/ability_paladin_shieldofthetemplar.jpg',
            'Retribution': 'https://wow.zamimg.com/images/wow/icons/medium/spell_holy_auraoflight.jpg',
        },
    },
    'Priest': {
        'color': '#FFFFFF',
        'specs': {
            'Discipline': 'https://wow.zamimg.com/images/wow/icons/medium/spell_holy_powerwordshield.jpg',
            'Holy': 'https://wow.zamimg.com/images/wow/icons/medium/spell_holy_guardianspirit.jpg',
            'Shadow': 'https://wow.zamimg.com/images/wow/icons/medium/spell_shadow_shadowwordpain.jpg',
        },
    },
    'Rogue': {
        'color': '#FFF569',
        'specs': {
            'Assassination': 'https://wow.zamimg.com/images/wow/icons/medium/ability_rogue_deadlybrew.jpg',
            'Outlaw': 'https://wow.zamimg.com/images/wow/icons/medium/inv_sword_30.jpg',
            'Subtlety': 'https://wow.zamimg.com/images/wow/icons/medium/ability_stealth.jpg',
        },
    },
    'Shaman': {
        'color': '#0070DE',
        'specs': {
            'Elemental': 'https://wow.zamimg.com/images/wow/icons/medium/spell_nature_lightning.jpg',
            'Enhancement': 'https://wow.zamimg.com/images/wow/icons/medium/spell_shaman_improvedstormstrike.jpg',
            'Restoration': 'https://wow.zamimg.com/images/wow/icons/medium/spell_nature_magicimmunity.jpg',
        },
    },
    'Warlock': {
        'color': '#9482C9',
        'specs': {
            'Affliction': 'https://wow.zamimg.com/images/wow/icons/medium/spell_shadow_deathcoil.jpg',
            'Demonology': 'https://wow.zamimg.com/images/wow/icons/medium/spell_shadow_metamorphosis.jpg',
            'Destruction': 'https://wow.zamimg.com/images/wow/icons/medium/spell_shadow_rainoffire.jpg',
        },
    },
    'Warrior': {
        'color': '#C79C6E',
        'specs': {
            'Arms': 'https://wow.zamimg.com/images/wow/icons/medium/ability_warrior_savageblow.jpg',
            'Fury': 'https://wow.zamimg.com/images/wow/icons/medium/ability_warrior_innerrage.jpg',
            'Protection': 'https://wow.zamimg.com/images/wow/icons/medium/ability_warrior_defensivestance.jpg',
        },
    },
}


class Player:
    """Class contains all relevant informations about a player (wow-character)"""

    def __init__(self, response, alt=False, hidden=False):
        self._response = response
        self._data = response.json()

        self._is_alt = alt
        self._is_hidden = hidden

        self._class = self._data['class']

        # Data which is only available via bnet api
        self._realm_slug = None
        self._professions = None
        self.set_up_bnet_data()

    @property
    def name(self):
        return self._data['name']

    @property
    def realm(self):
        return self._data['realm']

    @property
    def realm_slug(self):
        return self._realm_slug

    @property
    def spec(self):
        return self._data['active_spec_name']

    @property
    def ilvl(self):
        return self._data['gear']['item_level_equipped']

    @property
    def score(self):
        return self._data['mythic_plus_scores_by_season'][0]['scores']['all']

    @property
    def achievement_points(self):
        return self._data['achievement_points']

    @property
    def class_color(self):
        return CLASS_DATA[self._class]['color']

    @property
    def professions(self):
        return self._professions

    def profession_string(self, profession_number):
        if profession_number not in [1, 2] or self.professions is None:
            return "-"
        if profession_number - 1 not in range(len(self.professions)):
            return "-"

        profession = self.professions[profession_number - 1]
        profession_string = profession['profession']['name']
        tiers = profession['tiers']
        for t in tiers:
            if 'Dragon' in t['tier']['name']:
                skill_level = f"{t['skill_points']}/{t['max_skill_points']}"
                profession_string += f" ({skill_level})"
        return profession_string

    def mythic_plus_best_runs(self):
        return self._data['mythic_plus_best_runs']

    def mythic_plus_alternate_runs(self):
        return self._data['mythic_plus_alternate_runs']

    def last_crawled_at(self):
        return datetime.strptime(self._data['last_crawled_at'], '%Y-%m-%dT%H:%M:%S.000Z')

    def days_since_last_update(self):
        last_crawled = self.last_crawled_at()
        tday = datetime.now()
        days = (tday - last_crawled).days
        return days

    def relevant_scores(self):
        scores = dict()
        score_dps = self._data['mythic_plus_scores_by_season'][0]['scores']['dps']
        if score_dps > 0:
            scores['dps'] = score_dps
        score_healer = self._data['mythic_plus_scores_by_season'][0]['scores']['healer']
        if score_healer > 0:
            scores['healer'] = score_healer
        score_tank = self._data['mythic_plus_scores_by_season'][0]['scores']['tank']
        if score_tank > 0:
            scores['tank'] = score_tank
        return scores

    def get_tier_items(self):
        tset_pieces = ['head', 'shoulder', 'chest', 'hands', 'legs']
        tset_equiped = [0, 0, 0, 0, 0]
        for i, x in enumerate(tset_pieces):
            if 'tier' in self._data['gear']['items'][x]:
                tset_equiped[i] = int(self._data['gear']['items'][x]['tier'])
        if sum(tset_equiped) == 0:
            return ""
        else:
            tool_tip_per_tier = []
            different_tiers = set(tset_equiped)
            different_tiers.discard(0)
            for tier in different_tiers:
                count = tset_equiped.count(tier)
                pieces = []
                for piece, t in zip(tset_pieces, tset_equiped):
                    if t == tier:
                        pieces.append(piece)
                tool_tip_per_tier.append(f'T{tier}: {count}/5 ({", ".join(pieces)})')
            tool_tip = '\n'.join(tool_tip_per_tier)
            return tool_tip

    def profile_url(self):
        return self._data['profile_url']

    def thumbnail_url(self):
        return self._data['thumbnail_url']

    def spec_icon(self):
        class_ = self._class
        spec = self.spec
        if class_ in CLASS_DATA:
            class_specs = CLASS_DATA[class_]['specs']
            if spec in class_specs:
                return class_specs[spec]
            return ""
        else:
            return ""

    def set_up_bnet_data(self):
        bnet_broker = BnetBroker()
        if not bnet_broker.is_operational():
            return

        realm_index_endpoint = f'/data/wow/realm/index'
        r = bnet_broker.pull(realm_index_endpoint, namespace='dynamic-eu')
        if not r:
            return
        for realm in r['realms']:
            if realm['name'] == self.realm:
                self._realm_slug = realm['slug']

        name_lc = self.name.lower()
        professions_endpoint = f'/profile/wow/character/{self.realm_slug}/{name_lc}/professions'
        r = bnet_broker.pull(professions_endpoint, namespace='profile-eu')
        if r:
            if 'primaries' in r:
                self._professions = r['primaries']

    @staticmethod
    def create_players(player_list, responses):
        if len(player_list) != len(responses):
            print("ERROR: player_list and responses don't have the same length!")
            return []

        players = []
        for p, r in zip(player_list, responses):
            if not r.ok:
                print(f"WARNING: Couldn't get a valid response for player {p['name']}-{p['realm']}:")
                print(f"status-code: {r.status_code}")
                print(f"Reason: {r.reason}")
                print(f"URL: {r.url}")
                try:
                    print(f"Response: {r.json()}")
                except requests.exceptions.JSONDecodeError as e:
                    print(f"Response: {r.text}")
                continue
            player = Player(r, alt=p['is_alt'], hidden=p.get('is_hidden', False))
            players.append(player)
        return players
