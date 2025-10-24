# bot/bot.py
import os, asyncio
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from storage import storage
from server.telegram_api import send_teacher_snapshot

load_dotenv()
TOKEN = os.environ.get("NOETICA_BOT_TOKEN") or ""
WEBAPP_URL = os.environ.get("WEBAPP_URL") or ""
if not TOKEN:
    raise SystemExit("NOETICA_BOT_TOKEN not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    who = update.effective_user.full_name
    text = (f"Hi {who} — Noētica LMS.\n"
            "Teachers: use /dashboard to open the in-Telegram app, then link your class.\n"
            "Tip: disable bot privacy mode for reply-based submissions.")
    await update.message.reply_text(text)

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not WEBAPP_URL:
        await update.message.reply_text("Mini App URL not configured.")
        return
    kb = [[KeyboardButton(text="Open LMS Dashboard", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text("Open the dashboard:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def init_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("Run this command in your class group.")
        return
    teacher_id = update.effective_user.id
    title = update.effective_chat.title or f"Class {update.effective_chat.id}"
    storage.ensure_teacher(teacher_id, update.effective_user.full_name)
    cls = storage.link_class(update.effective_chat.id, title, teacher_id)
    await update.message.reply_text(f"✅ Class linked: {title}\nUse /dashboard (Mini App) to create assignments.")
    send_teacher_snapshot(teacher_id)

async def reply_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.reply_to_message: return
    if update.effective_chat.type not in ("group","supergroup"): return
    replied_id = msg.reply_to_message.message_id
    group_id = str(update.effective_chat.id)
    # find assignment by posted message id
    found = None
    for a in storage.list_assignments(group_id):
        if a.get("posted_message_id") == replied_id:
            found = a; break
    if not found: return
    # collect file info
    file_meta = None
    if msg.document:
        file = msg.document
        file_meta = {"file_id": file.file_id, "mime": file.mime_type, "size": file.file_size, "local_path": ""}
    elif msg.photo:
        p = msg.photo[-1]
        file_meta = {"file_id": p.file_id, "mime":"image/jpeg", "size": p.file_size, "local_path": ""}
    elif msg.video:
        v = msg.video
        file_meta = {"file_id": v.file_id, "mime": v.mime_type, "size": v.file_size, "local_path": ""}
    sub = storage.add_submission(found["assignment_id"], msg.from_user.id, msg.from_user.full_name, text=(msg.text or ""), file_meta=file_meta, message_id=msg.message_id)
    try:
        await msg.reply_text(f"✅ Submission received for {found['assignment_id']} (ID: {sub['submission_id']}).")
    except Exception:
        pass
    # DM snapshot to teacher
    cls = storage.get_class(int(group_id))
    if cls:
        send_teacher_snapshot(cls["teacher_tg_id"])

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("init_class", init_class))
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), reply_capture))
    print("Bot polling…")
    app.run_polling()

if __name__ == "__main__":
    main()
