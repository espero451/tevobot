CREATE TABLE words (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL
);

CREATE INDEX idx_words_word ON words(word);

CREATE TABLE definitions (
    id INTEGER PRIMARY KEY,
    word_id INTEGER NOT NULL,
    definition TEXT,
    FOREIGN KEY(word_id) REFERENCES words(id)
);

CREATE TABLE translations (
    id INTEGER PRIMARY KEY,
    word_id INTEGER NOT NULL,
    lang TEXT NOT NULL,
    "translation" TEXT,
    UNIQUE(word_id, lang, translation)
    FOREIGN KEY(word_id) REFERENCES words(id)
);

CREATE INDEX idx_translations_word_lang ON translations(word_id, lang);
