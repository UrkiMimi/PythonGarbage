import os
import json
import requests
import zipfile

URL = "https://ci.86box.net/job/86Box/lastSuccessfulBuild/api/json"
ROMS_URL = "https://github.com/86Box/roms.git"
ASSETS_URL = "https://github.com/86Box/assets.git"
BUILDTYPE = "Windows"
COMPILER = "Old"
INCLUDE_ASSETS = True


# get and load request 
buildRequest = requests.get(URL)
artifactJson = buildRequest.json()


# determine which version to pull
for artifacts in artifactJson['artifacts']:
    path = artifacts['relativePath']

    if (BUILDTYPE in path) and (COMPILER in path):
        finalPath = path
        break

# download the determined version 
# TODO: don't download if hash exists
print('Pulling latest build...')
with open('build.zip', 'wb') as f:
    buildZip = requests.get(f'https://ci.86box.net/job/86Box/lastSuccessfulBuild/artifact/{finalPath}')
    f.write(buildZip.content)


# unzip build
print('Unzipping...')
with zipfile.ZipFile('build.zip', 'r') as buildZip:
    buildZip.extractall('.')

# remove zip artifact
os.remove('build.zip')


# github roms stuff
if os.path.isdir('roms'):
    os.chdir('roms')
    os.system('git pull')
    os.chdir('..')
else:
    os.system(f'git clone {ROMS_URL}')


# download assets if requested
if INCLUDE_ASSETS:
    if os.path.isdir('assets'):
        os.chdir('assets')
        os.system('git pull')
        os.chdir('..')
    else:
        os.system(f'git clone {ASSETS_URL}')