import requests
HOST='https://pub023.cs.technik.fhnw.ch'
#HOST='http://localhost:5000'
URLS={
        'LC':f'{HOST}/api/request/ql/lightcurves',
        'ELUT':f'{HOST}/api/request/eluts',
        'EMPHERIS':f'{HOST}/api/request/ephemeris',
        'SCIENCE':f'{HOST}/api/request/science-data/id',
    }
def post(url, form):
    response = requests.post(url, data = form)

    data=response.json()
    if 'error' in data:
        print(data['error'])
        return None
    return data



def fetch_light_curves(begin_utc:str, end_utc:str, ltc:bool):
    form = {
         'begin': begin_utc,
         'ltc':ltc,
         'end':end_utc
        }
    url=URLS['LC']
    return post(url,form)
def fetch_onboard_and_true_eluts(utc):
    form = {
         'utc': utc
        }
    url=URLS['ELUT']
    return post(url,form)

def fetch_empheris(start_utc:str, end_utc:str, steps=1):
    return post(URLS['EMPHERIS'],{
         'start_utc': start_utc,
         'end_utc': end_utc,
         'steps':steps
        })

def fetch_science_data(_id:int):
    return post(URLS['SCIENCE'],{
         'id': _id,
        })

