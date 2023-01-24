import requests


def create_access_token(client_id, client_secret, region='eu'):
	data = {'grant_type': 'client_credentials'}
	endpoint = f'https://{region}.battle.net/oauth/token'
	response = requests.post(endpoint, data=data, auth=(client_id, client_secret))
	if response.status_code == 200:
		return response.json()['access_token']
	else:
		print("WARNING: No valid bnet client_id / client_secret set. Bnet API requests woun't be available!")
		return None
