import os
import json
import requests
import zipfile
import subprocess
from tqdm import tqdm

URL = "https://ci.86box.net/job/86Box/lastSuccessfulBuild/api/json"
ROMS_URL = "https://github.com/86Box/roms.git"
ASSETS_URL = "https://github.com/86Box/assets.git"
BUILDTYPE = "macOS"
ARCH = "arm64"
ASSETS_PATH = "~/Library/Application Support/86Box"
INCLUDE_ASSETS = True


# get and load request 
print('Pulling latest build from Jenkins...')
buildRequest = requests.get(URL)
artifactJson = buildRequest.json()
print('Jenkins pull complete.')

# determine which version to pull
for artifacts in artifactJson['artifacts']:
    path = artifacts['relativePath']

    if (BUILDTYPE in path) and (ARCH in path):
        finalPath = path
        break

# download the determined version 
# TODO: don't download if hash exists
buildZip = requests.get(f'https://ci.86box.net/job/86Box/lastSuccessfulBuild/artifact/{finalPath}', stream=True)
blockTotal = int(buildZip.headers.get('content-length', 0)) # total file size in bytes

# show progress bar with tqdm
with tqdm(total=blockTotal, unit='B', unit_scale=True, desc='Pulling latest build ') as pb:
    with open('build.zip', 'wb') as f:
        for data in buildZip.iter_content(1024): # 1024 is 1 kibybite
            f.write(data)
            pb.update(len(data))


# unzip build
if (BUILDTYPE != "macOS"):
    with zipfile.ZipFile('build.zip', 'r') as buildZip:
        for member in tqdm(buildZip.infolist(), desc='Extracting build '):
            try:
                buildZip.extract(member, '.')
            except zipfile.error as e:
                pass
else:
    # use native unzip command for mac build target
    subprocess.run(['unzip', '-oq', 'build.zip'])

# remove zip artifact
os.remove('build.zip')

if (ASSETS_PATH != ""):
    os.chdir(os.path.expanduser(ASSETS_PATH))

# github roms stuff
if os.path.isdir('roms'):
    os.chdir('roms')
    subprocess.run(['git', 'pull'])
    os.chdir('..')
else:
    subprocess.run(['git', 'clone', ROMS_URL])


# download assets if requested
if INCLUDE_ASSETS:
    if os.path.isdir('assets'):
        os.chdir('assets')
        subprocess.run(['git', 'pull'])
        os.chdir('..')
    else:
        subprocess.run(['git', 'clone', ASSETS_PATH])
        