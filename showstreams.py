import sys
import json
import os
from workflow import Workflow3, web

OMDB_API_URL = 'http://www.omdbapi.com/'
IMDB_URL = 'http://imdb.com/'
ROTTEN_TOMATOES_SEARCH_URL = 'http://rottentomatoes.com/search/?search='

def main(wf):
    streams = os.environ['streamoptions']

    imdbId = search_omdb_info(os.environ['movie'],os.environ['year'],os.environ['type'])
    omdb_info = get_omdb_info(imdbId)
    if omdb_info['Response'] == 'False':
        wf.add_item(title='Ratings details not found.')
    else:
        #omdb_info = omdb_info['Search'][1]
        search_url = IMDB_URL + 'title/' + str(omdb_info['imdbID'])
        if omdb_info['imdbRating'] != 'N/A':
            wf.add_item(title=omdb_info['imdbRating'],
                        subtitle='IMDb (' + omdb_info['imdbVotes'] + " votes)",
                        icon='img/imdb.png',
                        valid=True,
                        arg=search_url,
                        copytext=omdb_info['imdbID'])

        #Rotten Tomatoes
        if omdb_info['tomatoMeter'] != 'N/A':
            tomatoIcon = 'img/fresh.png'
            if omdb_info['tomatoImage'] == 'N/A':
                tomatoIcon = 'img/noidea.png'
            else:
                tomatoIcon = 'img/' + omdb_info['tomatoImage'] + '.png'

            wf.add_item(title=omdb_info['tomatoMeter'] + '%',
                        subtitle='Rotten Tomatoes (' + omdb_info['tomatoReviews'] + ' reviews, ' + omdb_info['tomatoFresh'] + ' fresh, ' + omdb_info['tomatoRotten'] + ' rotten)',
                        icon=tomatoIcon,
                        valid=False
                        )
        else:
            for rating in omdb_info['Ratings']:
                if rating['Source'] == 'Rotten Tomatoes':
                    wf.add_item(title=rating['Value'],
                                subtitle='Rotten Tomatoes',
                                icon='img/fresh.png',
                                valid=False)

        if omdb_info['tomatoUserMeter'] != 'N/A':
            tomatoUserIcon = 'img/rtliked.png'
            if int(omdb_info['tomatoUserMeter']) < 60:
                tomatoUserIcon = 'img/rtdisliked.png'

            wf.add_item(title=omdb_info['tomatoUserMeter'] + '%',
                        subtitle='Rotten Tomatoes Audience Score (' + omdb_info['tomatoUserReviews'] + ' reviews, ' + omdb_info['tomatoUserRating'] + ' avg rating)',
                        icon=tomatoUserIcon,
                        valid=True)


    convertJsonToItems(wf,json.loads(streams))

    wf.send_feedback()

def convertJsonToItems(wf,streams):
    for s in streams:
        wf.add_item(
            title=s['title'],
            subtitle=s['subtitle'],
            arg=s['arg'],
            icon=s['icon'],
            valid=True
        )

def search_omdb_info(movie,year,type):
    url = OMDB_API_URL
    params = dict(s=movie, y=year, type=type, apikey=os.environ['omdb_api_key'])
    response = web.get(url, params).json()
    imdbId = -1
    if response['Response'] == 'True':
        imdbId = response['Search'][0]['imdbID']

    return imdbId

def get_omdb_info(imdbId):
    url = OMDB_API_URL
    params = dict(i=imdbId, tomatoes=True, apikey=os.environ['omdb_api_key'])
    return web.get(url, params).json()

if __name__ == "__main__":
    wf = Workflow3()
    log = wf.logger
    sys.exit(wf.run(main))
