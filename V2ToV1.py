import json
import os

infoNew = json.loads('{}')
debug = True


#list current directory
direcList = os.listdir()

for currentDir in direcList:
    try:
        # region info data stuff
        with open(currentDir + '\Info.dat', 'r') as infoFile:
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
                    audioPath = 'song.ogg',
                    jsonPath = index['_beatmapFilename'].replace('dat', 'json'),
                    offset = index['_noteJumpStartBeatOffset'],
                    oldOffset = index['_noteJumpStartBeatOffset'],
                    customData = {'njs':index['_noteJumpMovementSpeed']}
                ))

        # region note stuff

        # removes noodle extensions/chroma stuff for maps
        def denoodleFunction(mapJSN):
            # removes custom data if found
            if '_customData' in mapJSN:
                mapJSN.pop('_customData')

            # removes chroma events if found
            for i in range(len(mapJSN['_events'])):
                if '_customData' in mapJSN['_events'][i]:
                    mapJSN['_events'][i].pop('_customData')

            amountDeleted = 0
            # removes walls if they have customdata
            for i in range(len(mapJSN['_obstacles'])):
                if '_customData' in mapJSN['_obstacles'][i - amountDeleted]:
                    mapJSN['_obstacles'].pop(i - amountDeleted)
                    amountDeleted +=1

            amountDeleted = 0
            # removes notes that are fake
            # also pops customdata
            for i in range(len(mapJSN['_notes'])):
                if  '_customData' in mapJSN['_notes'][i - amountDeleted]:
                    if '_fake' in mapJSN['_notes'][i - amountDeleted]['_customData']:
                        mapJSN['_notes'].pop(i - amountDeleted)
                        amountDeleted +=1
                    else:
                        # TODO, pop items that go out of the players range
                        mapJSN['_notes'][i - amountDeleted].pop('_customData')
                
            return mapJSN

        #start editing note shit
        for index in diffList:
            with open(currentDir + '\\' + index['jsonPath'].replace('json','dat'),'r') as mapDat:
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
            mapJson = denoodleFunction(mapJson)

            if '_wayPoints' in mapJson:
                mapJson.pop('_wayPoints')

            #saveMap
            with open(currentDir + '\\' + index['jsonPath'],'w') as saveMap:
                saveMap.write(json.dumps(mapJson,indent=2))


        # save info dat file
        for i in range(len(diffList)):
            diffList[i].pop('customData')

        infoNew['difficultyLevels'] = diffList

        with open(currentDir + '\info.json', 'w') as saveJson:
            saveJson.write(json.dumps(infoNew,indent=2))
            saveJson.close()

        # hopefully i dont delete important shit 
        if not(debug):
            if os.path.exists(currentDir + '\\'+ 'Info.dat'):
                os.remove(currentDir + '\\' + 'Info.dat')
            else:
                print('i farted')

            for i in diffList:
                os.remove(currentDir + '\\' + i['jsonPath'].replace('json', 'dat'))

        # rename audio file if possible
        if os.path.exists(currentDir + '\\' +infoOld['_songFilename']):
            os.rename(currentDir + '\\' + infoOld['_songFilename'],currentDir + '\\' + 'song.ogg')

        print('Sucessfully converted ' + currentDir)
    except:
        print('Unable to convert ' + str(currentDir) + '. This may not be a valid map folder or something horribly went wrong')
