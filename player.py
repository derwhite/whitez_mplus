CLASS_COLOR = {
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


class Player:
    """Class contains all relevant informations about a player (wow-character)"""

    def __init__(self, response, alt=False, hidden=False):
        self._response = response
        self._data = response.json()

        self._is_alt = alt
        self._is_hidden = hidden

        self._class = self._data['class']
        self._score = self._data['mythic_plus_scores_by_season'][0]['scores']['all']

    @property
    def name(self):
        return self._data['name']

    @property
    def ilvl(self):
        return self._data['gear']['item_level_equipped']

    @property
    def class_color(self):
        return CLASS_COLOR[self._data['class']]

    def mythic_plus_best_runs(self):
        return self._data['mythic_plus_best_runs']

    def mythic_plus_alternate_runs(self):
        return self._data['mythic_plus_alternate_runs']

    def last_crawled_at(self):
        return self._data['last_crawled_at']

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

    @staticmethod
    def create_players(player_list, responses):
        players = []
        for p, r in zip(player_list, responses):
            player = Player(r, alt=p['is_alt'], hidden=p.get('is_hidden', False))
            players.append(player)
        return players
