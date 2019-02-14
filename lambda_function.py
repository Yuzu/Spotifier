import sys
import json
import spotipy
import spotipy.util as util
from datetime import datetime
from datetime import timedelta
from datetime import time
import requests

def lambda_handler(event, context):
    
    bot_token = "" # Telegram bot token.
    chat_id = "" # Chat channel you want the bot to talk in.

    if len(sys.argv) > 1:
        username = sys.argv[1] # User ID = hqn3isgkrwyfzo8d0fv6477t3
    else:
        username = "hqn3isgkrwyfzo8d0fv6477t3"

        
    followScope = "user-follow-read" # Read user's followers. https://developer.spotify.com/documentation/general/guides/scopes/#scopes

    try:
        token = util.prompt_for_user_token(username, scope=followScope)
    except:
        os.remove(".cache--{}".format(username))
        token = util.prompt_for_user_token(username, scope=followScope)

    if token:
        sp = spotipy.Spotify(auth=token)

        user = sp.current_user()

        # count = 0 Debug
        data = {}
        
        page = sp.current_user_followed_artists()
        for artist in page["artists"]["items"]:
            # count += 1
            data.setdefault(str(artist["name"]), artist["uri"])

        nextCursor = page["artists"]["cursors"]["after"]
        while nextCursor != None:

            page = sp.current_user_followed_artists(after=nextCursor)

            for artist in page["artists"]["items"]:
                # count += 1
                data.setdefault(str(artist["name"]), artist["uri"])

            nextCursor = page["artists"]["cursors"]["after"]

       # print("{} artists.".format(count)) # Keep for sake of debugging

        todaysReleases = {}
        
        for artist in data:
            urn = data[artist]

            artistAlbums = sp.artist_albums(urn)

            for album in artistAlbums["items"]:
                if (album["release_date_precision"] != "day"):
                    continue
                
                releaseDate = datetime.strptime(album["release_date"], '%Y-%m-%d').strftime('%Y/%m/%d')
                                                
                utcDate = datetime.utcnow().strftime('%Y/%m/%d')

                if releaseDate == utcDate:
                    todaysReleases.setdefault(artist, [])
                    todaysReleases[artist].append({"albumName": album["name"], "albumURL": album["external_urls"]["spotify"]})

        # print("Done determining releases.") # Maybe keep just for debugging

        message = "Hello! Here's today's updates: \n\n"

        for artist in todaysReleases:
            artistString = ""
            artistString += artist + "\n" + "\n"

            for album in todaysReleases[artist]:
                # print(album)
                
                artistString += album["albumName"] + "\n"
                artistString += album["albumURL"] + "\n" + "\n"

            message += artistString  + "\n" + "==========" + "\n" + "\n"

        if message == "Hello! Here's today's updates: \n\n":
            message = "No updates today."

        requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_token, chat_id, message))

    else:
        print("Invalid token.")
        
    return 'Completed'



