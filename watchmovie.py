import requests
import sys
import json
import re
from workflow import Workflow3

presentation = ["hd", "4k"]

def main(wf):

    query = (wf.args[0]).replace(" ","+")
    try:
        response = get_justwatch_info(query)
    except Exception, e:
        wf.add_item('Uh oh... something went wrong',
            subtitle='Please check your internet connection.')
        wf.send_feedback()
        return 0
    if 'status_code' in response:
        wf.add_item(title='Nothing was found.')
    else:
        if not response.json()['items']:
            wf.add_item(title='Nothing was found.')
        for r in response.json()['items']:
            if 'offers' in r:
                newItems = formatJsonItems(r['offers'])
            iconPath = ""
            type = ""
            if r['object_type'] == 'show':
                iconPath = 'img/tv.png'
                type = 'series'
            else:
                iconPath = 'img/filmicon.png'
                type = 'movie'
            id = r['id']
            r = wf.add_item(
                title=r['title'],
                subtitle="Released "+str(r['original_release_year']),
                arg=r['title'],
                valid=True,
                autocomplete=r['title'],
                icon=iconPath
            )
            wf.setvar('streamoptions',json.dumps(newItems))
            wf.setvar('movie',r['title'])
            wf.setvar('year',r['original_release_year'])
            wf.setvar('type',type)
            #wf.setvar("stream-"+str(id)],json.dumps(newItems))
            # log.debug(json.dumps(newItems))
            # r.setvar('streamoptions',json.dumps(newItems))

    wf.send_feedback()

# def main(wf):
#     #myProviders = wf.args[1]
#     providers = getProviders()
#     movie = (wf.args[0]).replace(" ","+")
#     justWatchUrl = "https://apis.justwatch.com/content/titles/en_US/popular?language=en&body=%7B%22page_size%22:5,%22page%22:1,%22query%22:%22"+movie+"%22,%22content_types%22:[%22show%22,%22movie%22]%7D"
#
#     payload = ""
#     headers = {
#         'cache-control': "no-cache",
#         }
#
#     response = requests.request("GET", justWatchUrl, data=payload, headers=headers)
#
#     #omdbResponse
#
#     data = {}
#     data['items'] = []
#
#     for r in response.json()['items']:
#         streams = {}
#         streams['items'] = []
#         index = 0
#         if 'offers' in r:
#             for o in r['offers']:
#                 if o['monetization_type'] == "flatrate" and o['presentation_type'] in presentation:
#                     providerIds = [prov['id'] for prov in providers]
#                     if o['provider_id'] in providerIds:
#                         provInfo = getProviderById(providers,o['provider_id'])
#                         stream = {
#                             'uid': o['provider_id'],
#                             'title': provInfo['name'],
#                             'subtitle': "Quality "+o['presentation_type'].upper(),
#                             'arg': o['urls']['standard_web'],
#                             'valid': "true",
#                             'icon': {
#                                 'path': provInfo['iconpath']
#                             },
#                             'text': {
#                                 'copy': o['urls']['standard_web']
#                             }
#                         }
#                         streams['items'].append(stream)
#                 index = index+1
#
#         iconPath = ""
#         if r['object_type'] == 'show':
#             iconPath = 'img/tv.png'
#         else:
#             iconPath = 'img/filmicon.png'
#         val = {
#             'uid': r['title'],
#             'title': r['title'],
#             'subtitle': "Released "+str(r['original_release_year']),
#             'arg': "Streams to watch!",
#             'valid': "true",
#             'autocomplete': r['title'],
#             'icon': {
#                 'path': iconPath
#             },
#             'variables': {
#                 'streamoptions': json.dumps(streams)
#             }
#         }
#         data['items'].append(val)
#
#     print json.dumps(data)

def formatJsonItems(streams):
    items = []
    providers = getProviders()
    for s in streams:
        if s['monetization_type'] == "flatrate" and s['presentation_type'] in presentation:
            providerIds = [prov['id'] for prov in providers]
            if s['provider_id'] in providerIds:
                provInfo = getProviderById(providers,s['provider_id'])
                stream = {
                    'uid': s['provider_id'],
                    'title': provInfo['name'],
                    'subtitle': "Quality "+s['presentation_type'].upper(),
                    'arg': s['urls']['standard_web'],
                    'valid': "true",
                    'icon': provInfo['iconpath'],
                    'text': {
                        'copy': s['urls']['standard_web']
                    }
                }
                items.append(stream)
    return items

def getProviders():
    return [
        {
            'name': "Disney Plus",
            'id': 337,
            'iconpath': 'img/disneyplus.png'
        },
        {
            'name': "Netflix",
            'id': 8,
            'iconpath': 'img/netflix.png'
        },
        {
            'name': "Amazon Prime",
            'id': 9,
            'iconpath': 'img/amazonprime.png'
        },
        {
            'name': "HBO Max",
            'id': 384,
            'iconpath': 'img/hbomax.png'
        },
        {
            'name': "Hulu",
            'id': 15,
            'iconpath': 'img/hulu.png'
        }
    ]

def getProviderById(providers, value):
    idx = None
    for i, d in enumerate(providers):
        if d.get('id', None) == value:
            idx = i
    if idx is None:
        return {
            'name': "Not Found",
            'iconpath': 'img/noidea.png'
        }
    else:
        return providers[idx]

def get_omdb_info(imdb_id):
    url = 'http://www.omdbapi.com/'
    params = dict(i=imdb_id, tomatoes=True, apikey=os.environ['omdb_api_key'])
    return web.get(url, params).json()

def get_justwatch_info(movie):
    justWatchUrl = "https://apis.justwatch.com/content/titles/en_US/popular?language=en&body=%7B%22page_size%22:5,%22page%22:1,%22query%22:%22"+movie+"%22,%22content_types%22:[%22show%22,%22movie%22]%7D"
    headers = {
        'cache-control': "no-cache",
        }
    return requests.request("GET", justWatchUrl, data="", headers=headers)


if __name__ == "__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
