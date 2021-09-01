
HOST='https://pub023.cs.technik.fhnw.ch'

URLS{
        'LC':f'{HOST}/request/ql/lightcurves',
        'ELUT':f'{HOST}/request/eluts',
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

