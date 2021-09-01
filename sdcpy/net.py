import requests
HOST='https://pub023.cs.technik.fhnw.ch'
HOST='http://localhost:5000'

URLS={
        'LC':f'{HOST}/api/request/ql/lightcurves',
        'ELUT':f'{HOST}/api/request/eluts',
    }

def fetch_light_curves(begin_utc, end_utc, ltc):
    form = {
         'begin': begin_utc,
         'ltc':ltc,
         'end':end_utc
        }
    url=URLS['LC']
    response = requests.post(url, data = form)
    data=response.json()
    if 'error' in data:
        raise FileNotFoundError
        return None
    return data

def fetch_onboard_and_true_eluts(utc):
    form = {
         'utc': utc
        }
    url=URLS['ELUT']
    response = requests.post(url, data = form)
    data=response.json()
    if 'error' in data:
        raise FileNotFoundError
        return None
    return data

