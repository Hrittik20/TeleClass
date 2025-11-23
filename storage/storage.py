from __future__ import annotations
import json, os, time, threading, tempfile, shutil, csv, uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_PATH = os.path.join(DATA_DIR, "data.json")
FILES_DIR = os.path.join(DATA_DIR, "files")
os.makedirs(FILES_DIR, exist_ok=True)

_lock = threading.Lock()

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _ensure_file():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "meta": {"version": 1, "last_updated": _now_iso()},
                "teachers": {}, "students": {}, "classes": {}, "assignments": {}, 
                "submissions": {}, "enrollments": {}, "events": []
            }, f, ensure_ascii=False, indent=2)

def load() -> Dict[str, Any]:
    _ensure_file()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _atomic_write(obj: Dict[str, Any]):
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="data_", suffix=".json", dir=DATA_DIR)
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.flush(); os.fsync(f.fileno())
        shutil.move(tmp_path, DATA_PATH)
    finally:
        try: os.remove(tmp_path)
        except FileNotFoundError: pass

def save(mutate_fn):
    with _lock:
        data = load()
        res = mutate_fn(data)
        data["meta"]["last_updated"] = _now_iso()
        _atomic_write(data)
        return res

def make_assignment_id() -> str:
    return "A" + str(int(time.time()))

def make_submission_id() -> str:
    return "S" + str(int(time.time()*1000))

def make_course_code() -> str:
    """Generate a unique course code for enrollment"""
    return str(uuid.uuid4())[:8].upper()

# --- TEACHERS ---
def ensure_teacher(tg_user_id: int, name: str) -> Dict[str, Any]:
    def mut(d):
        key = str(tg_user_id)
        if key not in d["teachers"]:
            d["teachers"][key] = {"tg_user_id": tg_user_id, "name": name, "created_at": _now_iso()}
            d["events"].append({"id": f"E{time.time_ns()}", "type":"teacher_created","actor":tg_user_id,"payload":{"name":name},"ts":_now_iso()})
        return d["teachers"][key]
    return save(mut)

# --- STUDENTS ---
def ensure_student(tg_user_id: int, name: str = None) -> Dict[str, Any]:
    def mut(d):
        key = str(tg_user_id)
        if key not in d["students"]:
            student_name = name or f"Student {tg_user_id}"
            d["students"][key] = {"tg_user_id": tg_user_id, "name": student_name, "created_at": _now_iso()}
            d["events"].append({"id": f"E{time.time_ns()}", "type":"student_created","actor":tg_user_id,"payload":{"name":student_name},"ts":_now_iso()})
        return d["students"][key]
    return save(mut)

def get_student(tg_user_id: int) -> Optional[Dict[str, Any]]:
    return load()["students"].get(str(tg_user_id))

# --- CLASSES ---
def link_class(group_chat_id: int, group_title: str, teacher_tg_id: int) -> Dict[str, Any]:
    def mut(d):
        gid = str(group_chat_id)
        # Generate a unique course code for enrollment
        course_code = make_course_code()
        d["classes"][gid] = {
            "class_id": gid, 
            "title": group_title, 
            "teacher_tg_id": teacher_tg_id, 
            "course_code": course_code,
            "created_at": _now_iso()
        }
        d["events"].append({"id": f"E{time.time_ns()}","type":"class_linked","actor":teacher_tg_id,
                            "payload":{"group_chat_id":group_chat_id,"title":group_title},"ts":_now_iso()})
        return d["classes"][gid]
    return save(mut)

def get_class(group_chat_id: int) -> Optional[Dict[str, Any]]:
    return load()["classes"].get(str(group_chat_id))

def get_course_by_code(course_code: str) -> Optional[Dict[str, Any]]:
    """Find a class by its enrollment code"""
    for cls in load()["classes"].values():
        if cls.get("course_code") == course_code:
            return cls
    return None

# --- ENROLLMENTS ---
def enroll_student(student_tg_id: int, class_id: str) -> Dict[str, Any]:
    """Enroll a student in a class"""
    def mut(d):
        # Create a unique enrollment ID
        enrollment_id = f"E{student_tg_id}_{class_id}"
        
        # Check if already enrolled
        if enrollment_id in d["enrollments"]:
            return d["enrollments"][enrollment_id]
        
        # Create enrollment record
        d["enrollments"][enrollment_id] = {
            "enrollment_id": enrollment_id,
            "student_tg_id": student_tg_id,
            "class_id": class_id,
            "enrolled_at": _now_iso()
        }
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "student_enrolled",
            "actor": student_tg_id,
            "payload": {"class_id": class_id},
            "ts": _now_iso()
        })
        
        return d["enrollments"][enrollment_id]
    return save(mut)

def is_student_enrolled(student_tg_id: int, class_id: str) -> bool:
    """Check if a student is enrolled in a class"""
    enrollment_id = f"E{student_tg_id}_{class_id}"
    return enrollment_id in load()["enrollments"]

def get_student_courses(student_tg_id: int) -> List[Dict[str, Any]]:
    """Get all courses a student is enrolled in"""
    data = load()
    enrollments = [e for e in data["enrollments"].values() if e["student_tg_id"] == student_tg_id]
    
    result = []
    for enrollment in enrollments:
        class_id = enrollment["class_id"]
        if class_id in data["classes"]:
            cls = data["classes"][class_id]
            # Get teacher name
            teacher_name = "Unknown"
            if str(cls["teacher_tg_id"]) in data["teachers"]:
                teacher_name = data["teachers"][str(cls["teacher_tg_id"])]["name"]
            
            result.append({
                "course_id": class_id,
                "title": cls["title"],
                "teacher_tg_id": cls["teacher_tg_id"],
                "teacher_name": teacher_name,
                "enrolled_at": enrollment["enrolled_at"]
            })
    
    return result

