import requests





class Singleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class BnetBroker(metaclass=Singleton):

	def __init__(self, client_id='', client_secret=''):
		self._bnet_token = BnetBroker._create_access_token(client_id, client_secret)

	@property
	def bnet_token(self):
		return self._bnet_token

	def pull(self):
		realmSlug = 'nathrezim'
		characterName = 'käseknacker'
		url = f'https://eu.api.blizzard.com/profile/wow/character/{realmSlug}/{characterName}/professions?namespace=profile-eu&locale=en_US&access_token={self.bnet_token}'
		r = requests.get(url)
		if r.ok:
			return r.json()
		else:
			return {}

	@staticmethod
	def _create_access_token(client_id, client_secret, region='eu'):
		data = {'grant_type': 'client_credentials'}
		endpoint = f'https://{region}.battle.net/oauth/token'
		response = requests.post(endpoint, data=data, auth=(client_id, client_secret))
		if response.status_code == 200:
			return response.json()['access_token']
		else:
			print("WARNING: No valid bnet client_id / client_secret set. Bnet API requests woun't be available!")
			return None
