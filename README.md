# DiscordFkPyramids
The original main purpose of this bot was to automatically block pyramids after the third message. 

## Requirements
- Python 3.6+
- `discord.py` 1.0.0a (for stable release, see [master](https://github.com/zaxutic/Discord-FkPyramids/tree/master/) branch)
- `aiohttp` library
- `websockets` library

## Setup 
- Clone or download this repository into a directory.
- On line 9 of `FkPyramids.py`, replace `135678905028706304` with your user ID (NOT the bot's ID). Refer to the [Discord Support Article](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) to find this. This will be used to issue commands to the bot.
- In the directory, create a `token.txt` file and write your bot's token to this file. This will be used to authenticate your bot with the servers.

## Running
`python3 FkPyramids.py`
