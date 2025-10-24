# server/telegram_api.py
import os, requests
from typing import Optional
from storage.storage import build_snapshot_text

BOT_TOKEN = os.environ.get("NOETICA_BOT_TOKEN") or ""
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

def _post(method: str, **payload):
    url = f"{API_BASE}/{method}"
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data["result"]

def send_message(chat_id: int, text: str, parse_mode: Optional[str] = None, reply_markup: Optional[dict]=None):
    return _post("sendMessage", chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup)

def pin_message(chat_id: int, message_id: int, silent: bool=True):
    try:
        return _post("pinChatMessage", chat_id=chat_id, message_id=message_id, disable_notification=silent)
    except Exception:
        return None

def edit_message_text(chat_id: int, message_id: int, text: str, parse_mode: Optional[str]=None, reply_markup: Optional[dict]=None):
    return _post("editMessageText", chat_id=chat_id, message_id=message_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup)

def post_assignment_to_group(group_chat_id: int, assignment_id: str, title: str, due_at: Optional[str], instructions_md: str):
    lines = [f"📌 *Assignment* — *{assignment_id}*", f"*{title}*"]
    if due_at: lines.append(f"🗓 Due: {due_at}")
    if instructions_md: lines.append(f"\n{instructions_md}")
    lines.append(f"\nReply to *this message* with your document/file.")
    text = "\n".join(lines)
    res = send_message(group_chat_id, text, parse_mode="Markdown", reply_markup={
        "inline_keyboard":[
            [{"text":"View details","callback_data":f"view:{assignment_id}"}],
        ]
    })
    pin_message(group_chat_id, res["message_id"])
    return res["message_id"]

def send_teacher_snapshot(teacher_tg_id: int):
    text = build_snapshot_text()
    try:
        m = send_message(teacher_tg_id, text)
        try:
            pin_message(teacher_tg_id, m["message_id"])
        except Exception:
            pass
    except Exception as e:
        print("Snapshot send failed:", e)

def send_reminder(group_chat_id: int, assignment_id: str, title: str, due_at: Optional[str]):
    text = f"⏰ Reminder: *{title}* (ID: {assignment_id})"
    if due_at: text += f"\nDue: {due_at}"
    return send_message(group_chat_id, text, parse_mode="Markdown")