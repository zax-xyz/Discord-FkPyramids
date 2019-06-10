[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# DiscordFkPyramids
Discord bot designed to automatically block pyramids after the third message, with other features/functionality.

NOTE: Although it was the original entire purpose of the bot, the pyramid blocking functionally has since been removed. Yes, I know the name of the bot doesn't make sense anymore. No, I probably won't change it :)

## Dependencies
- Python 3.6+
- just look at requirements.txt for everything else

## Setup 
- Create an `auth.py` file in `config` and assign your bot's authentication (OAuth) token to a `token` variable as a string in this file.
- Optionally create a virtual environment with `python -m venv venv` and activate it with `source venv/bin/activate`. If this command doesn't work on your machine, Google it or PR a better README for me :)
- Install dependencies with `pip install -U -r requirements.txt`

## Running
### Windows
```
$ py -3 FkPyramids.py
```
### Linux/Mac OS X
```
$ python3 FkPyramids.py
```
## License
This project is licensed under the GNU General Public License v3.0. See [LICENSE](https://github.com/zaxutic/Discord-FkPyramids/tree/rewrite/LICENSE) for more information.
