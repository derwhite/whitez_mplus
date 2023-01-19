
class Player:

    def __init__(self, response, alt=False, hidden=False):
        self._response = response
        self._is_alt = alt
        self._is_hidden = hidden

        j = response.json()

        self._name = j['name']


    @staticmethod
    def create_players(player_list, responses):
        players = []
        for p, r in zip(player_list, responses):
            player = Player(r, alt=False, hidden=p.get('is_hidden', False))
            players.append(player)
        return players
