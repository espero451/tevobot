# TeVo: Telegrama Vortaro

Esperanto dictionary Telegram bot based on the [Reta Vortaro](https://github.com/revuloj) project database.


## Features

- Search Esperanto words with definitions.


## Build the Database

1. Download the latest revoxdxf_YYYY-MM-DD.zip from [revo-fonto](https://github.com/revuloj/revo-fonto/releases) and unpack it.
2. In ./tools/xdxf_parser.py, configure the following variables:
INPUT_XDXF = "/path/to/revo.xdxf"   # path to your xdxf file
OUTPUT_DB = "tevobot.db"            # desired output database name
3. Run the parser:
```cd tools/
python3 xdxf_parser.py```
The database will be generated in the ./data/ folder.

Execute:
```bash
cd tools/
python3 xdxf_parser.py
```
The database will be created in ./data/ folder.


## Deployment

venv:
```bash
git clone https://github.com/espero451/tevobot
cd tevobot
python3 -m venv ./venv
. ./venv/bin/activate
pip install -r requirements.txt
python3 -m tevobot
```
poetry:
```bash
git clone https://github.com/espero451/tevobot
cd tevobot
poetry install --no-root
poetry run python3 bot/bot.py
```


## Bot Commands
```
/starto     : Check if the bot alive
/lingvo     : Set the dictionary language
/statuso    : Show current dictionary status (default: Esperanto → En)
/inversigi  : Invert dictionary languages
```
