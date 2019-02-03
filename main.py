import sys
import os
import json
import webbrowser
import spotipy
import spotipy.util as util
from datetime import datetime
from datetime import timedelta
from datetime import time

if len(sys.argv) > 1:
    username = sys.argv[1] # User ID = hqn3isgkrwyfzo8d0fv6477t3
else:
    username = "hqn3isgkrwyfzo8d0fv6477t3"

    
followScope = "user-follow-read"

try:
    token = util.prompt_for_user_token(username, scope=followScope)
except:
    os.remove(".cache--{}".format(username))
    token = util.prompt_for_user_token(username, scope=followScope)


if token:
    sp = spotipy.Spotify(auth=token)

    user = sp.current_user()
    #print(json.dumps(user, sort_keys=True, indent=2))

    with open("followedArtists.json", "w") as f:


        # can take everything below outside of open

        count = 0
        data = {}
        
        page = sp.current_user_followed_artists()
        for artist in page["artists"]["items"]:
            #print(artist["name"])
            count += 1
            data.setdefault(str([artist["name"]]), artist["uri"])

        nextCursor = page["artists"]["cursors"]["after"]
        while nextCursor != None:

            page = sp.current_user_followed_artists(after=nextCursor)

            for artist in page["artists"]["items"]:
                #print(artist["name"])
                count += 1
                data.setdefault(str([artist["name"]]), artist["uri"])

            nextCursor = page["artists"]["cursors"]["after"]

        json.dump(data, f, indent=4) 
        print("{} artists.".format(count))

        todaysReleases = {}
        
        for artist in data:
            urn = data[artist]

            artistAlbums = sp.artist_albums(urn)

            #with open("current.json", "w") as f:
                #json.dump(artistAlbums, f, indent=4)


            for album in artistAlbums["items"]:
                if (album["release_date_precision"] != "day"):
                    continue
                
                releaseDate = datetime.strptime(album["release_date"], '%Y-%m-%d').strftime('%Y/%m/%d')
                                                
                utcDate = datetime.utcnow().strftime('%Y/%m/%d')

                
                if (releaseDate != utcDate):
                    todaysReleases.setdefault(str(artist), [])
                    todaysReleases[str(artist)].append({"name": str(album["name"]), "link": str(album["external_urls"]["spotify"])})
            
        with open("releases.json", "w") as f:
            json.dump(todaysReleases, f, indent=4)
            
        print("done")
    
else:
    print("Invalid token.")
    

