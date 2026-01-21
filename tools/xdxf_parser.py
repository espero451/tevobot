import sqlite3
import xml.etree.ElementTree as ET
from conf_update import update_variable


INPUT_XDXF = "../data/revo.xdxf"
OUTPUT_DB = "../data/tevo.db"
SCHEMA_SQL = "../bot/schema.sql"
CONFIG_FILE = "../bot/config.py"


# Create DB
conn = sqlite3.connect(OUTPUT_DB)
with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
    sql_script = f.read()
conn.executescript(sql_script)

cur = conn.cursor()

# Parse XDXF
tree = ET.parse(INPUT_XDXF)
root = tree.getroot()
lexicon = root.find("lexicon")

# <dtrn> tags parsing function
def process_dtrn(parent_tag, translations_dict):
    for dtrn_tag in parent_tag.findall("dtrn"):
        if dtrn_tag.text:
            parts = dtrn_tag.text.strip().split(" ", 1)
            if len(parts) == 2:
                lang = parts[0].strip("/").lower()
                translation = parts[1].strip()
                for part in translation.split(","):
                    part = part.strip()
                    if part:
                        translations_dict.setdefault(lang, []).append(part)


for ar_tag in lexicon.findall("ar"):

    # <k>: word
    word = ar_tag.find("k").text.lower().strip()
    cur.execute("INSERT INTO words (word) VALUES (?)", (word,))
    word_id = cur.lastrowid

    # <def>: definition
    def_tags = []
    for def_tag in ar_tag.findall("def"):

        def_parts = []
        if def_tag.text and def_tag.text.strip():
            def_parts.append(def_tag.text)

        for child in def_tag:
            if child.tag in {"dtrn", "ex", "sr"}: # ignore
                continue
            else:
                def_text = "".join(child.itertext())
                if child.tail:
                    def_text += child.tail
                def_parts.append(def_text)

        definition_main = "".join(def_parts).strip()

        # <ex>: examples
        ex_parts = []
        for ex_tag in def_tag.findall("ex"):
            ex_text = "".join(ex_tag.itertext()).strip()
            if ex_text:
                ex_parts.append(ex_text)
        # add \n between definition and examples
        if ex_parts:
            definition_text = definition_main + "\n\n" + "\n".join(ex_parts)
        else:
            definition_text = definition_main

        def_tags.append(definition_text)

    final_definition = "\n\n".join(def_tags)

    cur.execute(
        "INSERT INTO definitions (word_id, definition) VALUES (?, ?)",
        (word_id, final_definition),
    )

    # <dtrn>: translation
    translations_dict = {}
    for def_tag in ar_tag.findall("def"):
        process_dtrn(def_tag, translations_dict) # <dtrn> inside <def>
    process_dtrn(ar_tag, translations_dict) # <dtrn> outside <def>

    rows = []
    for lang, translations in translations_dict.items():
        for translation in translations:
            rows.append((word_id, lang, translation))

    cur.executemany(
        "INSERT OR IGNORE INTO translations (word_id, lang, translation) VALUES (?, ?, ?)", rows,
    )

conn.commit()

# Write SUPPORTED_LANGUAGES -> config.py
cur.execute("SELECT lang FROM translations")
languages = cur.fetchall()
languages_set = sorted({row[0] for row in languages})
update_variable(CONFIG_FILE, "SUPPORTED_LANGUAGES", languages_set)
print(f"Config '{CONFIG_FILE}' updated.")
print(f"DB '{OUTPUT_DB}' created.")

conn.close()
