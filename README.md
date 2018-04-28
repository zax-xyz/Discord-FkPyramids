[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# DiscordFkPyramids
The initial main purpose of this bot was to automatically block pyramids after the third message. 

## Dependencies
- Python 3.6+
- `discord.py` 1.0.0a (for stable release, see [master](https://github.com/zaxutic/Discord-FkPyramids/tree/master/) branch)
- `aiohttp` library
- `websockets` library

## Installation
```
$ git clone -b rewrite --single-branch https://github.com/zaxutic/Discord-FkPyramids.git
$ cd Discord-FkPyramids
```

## Setup 
- Clone or download this repository into a directory.
- On line 9 of `FkPyramids.py`, replace `135678905028706304` with your user ID (NOT the bot's ID). Refer to the [Discord Support Article](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-) if unsure. This will be used to issue commands to the bot.
- Create a `token.txt` file and write your bot's authentication token to this file.

## Running
### Windows
```
$ python FkPyramids.py
```
### Linux/Mac OS X
```
$ python3 FkPyramids.py
```
## License
This project is licensed under the GNU General Public License v3.0. See [LICENSE](https://github.com/zaxutic/Discord-FkPyramids/tree/rewrite/LICENSE) for more information.
