import requests, colorama, json, webbrowser, os
import sys
from time import sleep
import random as rand

#region init
### get channel from args and exit if they are empt
if len(sys.argv[1:]) == 0:
    print('usage thing')
    exit()

# channel arguments
channel = sys.argv[1]
videos = []
seed = os.urandom(8)
chunk = 1

# get api key
with open('API', 'r') as f:
    api = f.read()

# check if channel is in cache
try:
    with open('playlistCache', 'r') as f:
        tmp = json.loads(f.read())

        newChannel = True
        
        # set newchannel to true if channel id is the same
        if ('chID' in tmp):
            if (tmp['chID'] == channel):
                newChannel = False
                
                videos = tmp['videos']
except:
    newChannel = True


#region requests
# get channel and playlist id
# also skip this entirely if the same channel is reused
if newChannel:
    request = requests.get(f'https://www.googleapis.com/youtube/v3/channels?part=statistics,contentDetails&id={channel}&key={api}')
    print(f'https://www.googleapis.com/youtube/v3/channels?part=statistics,contentDetails&id={channel}&key={api}')
    # check if request is valid
    if (request.status_code != 200):
        print(f'Response failed! Returned with HTTP code {request.status_code}.')
        sys.exit()

    # set total videos and uploadid
    uploadsID = request.json()['items'][0]['contentDetails']['relatedPlaylists']['uploads'] # gets the channel uploads playlist
    totalVideos = request.json()['items'][0]['statistics']['videoCount']
    totalVideos = int(totalVideos)


    #region ### playlists
    #get playlist
    request = requests.get(f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploadsID}&maxResults=50&key={api}')

    # continue
    if (request.status_code == 200):
        chunk +=1
        playlistJSN = request.json()

        if ('nextPageToken' in playlistJSN):
            nextKey = playlistJSN['nextPageToken']
        else:
            nextKey = ''
        
        # add result to video array
        videos.append(playlistJSN['items'])
    else:
        sys.exit()

    # hammer api
    while (nextKey != ''):
        # delay to avoid ratelimiting
        print(f'Waiting a second before next request. / Chunk: {chunk}/{round(totalVideos/50)}')
        sleep(1)
        chunk+=1
        request = requests.get(f'https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={uploadsID}&maxResults=50&key={api}&pageToken={nextKey}')

        # continue
        if (request.status_code == 200):
            playlistJSN = request.json()

            if ('nextPageToken' in playlistJSN):
                nextKey = playlistJSN['nextPageToken']
            else:
                nextKey = ''
            
            # add result to video array
            videos.append(playlistJSN['items'])
        else:
            nextKey = ''

    # cache playlist result
    playlistResult = {}
    playlistResult['videos'] = videos
    playlistResult['chID'] = channel

    with open('playlistCache', 'w') as f:
        f.write(json.dumps(playlistResult))


# pick random api and open result in browser
# to do true random, do seeding lmao
rand.seed = seed
pickedVideo = rand.choice(videos[0])
pickedVideo = pickedVideo['contentDetails']['videoId']
print(pickedVideo)

print('Opening browser for selected video')
webbrowser.open(f'https://www.youtube.com/watch?v={pickedVideo}')

print(f'Debug args, Video ID: {pickedVideo}, Channel ID: {channel}, Random state: {seed}')