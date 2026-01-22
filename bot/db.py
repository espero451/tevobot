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
        SELECT d.definition, t.translation
        FROM words w
        JOIN definitions d ON d.word_id = w.id
        LEFT JOIN translations t ON t.word_id = w.id AND t.lang = ?
        WHERE LOWER(w.word) = ?
    """

    cur.execute(query, (lang_code, word))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return None

    definition = rows[0][0]
    lines = [t for _, t in rows if t is not None]
    translations = ", ".join(lines) if lines else "🤷"

    # return [word, definition, translations]

    return {
        "word": word,
        "definition": definition,
        "translations": translations
    }


def get_reverse_translation(word, lang_code="en"):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT w.word, d.definition
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
    for word, definition in rows:
        lines.append(f"<b>{word}</b>:\n\n{definition}")

    return lines
