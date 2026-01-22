# TeVo: Telegrama Vortaro

Esperanto dictionary Telegram bot based on the [Reta Vortaro](https://github.com/revuloj) project database.


## Features

- Search for words in the dictionary and display definition and usage examples in Esperanto.
- Accept words in different forms (plural, accusative, past/future tense) and automatically normalize them to the base form (singular noun or infinitive verb).
- Invert dictionary direction (From → To).
- Multilingual support.


## Build the Database

1. Download the latest `revoxdxf_YYYY-MM-DD.zip` from [revo-fonto](https://github.com/revuloj/revo-fonto/releases) and unpack it.
2. In `./tools/xdxf_parser.py`, configure the following variables:
```
INPUT_XDXF = "/path/to/revo.xdxf"   # path to unpacked .xdxf file
OUTPUT_DB = "tevo.db"            # desired output database name
```
3. Run the parser:
```
python3 xdxf_parser.py
```
The database will be created in `./data/` folder.


## Deployment

poetry:
```bash
git clone https://github.com/espero451/tevobot
cd tevobot
poetry install --no-root
poetry run python3 bot/bot.py
```

venv:
```bash
git clone https://github.com/espero451/tevobot
cd tevobot
python3 -m venv ./venv
. ./venv/bin/activate
pip install -r requirements.txt
python3 -m tevobot
```


## Config

1. Create `./bot/TOKEN.py` file and add variable with your bot token from BodFather:
```python
TOKEN = "YOUR_TOKEN_HERE"
```
*`TOKEN.py` is already listed in `.gitignore`, so it will not be committed. Make sure never to share it publicly.*


## Bot Commands
```
/starto     : Check if the bot alive
/lingvo     : Set the dictionary language
/statuso    : Show current dictionary status (default: Esperanto → En)
/inversigi  : Invert dictionary languages
```


## TODO

- Add cx, ux, sx, gx, hx auto input transformations.
