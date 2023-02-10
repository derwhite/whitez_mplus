from rio import pull


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
    def __init__(self, bnet_token=None, proxy=''):
        urls = []
        rio_current_affixes_url = 'https://raider.io/api/v1/mythic-plus/affixes?region=eu&locale=en'
        urls.append(rio_current_affixes_url)
        if bnet_token:
            bnet_all_affixes_url = f'https://eu.api.blizzard.com/data/wow/keystone-affix/index?namespace=static-eu&locale=en_US&access_token={bnet_token}'
            urls.append(bnet_all_affixes_url)

        responses = pull(urls, proxy)

        self.current_affixes = []
        if len(responses) >= 1 and responses[0].ok:
            r = responses[0].json()
            self.current_affixes = r['affix_details']

        self.all_affixes = {}
        if len(responses) == 2 and responses[1].ok:
            r = responses[1].json()
            for affix in r['affixes']:
                self.all_affixes[affix['id']] = affix['name']
        print("stop")

    def get_this_week_affixes(self):
        return self.current_affixes

    def get_next_week_affixes(self):
        next_week_affixes = []

        next_week_affix_ids = self.search_next_affix_week()
        for affix_id in next_week_affix_ids:
            affix = {}
            affix['id'] = affix_id
            affix['name'] = self.all_affixes[affix_id]
            affix['description'] = ""  # TODO: You can get this here: /data/wow/keystone-affix/{keystoneAffixId}
            affix['icon'] = ""  # TODO: You can (maybe) get this here:  /data/wow/media/keystone-affix/{keystoneAffixId}
            affix['wowhead_url'] = f'https://wowhead.com/affix={affix_id}'
            next_week_affixes.append(affix)
        return next_week_affixes

    def search_next_affix_week(self):
        current_affix_ids = [affix['id'] for affix in self.current_affixes]
        for i, possible_affix_week in enumerate(AFFIX_ROTATION):
            print(i, possible_affix_week)
            if possible_affix_week == current_affix_ids:
                return AFFIX_ROTATION[(i+1) % len(AFFIX_ROTATION)]
        return None
