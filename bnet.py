import requests


class Singleton(type):
	# TODO: only create a singleton if Broker is_operational / bnet_token is set
	# otherwise this happens:
	# bb = BnetBroker()
	# bb.is_operational()  # => False
	# bb2 = BnetBroker(settings['client_id'], settings['client_secret'])
	# bb2.is_operational()  # => False, because singleton was already created

	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class BnetBroker(metaclass=Singleton):

	def __init__(self, client_id='', client_secret=''):
		self._region = 'eu'
		self._locale = 'en_US'
		self._url_prefix = f'https://{self.region}.api.blizzard.com'

		self._bnet_token = BnetBroker._create_access_token(client_id, client_secret, self.region)

	@property
	def bnet_token(self):
		return self._bnet_token

	@property
	def region(self):
		return self._region

	@property
	def locale(self):
		return self._locale

	def is_operational(self):
		return self.bnet_token is not None

	def pull(self, endpoint, namespace):
		if not self.is_operational:
			return {}

		query_parameters = f'?namespace={namespace}&locale={self.locale}&access_token={self.bnet_token}'
		url = self._url_prefix + endpoint + query_parameters

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
			print("WARNING: No valid bnet client_id / client_secret set. Bnet API requests won't be available!")
			return None
