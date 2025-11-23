# server/quiz_api.py
from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from storage import storage
from storage.quiz import (
    create_quiz, update_quiz, get_quiz, list_quizzes,
    add_question, update_question, delete_question, list_questions,
    start_quiz_attempt, answer_question, complete_quiz_attempt,
    get_quiz_attempt, list_student_quiz_attempts, list_quiz_attempts
)
from server.app import current_user_id

router = APIRouter(prefix="/api/quiz", tags=["quiz"])

# --- Models ---
class QuizCreateRequest(BaseModel):
    class_id: str
    title: str
    description: str
    time_limit_minutes: Optional[int] = None
    due_at: Optional[str] = None
    passing_score: Optional[int] = None

class QuizUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    due_at: Optional[str] = None
    passing_score: Optional[int] = None
    status: Optional[str] = None  # draft, published, closed

class QuestionCreateRequest(BaseModel):
    quiz_id: str
    question_text: str
    question_type: str  # multiple_choice, true_false, short_answer, essay
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: Optional[Any] = None
    points: int = 1

class QuestionUpdateRequest(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    correct_answer: Optional[Any] = None
    points: Optional[int] = None

class QuizAttemptRequest(BaseModel):
    quiz_id: str

class AnswerRequest(BaseModel):
    question_id: str
    answer: Any

# --- Teacher Routes ---
@router.post("/teacher/quizzes")
async def teacher_create_quiz(
    request: QuizCreateRequest, 
    user_id: int = Depends(current_user_id())
):
    """Create a new quiz"""
    # Check if class exists and teacher owns it
    cls = storage.get_class(int(request.class_id))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    
    # Create quiz
    quiz = create_quiz(
        request.class_id,
        request.title,
        request.description,
        request.time_limit_minutes,
        request.due_at,
        request.passing_score
    )
    
    return quiz

@router.get("/teacher/quizzes")
async def teacher_list_quizzes(
    class_id: str,
    user_id: int = Depends(current_user_id())
):
    """List quizzes for a class"""
    # Check if class exists and teacher owns it
    cls = storage.get_class(int(class_id))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    
    # List quizzes
    quizzes = list_quizzes(class_id)
    
    # Add question count and attempt count to each quiz
    for quiz in quizzes:
        quiz["question_count"] = len(list_questions(quiz["quiz_id"]))
        quiz["attempt_count"] = len(list_quiz_attempts(quiz["quiz_id"]))
    
    return {"quizzes": quizzes}

@router.get("/teacher/quizzes/{quiz_id}")
async def teacher_get_quiz(
    quiz_id: str,
    user_id: int = Depends(current_user_id())
):
    """Get a quiz with questions and attempts"""
    # Get quiz
    quiz = get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if teacher owns the class
    cls = storage.get_class(int(quiz["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    
    # Get questions and attempts
    questions = list_questions(quiz_id)
    attempts = list_quiz_attempts(quiz_id)
    
    # Group attempts by student
    student_attempts = {}
    for attempt in attempts:
        student_id = attempt["student_tg_id"]
        if student_id not in student_attempts:
            student_attempts[student_id] = []
        student_attempts[student_id].append(attempt)
    
    # Format student data
    students = []
    for student_id, student_attempts_list in student_attempts.items():
        # Get student name
        student = storage.get_student(student_id)
        student_name = student["name"] if student else f"Student {student_id}"
        
        # Get best score
        best_score = max([a["score"] for a in student_attempts_list if a["score"] is not None], default=None)
        
        students.append({
            "student_id": student_id,
            "student_name": student_name,
            "attempt_count": len(student_attempts_list),
            "best_score": best_score
        })
    
    return {
        "quiz": quiz,
        "questions": questions,
        "students": students
    }

@router.patch("/teacher/quizzes/{quiz_id}")
async def teacher_update_quiz(
    quiz_id: str,
    request: QuizUpdateRequest,
    user_id: int = Depends(current_user_id())
):
    """Update a quiz"""
    # Get quiz
    quiz = get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if teacher owns the class
    cls = storage.get_class(int(quiz["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    
    # Update quiz
    updated_quiz = update_quiz(quiz_id, **request.model_dump(exclude_none=True))
    if not updated_quiz:
        raise HTTPException(404, "Quiz not found")
    
    return updated_quiz

@router.post("/teacher/questions")
async def teacher_add_question(
    request: QuestionCreateRequest,
    user_id: int = Depends(current_user_id())
):
    """Add a question to a quiz"""
    # Get quiz
    quiz = get_quiz(request.quiz_id)
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if teacher owns the class
    cls = storage.get_class(int(quiz["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    
    # Check if quiz is in draft status
    if quiz["status"] != "draft":
        raise HTTPException(400, "Cannot modify questions for a published quiz")
    
    # Add question
    question = add_question(
        request.quiz_id,
        request.question_text,
        request.question_type,
        request.options,
        request.correct_answer,
        request.points
    )
    
    return question

@router.patch("/teacher/questions/{question_id}")
async def teacher_update_question(
    question_id: str,
    request: QuestionUpdateRequest,
    user_id: int = Depends(current_user_id())
):
    """Update a question"""
    # Get question
    data = storage.load()
    if "questions" not in data or question_id not in data["questions"]:
        raise HTTPException(404, "Question not found")
    
    question = data["questions"][question_id]
    
    # Get quiz
    quiz = get_quiz(question["quiz_id"])
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if teacher owns the class
    cls = storage.get_class(int(quiz["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    
    # Check if quiz is in draft status
    if quiz["status"] != "draft":
        raise HTTPException(400, "Cannot modify questions for a published quiz")
    
    # Update question
    updated_question = update_question(question_id, **request.model_dump(exclude_none=True))
    if not updated_question:
        raise HTTPException(404, "Question not found")
    
    return updated_question

@router.delete("/teacher/questions/{question_id}")
async def teacher_delete_question(
    question_id: str,
    user_id: int = Depends(current_user_id())
):
    """Delete a question"""
    # Get question
    data = storage.load()
    if "questions" not in data or question_id not in data["questions"]:
        raise HTTPException(404, "Question not found")
    
    question = data["questions"][question_id]
    
    # Get quiz
    quiz = get_quiz(question["quiz_id"])
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if teacher owns the class
    cls = storage.get_class(int(quiz["class_id"]))
    if not cls or cls["teacher_tg_id"] != user_id:
        raise HTTPException(403, "Not your class")
    
    # Check if quiz is in draft status
    if quiz["status"] != "draft":
        raise HTTPException(400, "Cannot modify questions for a published quiz")
    
    # Delete question
    success = delete_question(question_id)
    if not success:
        raise HTTPException(404, "Question not found")
    
    return {"success": True}

# --- Student Routes ---
@router.get("/student/quizzes")
async def student_list_quizzes(
    user_id: int = Depends(current_user_id())
):
    """List available quizzes for a student"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Get student's courses
    courses = storage.get_student_courses(user_id)
    
    # Get quizzes for each course
    result = []
    for course in courses:
        quizzes = list_quizzes(course["course_id"])
        
        # Filter to only published quizzes
        quizzes = [q for q in quizzes if q["status"] == "published"]
        
        for quiz in quizzes:
            # Get student's attempts for this quiz
            attempts = list_student_quiz_attempts(user_id, quiz["quiz_id"])
            
            # Calculate best score
            best_score = max([a["score"] for a in attempts if a["score"] is not None], default=None)
            
            # Add to result
            result.append({
                "quiz_id": quiz["quiz_id"],
                "title": quiz["title"],
                "description": quiz["description"],
                "course_id": course["course_id"],
                "course_title": course["title"],
                "due_at": quiz.get("due_at"),
                "time_limit_minutes": quiz.get("time_limit_minutes"),
                "attempt_count": len(attempts),
                "best_score": best_score,
                "passing_score": quiz.get("passing_score")
            })
    
    return {"quizzes": result}

@router.get("/student/quizzes/{quiz_id}")
async def student_get_quiz(
    quiz_id: str,
    user_id: int = Depends(current_user_id())
):
    """Get a quiz for a student"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Get quiz
    quiz = get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if quiz is published
    if quiz["status"] != "published":
        raise HTTPException(404, "Quiz not found")
    
    # Check if student is enrolled in the course
    if not storage.is_student_enrolled(user_id, quiz["class_id"]):
        raise HTTPException(403, "You are not enrolled in this course")
    
    # Get course
    course = storage.get_class(int(quiz["class_id"]))
    
    # Get student's attempts for this quiz
    attempts = list_student_quiz_attempts(user_id, quiz_id)
    
    # Calculate best score
    best_score = max([a["score"] for a in attempts if a["score"] is not None], default=None)
    
    return {
        "quiz": {
            "quiz_id": quiz["quiz_id"],
            "title": quiz["title"],
            "description": quiz["description"],
            "course_id": quiz["class_id"],
            "course_title": course["title"],
            "due_at": quiz.get("due_at"),
            "time_limit_minutes": quiz.get("time_limit_minutes"),
            "attempt_count": len(attempts),
            "best_score": best_score,
            "passing_score": quiz.get("passing_score")
        },
        "attempts": attempts
    }

@router.post("/student/attempts")
async def student_start_attempt(
    request: QuizAttemptRequest,
    user_id: int = Depends(current_user_id())
):
    """Start a quiz attempt"""
    # Ensure student exists
    storage.ensure_student(user_id)
    
    # Get quiz
    quiz = get_quiz(request.quiz_id)
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    
    # Check if quiz is published
    if quiz["status"] != "published":
        raise HTTPException(400, "Quiz is not available")
    
    # Check if student is enrolled in the course
    if not storage.is_student_enrolled(user_id, quiz["class_id"]):
        raise HTTPException(403, "You are not enrolled in this course")
    
    try:
        # Start attempt
        attempt = start_quiz_attempt(request.quiz_id, user_id)
        
        # Get questions
        questions = list_questions(request.quiz_id)
        
        # Remove correct answers from questions
        for q in questions:
            q.pop("correct_answer", None)
        
        return {
            "attempt": attempt,
            "questions": questions
        }
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/student/attempts/{attempt_id}/answer")
async def student_answer_question(
    attempt_id: str,
    request: AnswerRequest,
    user_id: int = Depends(current_user_id())
):
    """Answer a question in a quiz attempt"""
    # Get attempt
    attempt = get_quiz_attempt(attempt_id)
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    
    # Check if this is the student's attempt
    if attempt["student_tg_id"] != user_id:
        raise HTTPException(403, "Not your attempt")
    
    try:
        # Record answer
        updated_attempt = answer_question(attempt_id, request.question_id, request.answer)
        return updated_attempt
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.post("/student/attempts/{attempt_id}/complete")
async def student_complete_attempt(
    attempt_id: str,
    user_id: int = Depends(current_user_id())
):
    """Complete a quiz attempt"""
    # Get attempt
    attempt = get_quiz_attempt(attempt_id)
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    
    # Check if this is the student's attempt
    if attempt["student_tg_id"] != user_id:
        raise HTTPException(403, "Not your attempt")
    
    try:
        # Complete attempt
        completed_attempt = complete_quiz_attempt(attempt_id)
        
        # Get quiz
        quiz = get_quiz(completed_attempt["quiz_id"])
        
        # Check if passed
        passed = None
        if quiz.get("passing_score") is not None:
            passed = completed_attempt["score"] >= quiz["passing_score"]
        
        return {
            "attempt": completed_attempt,
            "passed": passed
        }
    except ValueError as e:
        raise HTTPException(400, str(e))

@router.get("/student/attempts/{attempt_id}")
async def student_get_attempt(
    attempt_id: str,
    user_id: int = Depends(current_user_id())
):
    """Get a quiz attempt"""
    # Get attempt
    attempt = get_quiz_attempt(attempt_id)
    if not attempt:
        raise HTTPException(404, "Attempt not found")
    
    # Check if this is the student's attempt
    if attempt["student_tg_id"] != user_id:
        raise HTTPException(403, "Not your attempt")
    
    # Get quiz
    quiz = get_quiz(attempt["quiz_id"])
    
    # Get questions
    questions = list_questions(attempt["quiz_id"])
    
    # If attempt is completed, include correct answers
    if attempt["status"] == "completed":
        questions_with_answers = questions
    else:
        # Remove correct answers from questions
        questions_with_answers = []
        for q in questions:
            q_copy = q.copy()
            q_copy.pop("correct_answer", None)
            questions_with_answers.append(q_copy)
    
    return {
        "attempt": attempt,
        "quiz": quiz,
        "questions": questions_with_answers
    }
