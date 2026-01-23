from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    BotCommandScopeDefault,
    BotCommandScopeAllPrivateChats
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    PicklePersistence
)
from datetime import datetime
import time
from collections import defaultdict, deque

import db
from config import TOKEN, SUPPORTED_LANGUAGES, PKL_PATH, LOG_PATH, LOG_ACTIVE, WINDOW, LIMIT
from esperanto import esperanto


persistence = PicklePersistence(filepath=PKL_PATH)

# flood protection
user_requests = defaultdict(deque)

def is_allowed(user_id):
    now = time.time()
    q = user_requests[user_id]
    while q and q[0] < now - WINDOW:
        q.popleft()
    if len(q) >= LIMIT:
        return False
    q.append(now)
    return True


def main():
    app = ApplicationBuilder().token(TOKEN).persistence(persistence).build()

    app.post_init = setup_commands

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("starto", start))
    app.add_handler(CommandHandler("lingvo", choose_language))
    app.add_handler(CommandHandler("inversigi", reverse_switch))
    app.add_handler(CommandHandler("statuso", status))
    app.add_handler(CallbackQueryHandler(set_language))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))

    # Run
    app.run_polling()


# Commands
async def setup_commands(app):
    commands = [
        BotCommand("starto", "🚀 Starto"),
        BotCommand("lingvo", "🌐 Lingvo"),
        BotCommand("statuso", "ℹ️ Statuso"),
        BotCommand("inversigi", "🔄 Inversigi"),
    ]
    await app.bot.set_my_commands(
        commands,
        scope=BotCommandScopeDefault()
    )
    await app.bot.set_my_commands(
        commands,
        scope=BotCommandScopeAllPrivateChats()
    )


# /starto handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "lang_code" not in context.user_data:
        context.user_data["lang_code"] = detect_lang(update)

    lang_code = context.user_data.get("lang_code")
    context.user_data["reverse"] = False
    status = build_status(context)

    welcome_text = f"Saluton! Mi estas vortaro boto. Sendu vorton, kaj mi resendos la difino.\n\n<b>Reĝimo:</b> {status}"

    await update.message.reply_text(welcome_text, parse_mode="HTML")


# /lingvo handlers
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data  # get language from callback_data
    context.user_data["lang_code"] = lang_code
    status = build_status(context)

    await query.edit_message_text(status, parse_mode="HTML")

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Elektu lingvon:", reply_markup=lang_keyboard())

# Default language detection
def detect_lang(update: Update) -> str:
    code = update.effective_user.language_code
    if not code:
        return "en"
    base = code.split("-")[0]  # en-US -> en
    return base if base in SUPPORTED_LANGUAGES else "en"

# Language keyboard
def lang_keyboard():
    buttons = []
    row = []
    for i, lang in enumerate(SUPPORTED_LANGUAGES, 1):
        row.append(InlineKeyboardButton(lang.title(), callback_data=lang))
        if i % 6 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)


# /inversigi handler (reverse ON/OFF)
async def reverse_switch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = context.user_data.get("reverse", False)
    context.user_data["reverse"] = toggle(current)
    status = build_status(context)

    await update.message.reply_text(status, parse_mode="HTML")

def toggle(value: bool) -> bool:
    return not value


# /statuso handler
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = build_status(context)
    await update.message.reply_text(status, parse_mode="HTML")

def build_status(context: ContextTypes.DEFAULT_TYPE):
    lang_code = (context.user_data.get("lang_code", "en"))
    reverse = context.user_data.get("reverse", False)

    if reverse:
        mode = lang_code.title() + " → Esperanto"
    else:
        mode = "Esperanto → " + lang_code.title()

    return f"<b>{mode}</b>"


# Vocabulary, translation
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # protection: flood
    user_id = update.message.from_user.id
    if not is_allowed(user_id):
        await update.message.reply_text("Kara amiko, vi tro ofte sendas mesaĝojn, bonvolu malrapidigi.")
        return

    word = update.message.text.strip()

    # protection: input length
    if len(word) > 30:
        await update.message.reply_text("Kara amiko, pardonu, sed mi ne konas tiom longajn vortojn...")
        return

    word = esperanto(word.lower())

    lang_code = context.user_data.get("lang_code", "en")
    reverse = context.user_data.get("reverse")
    
    if LOG_ACTIVE:
        log_input(user_id, word)

    if reverse:
        request = db.get_reverse_translation(word, lang_code)
    else:
        request = db.get_translation(word, lang_code)

    if not request:
        await update.message.reply_text("Kara amiko, pardonu, mi ne povas trovi ĉi tiun vorton...")
        return

    if reverse:
        result = "\n\n".join(request)
    else:
        result = f"<b>{request['word']}</b>:\n\n{request['definition']}\n\n<b>{lang_code}: {request['translations']}</b>"

    for chunk in split_message(result):
        await update.message.reply_text(chunk, parse_mode="HTML")


# Message length limiter
def split_message(text: str, limit: int = 4000):
    for i in range(0, len(text), limit):
        yield text[i:i + limit]


# Log writer (debugger)
# Turn it ON or OFF by LOG_ACTIVE var in config.py file
def log_input(user_id: int, text: str):
    timestamp = datetime.now().isoformat(timespec="seconds")
    print(timestamp, user_id, text)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}\t{user_id}\t{text}\n")


if __name__ == "__main__":
    main()
