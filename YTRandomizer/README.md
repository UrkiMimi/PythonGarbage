# YoutubeRandomizer
A hacked together script that lets you get random videos from somebody's channel! Channel IDs are only supported.

### Arguments
- Channel ID (First argument): The YouTube channel ID you're going to grab videos from. Must be the first argument
- API `--api`: The YouTube V3 API key. Alternatively, you can make put the API key in a file called `API`
- Regenerate `--regenerate`: Regenerates the playlist cache.
- API timeout `--timeout`: Wait time in seconds before next request if needed. Defaults to one second.

**Example**
```bash
python randomizer.py UCoFUO4AixQfs-_oXbmbMqag --regenerate --api [key] --timeout 4
```
