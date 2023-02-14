from rio import pull
from pathlib import Path

AFFIX_ROTATION = [
    [9, 7, 3, 132],
    [10, 6, 14, 132],
    [9, 11, 12, 132],
    [10, 8, 3, 132],
    [9, 6, 124, 132],
    [10, 123, 12, 132],
    [9, 8, 13, 132],
    [10, 7, 124, 132],
    [9, 123, 14, 132],
    [10, 11, 13, 132],
]


class AffixServant:
    """
    Provides the current affixes.
    This week affixes are pulled from raider.io.
    Next week affixes are only available if a valid bnet token is provided.
    """

    def __init__(self, bnet_token=None, proxy=''):
        self.bnet_token = bnet_token
        self.proxy = proxy
        self.next_week_affixes_available = False

        urls = []
        rio_current_affixes_url = 'https://raider.io/api/v1/mythic-plus/affixes?region=eu&locale=en'
        urls.append(rio_current_affixes_url)
        if self.bnet_token:
            bnet_all_affixes_url = f'https://eu.api.blizzard.com/data/wow/keystone-affix/index?namespace=static-eu&locale=en_US&access_token={self.bnet_token}'
            urls.append(bnet_all_affixes_url)

        responses = pull(urls, self.proxy)

        self.current_affixes = []
        if len(responses) >= 1 and responses[0].ok:
            r = responses[0].json()
            self.current_affixes = r['affix_details']

        self.all_affixes = {}
        if len(responses) == 2 and responses[1].ok:
            r = responses[1].json()
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
        for affix_id in next_week_affix_ids:
            affix = {}
            affix['id'] = affix_id
            affix['name'] = self.all_affixes[affix_id]
            affix['description'] = ""  # TODO: You can get this here: /data/wow/keystone-affix/{keystoneAffixId}
            affix['icon'] = self.get_affix_icon_name(affix_id)
            affix['wowhead_url'] = f'https://wowhead.com/affix={affix_id}'
            next_week_affixes.append(affix)
        return next_week_affixes

    def search_next_affix_week(self):
        current_affix_ids = [affix['id'] for affix in self.current_affixes]
        for i, possible_affix_week in enumerate(AFFIX_ROTATION):
            if possible_affix_week == current_affix_ids:
                return AFFIX_ROTATION[(i+1) % len(AFFIX_ROTATION)]
        return None

    def get_affix_icon_name(self, affix_id):
        if self.bnet_token is None:
            return ""
        affix_media_url = f'https://us.api.blizzard.com/data/wow/media/keystone-affix/{affix_id}?namespace=static-us&locale=en_US&access_token={self.bnet_token}'
        responses = pull([affix_media_url], self.proxy)
        if len(responses) == 1 and responses[0].ok:
            r = responses[0].json()
            for asset in r['assets']:
                if asset['key'] == 'icon':
                    icon_url = asset['value']
                    # NOTE: this is maybe a little bit hacky
                    p = Path(icon_url)
                    return p.stem
        return ""

    def is_tyrannical_week(self):
        affixes = self.get_this_week_affixes()
        return affixes[0]['id'] == 9
