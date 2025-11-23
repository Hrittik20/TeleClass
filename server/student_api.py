# server/student_api.py
import os, uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from storage import storage
from server.app import current_user_id

router = APIRouter(prefix="/api/student", tags=["student"])

# --- Models ---
class CourseResponse(BaseModel):
    id: str
    title: str
    teacher_name: str
    assignment_count: int
    completed_count: int

class EnrollRequest(BaseModel):
    course_code: str

class AssignmentResponse(BaseModel):
    id: str
    title: str
    instructions: str
    course_id: str
    course_title: str
    due_at: Optional[str] = None
    closed: bool
    submitted: bool

class SubmissionFile(BaseModel):
    name: str
    url: str
    mime_type: str
    size: int

class SubmissionResponse(BaseModel):
    id: str
    submitted_at: str
    text: Optional[str] = None
    files: List[SubmissionFile] = []
    status: str

class AssignmentDetailResponse(BaseModel):
    id: str
    title: str
    instructions: str
    course_id: str
    course_title: str
    due_at: Optional[str] = None
    closed: bool
    submission: Optional[SubmissionResponse] = None

# --- Routes ---
@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(user_id: int = Depends(current_user_id())):
    """Get all courses the student is enrolled in"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Get student's courses
    courses = storage.get_student_courses(user_id)
    
    # Format response
    result = []
    for course in courses:
        # Get assignments for this course
        assignments = storage.list_course_assignments(course["course_id"])
        # Count completed assignments
        completed = 0
        for assignment in assignments:
            if storage.has_student_submitted(assignment["assignment_id"], user_id):
                completed += 1
                
        result.append({
            "id": course["course_id"],
            "title": course["title"],
            "teacher_name": course["teacher_name"],
            "assignment_count": len(assignments),
            "completed_count": completed
        })
    
    return result

@router.post("/enroll")
async def enroll_in_course(request: EnrollRequest, user_id: int = Depends(current_user_id())):
    """Enroll student in a course using a course code"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Find course by code
    course = storage.get_course_by_code(request.course_code)
    if not course:
        raise HTTPException(404, "Course not found with this code")
    
    # Enroll student
    storage.enroll_student(user_id, course["course_id"])
    
    return {"success": True, "course_id": course["course_id"]}

@router.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(user_id: int = Depends(current_user_id())):
    """Get all assignments for courses the student is enrolled in"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Get student's courses
    courses = storage.get_student_courses(user_id)
    
    # Get assignments for all courses
    result = []
    for course in courses:
        assignments = storage.list_course_assignments(course["course_id"])
        for assignment in assignments:
            # Check if student has submitted
            submitted = storage.has_student_submitted(assignment["assignment_id"], user_id)
            
            result.append({
                "id": assignment["assignment_id"],
                "title": assignment["title"],
                "instructions": assignment["instructions_md"],
                "course_id": course["course_id"],
                "course_title": course["title"],
                "due_at": assignment.get("due_at"),
                "closed": assignment.get("status") == "closed",
                "submitted": submitted
            })
    
    return result

@router.get("/assignments/{assignment_id}", response_model=AssignmentDetailResponse)
async def get_assignment_detail(assignment_id: str, user_id: int = Depends(current_user_id())):
    """Get detailed information about an assignment"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Get assignment
    assignment = storage.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    
    # Get course
    course = storage.get_class(int(assignment["class_id"]))
    if not course:
        raise HTTPException(404, "Course not found")
    
    # Check if student is enrolled in this course
    if not storage.is_student_enrolled(user_id, assignment["class_id"]):
        raise HTTPException(403, "You are not enrolled in this course")
    
    # Check if student has submitted
    submission = storage.get_student_submission(assignment_id, user_id)
    submission_response = None
    
    if submission:
        files = []
        if submission.get("file"):
            file_meta = submission["file"]
            files.append({
                "name": file_meta.get("filename", "file"),
                "url": f"/api/files/{file_meta.get('file_id')}",
                "mime_type": file_meta.get("mime", "application/octet-stream"),
                "size": file_meta.get("size", 0)
            })
        
        submission_response = {
            "id": submission["submission_id"],
            "submitted_at": submission["ts"],
            "text": submission.get("text", ""),
            "files": files,
            "status": "late" if submission.get("late") else "on_time"
        }
    
    return {
        "id": assignment["assignment_id"],
        "title": assignment["title"],
        "instructions": assignment["instructions_md"],
        "course_id": assignment["class_id"],
        "course_title": course["title"],
        "due_at": assignment.get("due_at"),
        "closed": assignment.get("status") == "closed",
        "submission": submission_response
    }

@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: str,
    text: str = Form(""),
    file: Optional[UploadFile] = File(None),
    user_id: int = Depends(current_user_id())
):
    """Submit an assignment"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Get assignment
    assignment = storage.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(404, "Assignment not found")
    
    # Check if assignment is closed
    if assignment.get("status") == "closed":
        raise HTTPException(400, "Assignment is closed")
    
    # Check if student is enrolled in this course
    if not storage.is_student_enrolled(user_id, assignment["class_id"]):
        raise HTTPException(403, "You are not enrolled in this course")
    
    # Process file if provided
    file_meta = None
    if file:
        # Get student name for filename
        student = storage.get_student(user_id)
        student_name = student.get("name", f"student_{user_id}")
        
        # Create safe filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{student_name}_{file.filename}"
        
        # Ensure files directory exists
        files_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "files")
        os.makedirs(files_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(files_dir, filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Create file metadata
        file_meta = {
            "file_id": file_id,
            "filename": file.filename,
            "mime": file.content_type,
            "size": os.path.getsize(file_path),
            "local_path": file_path
        }
    
    # Get student name
    student = storage.get_student(user_id)
    student_name = student.get("name", f"User {user_id}")
    
    # Add submission
    submission = storage.add_submission(
        assignment_id,
        user_id,
        student_name,
        text=text,
        file_meta=file_meta
    )
    
    # Notify teacher
    cls = storage.get_class(int(assignment["class_id"]))
    if cls:
        from server.telegram_api import send_teacher_snapshot
        send_teacher_snapshot(cls["teacher_tg_id"])
    
    return {"success": True, "submission_id": submission["submission_id"]}
