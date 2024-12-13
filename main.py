import json
import os

infoNew = json.loads('{}')

# region info data stuff
with open('Info.dat', 'r') as infoFile:
    infoOld = json.loads(infoFile.read())

# import info data over
infoNew['songName'] = infoOld['_songName']
infoNew['songSubName'] = infoOld['_songSubName']
infoNew['authorName'] = infoOld['_songAuthorName']
infoNew['beatsPerMinute'] = infoOld['_beatsPerMinute']
infoNew['previewStartTime'] = infoOld['_previewStartTime']
infoNew['previewDuration'] = infoOld['_previewDuration']
infoNew['coverImagePath'] = infoOld['_coverImageFilename']
infoNew['environmentName'] = infoOld['_environmentName']


# specify diffList
diffList = []

# generate new diff set for new json
for index in infoOld['_difficultyBeatmapSets'][0]['_difficultyBeatmaps']:
    diffList.append(dict(
            difficulty = index['_difficulty'],
            difficultyRank = index['_difficultyRank'],
            audioPath = infoOld['_songFilename'].replace('egg','ogg'),
            jsonPath = index['_beatmapFilename'].replace('dat', 'json'),
            offset = index['_noteJumpStartBeatOffset'],
            oldOffset = 0,
            customData = {'njs':index['_noteJumpMovementSpeed']}
        ))

# region note stuff
#start editing note shit
for index in diffList:
    with open(index['jsonPath'].replace('json','dat'),'r') as mapDat:
        mapJson = json.loads(mapDat.read())
        mapDat.close()
    
    #mandatory json shit
    mapJson['_version'] = '1.5.0'
    mapJson['_beatsPerMinute'] = infoOld['_beatsPerMinute']
    mapJson['_noteJumpSpeed'] = index['customData']['njs']
    mapJson['_beatsPerBar'] = 16
    mapJson['_shuffle'] = 0
    mapJson['_shufflePeriod'] = 0.5
    
    #for 0.11.2 compat
    if '_customData' in mapJson:
        mapJson.pop('_customData')

    if '_wayPoints' in mapJson:
        mapJson.pop('_wayPoints')

    #saveMap
    with open(index['jsonPath'],'w') as saveMap:
        saveMap.write(json.dumps(mapJson,indent=2))


# save info dat file
for i in range(len(diffList)):
    diffList[i].pop('customData')

infoNew['difficultyLevels'] = diffList

with open('info.json', 'w') as saveJson:
    saveJson.write(json.dumps(infoNew,indent=2))
    saveJson.close()

# hopefully i dont delete important shit 
if os.path.exists('Info.dat'):
    os.remove('Info.dat')
else:
    print('i farted')

for i in diffList:
    os.remove(i['jsonPath'].replace('json', 'dat'))

# rename audio file if possible
if os.path.exists(infoOld['_songFilename']):
    os.rename(infoOld['_songFilename'],'song.ogg')
