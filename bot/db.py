import sqlite3
from config import DB_PATH

# Initialize a database connection in "always open" mode
# for resource efficiency purposes. The connection remains
# alive for the lifetime of the app process.

_conn = None

def get_connection():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False
        )
    return _conn


def get_translation(word, lang_code="en"):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT d.definition, t.lang, t.translation
        FROM words w
        JOIN definitions d ON d.word_id = w.id
        LEFT JOIN translations t ON t.word_id = w.id
        WHERE LOWER(w.word) = ? AND t.lang = ?
    """

    cur.execute(query, (word, lang_code))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return None

    lines = []
    for definition, lang, translation in rows:
        lines.append(translation)
    translations = ", ".join(lines)
#!!! return only values: word, definition, lang. translations
    return f"<b>{word}</b>:\n\n{definition}\n\n<b>{lang}: {translations}</b>"


def get_reverse_translation(word, lang_code="en"):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT w.word, d.definition, t.lang, t.translation
        FROM translations t
        JOIN words w ON w.id = t.word_id
        JOIN definitions d ON d.word_id = w.id
        WHERE t.lang = ?
        AND LOWER(t.translation) = ?
    """

    cur.execute(query, (lang_code, word))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return None

    lines = []
    for word, definition, lang, translation in rows:
        lines.append(f"<b>{word}</b>:\n\n{definition}")
#!!! return only values: word, definition
    return "\n\n".join(lines)
