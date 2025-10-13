import requests, colorama, json, webbrowser, os
import sys
from time import sleep
import random as rand

#region init
### get channel from args and exit if they are empt
if len(sys.argv[1:]) == 0:
    print('Usage: randomizer.py [channel ID] --regenerate [Regenerates playlist cache (debug)]` --api [API key] --timeout [number]')
    exit()

# channel arguments
channel = sys.argv[1]
videos = []
seed = int.from_bytes(os.urandom(4))
chunk = 1
api = ''
sleepTime = 1

# find other arguments
for arg in range(len(sys.argv[1:])):
    # regenerate
    if (sys.argv[arg+1] == '--regenerate'):
        try:
            os.remove('playlistCache.json')
        except:
            print(colorama.Fore.BLUE + 'Cache not found. Nothing to do.' + colorama.Fore.WHITE)

    # api key
    if (sys.argv[arg+1] == '--api'):
        try:
            api = sys.argv[arg + 2]
        except:
            print(colorama.Fore.RED + 'Error: You must put in an API key!' + colorama.Fore.RED)
            sys.exit()
    
    # timeout
    if (sys.argv[arg+1] == '--timeout'):
        try:
            # non negative duct tape fix lmao
            if (sleepTime < 0):
                print(colorama.Fore.RED + 'Error: timeout time must be non-negative!' + colorama.Fore.WHITE)
                sys.exit()
            else:
                sleepTime = float(sys.argv[arg + 2])
        except:
            sleepTime = 1


# get api key if not specified
if api == '':
    try:
        with open('API', 'r') as f:
            api = f.read()
    except:
        print(colorama.Fore.RED + 'Error: API key not found. Please specify a key using "--api" or create a file named API with the key inside.' + colorama.Fore.WHITE)
        sys.exit()


# check if channel is in cache
try:
    with open('playlistCache.json', 'r') as f:
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
    # check if request is valid
    if (request.status_code == 403):
        print(colorama.Fore.RED + 'Error: Response was forbidden! Did you put in a correct API key?' + colorama.Fore.WHITE)
    if (request.status_code != 200):
        print(colorama.Fore.red + f'Response failed! Returned with HTTP code {request.status_code}.' + colorama.Fore.WHITE)
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
        videos.extend(playlistJSN['items'])
    else:
        sys.exit()

    # hammer api
    while (nextKey != ''):
        # delay to avoid ratelimiting
        print(colorama.Fore.BLUE + f'Waiting before next request. / Chunk: {chunk}/{round(totalVideos/50)}' + colorama.Fore.WHITE)
        sleep(sleepTime)
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
            videos.extend(playlistJSN['items'])
        else:
            nextKey = ''

    # cache playlist result
    playlistResult = {}
    playlistResult['videos'] = videos
    playlistResult['chID'] = channel

    with open('playlistCache.json', 'w') as f:
        f.write(json.dumps(playlistResult, indent=2))


# pick random api and open result in browser
# to do true random, do seeding lmao
rand.seed = seed
pickedVideo = rand.choice(videos)
pickedVideo = pickedVideo['contentDetails']['videoId']

print(f'Opening browser with video ID {pickedVideo}.')
webbrowser.open(f'https://www.youtube.com/watch?v={pickedVideo}')

#print(f'Debug args, Video ID: {pickedVideo}, Channel ID: {channel}, Random state: {seed}, Total videos: {len(videos)}')