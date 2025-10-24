# server/app.py
import os, hmac, hashlib, urllib.parse
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from storage import storage
from server.telegram_api import (post_assignment_to_group, edit_message_text,
                                 send_teacher_snapshot, send_reminder)
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

load_dotenv()
BOT_TOKEN = os.environ.get("NOETICA_BOT_TOKEN") or ""
WEBAPP_URL = os.environ.get("WEBAPP_URL") or ""
DEV_SKIP = (os.environ.get("DEV_SKIP_INITDATA_VALIDATION","").lower() == "true")

app = FastAPI(title="Noetica LMS (file DB)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Telegram WebApp initData validation (simplified) ---
def validate_init_data(init_data: str) -> dict:
    """
    DEV: if DEV_SKIP=true, accept without signature.
    In production: implement per Telegram docs (HMAC SHA256, 'hash' field).
    """
    try:
        parsed = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        raise HTTPException(401, "Invalid initData format")
    if DEV_SKIP:
        return parsed
    # TODO: Implement strict HMAC validation here per Telegram docs.
    # For now, require user field to exist.
    if "user" not in parsed:
        raise HTTPException(401, "Missing user in initData")
    return parsed

# --- Schemas ---
class LinkClassPayload(BaseModel):
    group_chat_id: int
    group_title: str

class CreateAssignmentPayload(BaseModel):
    class_id: str
    title: str
    instructions_md: Optional[str] = ""
    due_at: Optional[str] = None

class UpdateAssignmentPayload(BaseModel):
    title: Optional[str]=None
    instructions_md: Optional[str]=None
    due_at: Optional[str]=None
    status: Optional[str]=None  # "open"|"closed"

# --- Dependency to get user id from initData header ---
def current_user_id(init_data: Optional[str] = None):
    # Frontend will send header "x-telegram-init-data"
    from fastapi import Request
    def dep(request: Request):
        hdr = request.headers.get("x-telegram-init-data", "")
        parsed = validate_init_data(hdr)
        # user id is inside 'user' JSON (when strict); in DEV we accept absent.
        # To keep dev moving, allow override with x-dev-user-id
        dev_uid = request.headers.get("x-dev-user-id")
        if dev_uid:
            return int(dev_uid)
        if "user" in parsed:
            import json as _json
            u = _json.loads(parsed["user"])
            return int(u["id"])
        raise HTTPException(401, "No user in initData (DEV: set DEV_SKIP_INITDATA_VALIDATION=true or x-dev-user-id)")
    return dep

@app.get("/api/health")
def health():
    return {"ok": True}

# --- Teacher: link class to group ---
@app.post("/api/classes/link")
def link_class(payload: LinkClassPayload, user_id: int = Depends(current_user_id())):
    storage.ensure_teacher(user_id, name=f"tg:{user_id}")
    cls = storage.link_class(payload.group_chat_id, payload.group_title, user_id)
    send_teacher_snapshot(user_id)
    return cls

# --- Teacher: create assignment (posts to group) ---
@app.post("/api/assignments")
def create_assignment(payload: CreateAssignmentPayload, user_id: int = Depends(current_user_id())):
    cls = storage.get_class(int(payload.class_id))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    a = storage.create_assignment(payload.class_id, payload.title, payload.instructions_md or "", payload.due_at)
    msg_id = post_assignment_to_group(int(payload.class_id), a["assignment_id"], a["title"], a["due_at"], a["instructions_md"])
    storage.set_assignment_message_id(a["assignment_id"], msg_id)
    send_teacher_snapshot(user_id)
    return storage.get_assignment(a["assignment_id"])

# --- Teacher: list assignments ---
@app.get("/api/assignments")
def list_assignments(class_id: str, user_id: int = Depends(current_user_id())):
    cls = storage.get_class(int(class_id))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    return storage.list_assignments(class_id)

# --- Teacher: update assignment (edit message if needed) ---
@app.patch("/api/assignments/{assignment_id}")
def update_assignment(assignment_id: str, payload: UpdateAssignmentPayload, user_id: int = Depends(current_user_id())):
    a = storage.get_assignment(assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")
    cls = storage.get_class(int(a["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    updated = storage.update_assignment(assignment_id, **payload.model_dump(exclude_none=True))
    # reflect edits in the group message if title/instructions/due changed
    if updated and updated.get("posted_message_id"):
        lines = [f"📌 *Assignment* — *{updated['assignment_id']}*", f"*{updated['title']}*"]
        if updated.get("due_at"): lines.append(f"🗓 Due: {updated['due_at']}")
        if updated.get("instructions_md"): lines.append(f"\n{updated['instructions_md']}")
        lines.append("\nReply to *this message* with your document/file.")
        text = "\n".join(lines)
        try:
            edit_message_text(int(updated["class_id"]), int(updated["posted_message_id"]), text, parse_mode="Markdown")
        except Exception as e:
            print("Edit failed:", e)
    send_teacher_snapshot(user_id)
    return updated

# --- Teacher: view submissions (read-only) ---
@app.get("/api/assignments/{assignment_id}/submissions")
def list_submissions(assignment_id: str, user_id: int = Depends(current_user_id())):
    a = storage.get_assignment(assignment_id)
    if not a: raise HTTPException(404, "Assignment not found")
    cls = storage.get_class(int(a["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    return storage.list_submissions(assignment_id)

# --- Teacher: reminder ---
@app.post("/api/assignments/{assignment_id}/remind")
def remind(assignment_id: str, user_id: int = Depends(current_user_id())):
    a = storage.get_assignment(assignment_id)
    if not a: raise HTTPException(404, "Assignment not found")
    cls = storage.get_class(int(a["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    send_reminder(int(a["class_id"]), a["assignment_id"], a["title"], a["due_at"])
    send_teacher_snapshot(user_id)
    return {"ok": True}

# --- Teacher: export CSV (server writes file; bot can DM, or just returns path) ---
@app.post("/api/assignments/{assignment_id}/export_csv")
def export_csv(assignment_id: str, user_id: int = Depends(current_user_id())):
    a = storage.get_assignment(assignment_id)
    if not a: raise HTTPException(404, "Assignment not found")
    cls = storage.get_class(int(a["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    path = storage.export_submissions_csv(assignment_id)
    # For simplicity, just return the file path (bot can DM separately if desired)
    return {"csv_path": path}


ROOT_DIR = Path(__file__).resolve().parents[1]
MINIAPP_DIR = ROOT_DIR / "miniapp"

if not MINIAPP_DIR.exists():
    raise RuntimeError(f"Mini App directory not found at: {MINIAPP_DIR}")

# Serve /miniapp/* and also let /miniapp render index.html by default
app.mount(
    "/miniapp",
    StaticFiles(directory=str(MINIAPP_DIR), html=True),
    name="miniapp",
)