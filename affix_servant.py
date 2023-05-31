from pathlib import Path
from rio import pull
from bnet import BnetBroker

AFFIX_ROTATION = [
    [9, 124, 6],
    [10, 134, 7],
    [9, 136, 123],
    [10, 135, 6],
    [9, -1, -1],
    [10, -1, -1],
    [9, -1, -1],
    [10, -1, -1],
]


class AffixServant:
    """
    Provides the current affixes.
    This week affixes are pulled from raider.io.
    Next week affixes are only available if a valid bnet token is provided.
    """

    def __init__(self, proxy=''):
        self.proxy = proxy
        self.next_week_affixes_available = False
        self._bnet_broker = BnetBroker()

        rio_current_affixes_url = 'https://raider.io/api/v1/mythic-plus/affixes?region=eu&locale=en'
        responses = pull([rio_current_affixes_url], self.proxy)

        bnet_response = {}
        if self._bnet_broker.is_operational():
            bnet_all_affixes_url = f'/data/wow/keystone-affix/index'
            bnet_response = self._bnet_broker.pull(bnet_all_affixes_url, 'static-eu')
        else:
            print("WARNING: bnet_broker not operational! Affix display will be incomplete.")

        self.current_affixes = []
        if len(responses) >= 0 and responses[0].ok:
            r = responses[0].json()
            self.current_affixes = r['affix_details']
        self._fix_current_affixes()

        self.all_affixes = {}
        if bnet_response:
            r = bnet_response
            for affix in r['affixes']:
                self.all_affixes[affix['id']] = affix['name']
            self.next_week_affixes_available = True

    def get_affixes(self):
        affixes = {
            'this_week': self.get_this_week_affixes(),
            'next_week': self.get_next_week_affixes(),
            'tyrannical': self.is_tyrannical_week()
        }
        return affixes

    def get_this_week_affixes(self):
        return self.current_affixes

    def get_next_week_affixes(self):
        if not self.next_week_affixes_available:
            return None

        next_week_affixes = []
        next_week_affix_ids = self.search_next_affix_week()
        if next_week_affix_ids:
            for affix_id in next_week_affix_ids:
                affix = {}
                if affix_id == -1:
                    unknown_affix = {
                        'id': -1,
                        'name': "???",
                        'description': ""
                    }
                    affix = unknown_affix
                else:
                    affix['id'] = affix_id
                    affix['name'] = self.all_affixes[affix_id]
                    affix['description'] = ""  # TODO: You can get this here: /data/wow/keystone-affix/{keystoneAffixId}
                    affix['icon'] = self.get_affix_icon_name(affix_id)
                    affix['wowhead_url'] = f'https://wowhead.com/affix={affix_id}'
                next_week_affixes.append(affix)
            return next_week_affixes
        return None

    def search_next_affix_week(self):
        current_affix_ids = [affix['id'] for affix in self.current_affixes]
        for i, possible_affix_week in enumerate(AFFIX_ROTATION):
            if possible_affix_week == current_affix_ids:
                return AFFIX_ROTATION[(i+1) % len(AFFIX_ROTATION)]
        return None

    def get_affix_icon_name(self, affix_id):
        if not self._bnet_broker.is_operational():
            return ""
        affix_media_url = f'/data/wow/media/keystone-affix/{affix_id}'
        response = self._bnet_broker.pull(affix_media_url, 'static-eu')
        if response:
            for asset in response['assets']:
                if asset['key'] == 'icon':
                    icon_url = asset['value']
                    # NOTE: this is maybe a little bit hacky
                    p = Path(icon_url)
                    return p.stem
        return ""

    def is_tyrannical_week(self):
        affixes = self.get_this_week_affixes()
        return affixes[0]['id'] == 9

    def _fix_current_affixes(self):
        # Note: fix the affix icons for the raider.io pulled affixes.
        # e.g. they use a different icon for thundering than the official source (bnet)
        if self._bnet_broker.is_operational():
            for a in self.current_affixes:
                a['icon'] = self.get_affix_icon_name(a['id'])
