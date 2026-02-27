'''
These statements allow us to make get requests of the Airtable API & parse that information
'''
import requests # you may need to run 'pip install requests' to install this library
import json 


''' This function makes a get request to the airtable API which will tell us how fast to spin the wheels'''

''' Put the URL for your Airtable Base here'''
''' Format: 'https://api.airtable.com/v0/BaseID/tableName '''
URL = 'Sbeav'


''' Format: {'Authorization':'Bearer Access_Token'}
Note that you need to leave "Bearer" before the access token '''
Headers = {'Authorization':'Bearer patUQ3nF5wWjGlMRb.361191ea73cbd06bfa25a7cf0e309dcf82ee4cfb52bfe83877a2b0e0d9f4877b'}

r = requests.get(url = URL, headers = Headers, params = {})
'''
The get request data comes in as a json package. We will convert this json package to a python dictionary so that it can be parsed
'''
data = r.json()
print(data)