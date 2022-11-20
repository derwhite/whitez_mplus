import requests

def create_access_token(client_id, client_secret, region='eu'):
	data = {'grant_type': 'client_credentials'}
	endpoint = 'https://%s.battle.net/oauth/token' % region
	response = requests.post(endpoint, data=data, auth=(client_id,client_secret))
	return response.json()['access_token']

def getBnetAccessToken():
	with open('bnetkeys') as f:
		lines = f.readlines()
		return create_access_token(lines[0].strip(),lines[1].strip())