# --- ASSIGNMENTS ---
def create_assignment(class_id: str, title: str, instructions_md: str, due_at: Optional[str]) -> Dict[str, Any]:
    aid = make_assignment_id()
    def mut(d):
        d["assignments"][aid] = {
            "assignment_id": aid, "class_id": class_id, "title": title,
            "instructions_md": instructions_md or "", "due_at": due_at,
            "posted_message_id": None, "status":"open", "created_at": _now_iso(), "updated_at": _now_iso()
        }
        d["events"].append({"id": f"E{time.time_ns()}","type":"assignment_created","actor":d["classes"][class_id]["teacher_tg_id"],
                            "payload":{"assignment_id":aid}, "ts":_now_iso()})
        return d["assignments"][aid]
    return save(mut)

def set_assignment_message_id(assignment_id: str, msg_id: int):
    def mut(d):
        if assignment_id in d["assignments"]:
            d["assignments"][assignment_id]["posted_message_id"] = msg_id
            d["assignments"][assignment_id]["updated_at"] = _now_iso()
        return True
    return save(mut)

def list_assignments(class_id: str) -> List[Dict[str, Any]]:
    return [a for a in load()["assignments"].values() if a["class_id"] == class_id]

def list_course_assignments(class_id: str) -> List[Dict[str, Any]]:
    """Alias for list_assignments to maintain consistent naming"""
    return list_assignments(class_id)

def get_assignment(aid: str) -> Optional[Dict[str, Any]]:
    return load()["assignments"].get(aid)

def update_assignment(aid: str, **updates) -> Optional[Dict[str, Any]]:
    def mut(d):
        if aid not in d["assignments"]:
            return None
        d["assignments"][aid].update({k:v for k,v in updates.items() if v is not None})
        d["assignments"][aid]["updated_at"] = _now_iso()
        d["events"].append({"id": f"E{time.time_ns()}","type":"assignment_updated",
                            "actor": d["classes"][d["assignments"][aid]["class_id"]]["teacher_tg_id"],
                            "payload":{"assignment_id":aid,"updates":list(updates.keys())}, "ts":_now_iso()})
        return d["assignments"][aid]
    return save(mut)

# --- SUBMISSIONS ---
def add_submission(assignment_id: str, student_tg_id: int, student_name: str,
                   text: str = "", file_meta: Optional[Dict[str, Any]] = None, message_id: Optional[int]=None) -> Dict[str, Any]:
    sid = make_submission_id()
    def mut(d):
        late = False
        due = d["assignments"].get(assignment_id, {}).get("due_at")
        if due:
            try:
                late = datetime.fromisoformat(_now_iso().replace("Z","")).replace(tzinfo=None) > datetime.fromisoformat(due.replace("Z","")).replace(tzinfo=None)
            except Exception:
                late = False
        d["submissions"][sid] = {
            "submission_id": sid, "assignment_id": assignment_id, "student_tg_id": student_tg_id,
            "student_name": student_name, "ts": _now_iso(), "late": late,
            "text": text, "file": file_meta, "message_id": message_id
        }
        d["events"].append({"id": f"E{time.time_ns()}","type":"submission_added","actor":student_tg_id,
                            "payload":{"assignment_id":assignment_id,"submission_id":sid}, "ts":_now_iso()})
        return d["submissions"][sid]
    return save(mut)

def list_submissions(assignment_id: str) -> List[Dict[str, Any]]:
    return [s for s in load()["submissions"].values() if s["assignment_id"] == assignment_id]

def has_student_submitted(assignment_id: str, student_tg_id: int) -> bool:
    """Check if a student has submitted an assignment"""
    return any(s["student_tg_id"] == student_tg_id for s in list_submissions(assignment_id))

def get_student_submission(assignment_id: str, student_tg_id: int) -> Optional[Dict[str, Any]]:
    """Get a student's submission for an assignment"""
    submissions = [s for s in list_submissions(assignment_id) if s["student_tg_id"] == student_tg_id]
    if submissions:
        # Return the most recent submission if multiple exist
        return max(submissions, key=lambda s: s["ts"])
    return None

def export_submissions_csv(assignment_id: str) -> str:
    rows = list_submissions(assignment_id)
    out_path = os.path.join(FILES_DIR, f"export_{assignment_id}.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["submission_id","student_tg_id","student_name","ts","late","has_file","local_path","text"])
        for s in rows:
            has_file = bool(s.get("file"))
            local_path = (s["file"] or {}).get("local_path","")
            w.writerow([s["submission_id"], s["student_tg_id"], s["student_name"], s["ts"], s["late"], has_file, local_path, (s.get("text") or "").replace("\n"," ")])
    return out_path

# --- SNAPSHOT TEXT ---
def build_snapshot_text() -> str:
    d = load()
    classes = d["classes"]; assignments = d["assignments"]
    latest = sorted(assignments.values(), key=lambda x: x.get("created_at",""), reverse=True)[:5]
    lines = [
        f"🔔 LMS Snapshot — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"Classes: {len(classes)} | Assignments: {len(assignments)}"
    ]
    for a in latest:
        lines.append(f"- {a['assignment_id']}: {a['title']} (class {a['class_id']}) due:{a.get('due_at','-')}")
    return "\n".join(lines)