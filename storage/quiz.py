# storage/quiz.py
from __future__ import annotations
import time
from typing import Dict, Any, Optional, List
from storage.storage import load, save, _now_iso

def make_quiz_id() -> str:
    """Generate a unique quiz ID"""
    return "Q" + str(int(time.time()))

def make_question_id() -> str:
    """Generate a unique question ID"""
    return "QQ" + str(int(time.time()*1000))

def make_attempt_id() -> str:
    """Generate a unique attempt ID"""
    return "QA" + str(int(time.time()*1000))

# --- QUIZZES ---
def create_quiz(class_id: str, title: str, description: str, time_limit_minutes: Optional[int] = None, 
                due_at: Optional[str] = None, passing_score: Optional[int] = None) -> Dict[str, Any]:
    """Create a new quiz for a class"""
    quiz_id = make_quiz_id()
    
    def mut(d):
        # Initialize quizzes dict if it doesn't exist
        if "quizzes" not in d:
            d["quizzes"] = {}
        
        # Create the quiz
        d["quizzes"][quiz_id] = {
            "quiz_id": quiz_id,
            "class_id": class_id,
            "title": title,
            "description": description,
            "time_limit_minutes": time_limit_minutes,
            "due_at": due_at,
            "passing_score": passing_score,
            "status": "draft",  # draft, published, closed
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "published_at": None
        }
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "quiz_created",
            "actor": d["classes"][class_id]["teacher_tg_id"],
            "payload": {"quiz_id": quiz_id},
            "ts": _now_iso()
        })
        
        return d["quizzes"][quiz_id]
    
    return save(mut)

def update_quiz(quiz_id: str, **updates) -> Optional[Dict[str, Any]]:
    """Update a quiz"""
    def mut(d):
        # Check if quizzes dict exists
        if "quizzes" not in d or quiz_id not in d["quizzes"]:
            return None
        
        # Update fields
        d["quizzes"][quiz_id].update({k: v for k, v in updates.items() if v is not None})
        d["quizzes"][quiz_id]["updated_at"] = _now_iso()
        
        # If publishing, set published_at
        if updates.get("status") == "published" and not d["quizzes"][quiz_id].get("published_at"):
            d["quizzes"][quiz_id]["published_at"] = _now_iso()
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "quiz_updated",
            "actor": d["classes"][d["quizzes"][quiz_id]["class_id"]]["teacher_tg_id"],
            "payload": {"quiz_id": quiz_id, "updates": list(updates.keys())},
            "ts": _now_iso()
        })
        
        return d["quizzes"][quiz_id]
    
    return save(mut)

def get_quiz(quiz_id: str) -> Optional[Dict[str, Any]]:
    """Get a quiz by ID"""
    data = load()
    if "quizzes" not in data:
        return None
    return data["quizzes"].get(quiz_id)

def list_quizzes(class_id: str) -> List[Dict[str, Any]]:
    """List all quizzes for a class"""
    data = load()
    if "quizzes" not in data:
        return []
    return [q for q in data["quizzes"].values() if q["class_id"] == class_id]

# --- QUESTIONS ---
def add_question(quiz_id: str, question_text: str, question_type: str, options: Optional[List[Dict[str, Any]]] = None,
                correct_answer: Optional[Any] = None, points: int = 1) -> Dict[str, Any]:
    """
    Add a question to a quiz
    
    question_type: 'multiple_choice', 'true_false', 'short_answer', 'essay'
    options: For multiple_choice, list of {id: str, text: str}
    correct_answer: For multiple_choice: option_id, for true_false: boolean, for short_answer: string
    """
    question_id = make_question_id()
    
    def mut(d):
        # Initialize questions dict if it doesn't exist
        if "questions" not in d:
            d["questions"] = {}
        
        # Get quiz
        if "quizzes" not in d or quiz_id not in d["quizzes"]:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        # Create the question
        d["questions"][question_id] = {
            "question_id": question_id,
            "quiz_id": quiz_id,
            "question_text": question_text,
            "question_type": question_type,
            "options": options or [],
            "correct_answer": correct_answer,
            "points": points,
            "created_at": _now_iso(),
            "updated_at": _now_iso()
        }
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "question_added",
            "actor": d["classes"][d["quizzes"][quiz_id]["class_id"]]["teacher_tg_id"],
            "payload": {"quiz_id": quiz_id, "question_id": question_id},
            "ts": _now_iso()
        })
        
        return d["questions"][question_id]
    
    return save(mut)

def update_question(question_id: str, **updates) -> Optional[Dict[str, Any]]:
    """Update a question"""
    def mut(d):
        # Check if questions dict exists
        if "questions" not in d or question_id not in d["questions"]:
            return None
        
        # Update fields
        d["questions"][question_id].update({k: v for k, v in updates.items() if v is not None})
        d["questions"][question_id]["updated_at"] = _now_iso()
        
        # Get quiz
        quiz_id = d["questions"][question_id]["quiz_id"]
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "question_updated",
            "actor": d["classes"][d["quizzes"][quiz_id]["class_id"]]["teacher_tg_id"],
            "payload": {"question_id": question_id, "updates": list(updates.keys())},
            "ts": _now_iso()
        })
        
        return d["questions"][question_id]
    
    return save(mut)

def delete_question(question_id: str) -> bool:
    """Delete a question"""
    def mut(d):
        # Check if questions dict exists
        if "questions" not in d or question_id not in d["questions"]:
            return False
        
        # Get quiz
        quiz_id = d["questions"][question_id]["quiz_id"]
        
        # Delete the question
        del d["questions"][question_id]
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "question_deleted",
            "actor": d["classes"][d["quizzes"][quiz_id]["class_id"]]["teacher_tg_id"],
            "payload": {"question_id": question_id},
            "ts": _now_iso()
        })
        
        return True
    
    return save(mut)

def list_questions(quiz_id: str) -> List[Dict[str, Any]]:
    """List all questions for a quiz"""
    data = load()
    if "questions" not in data:
        return []
    return [q for q in data["questions"].values() if q["quiz_id"] == quiz_id]

# --- QUIZ ATTEMPTS ---
def start_quiz_attempt(quiz_id: str, student_tg_id: int) -> Dict[str, Any]:
    """Start a quiz attempt for a student"""
    attempt_id = make_attempt_id()
    
    def mut(d):
        # Initialize attempts dict if it doesn't exist
        if "quiz_attempts" not in d:
            d["quiz_attempts"] = {}
        
        # Get quiz
        if "quizzes" not in d or quiz_id not in d["quizzes"]:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        # Check if quiz is published
        if d["quizzes"][quiz_id]["status"] != "published":
            raise ValueError(f"Quiz {quiz_id} is not published")
        
        # Check if quiz is past due date
        if d["quizzes"][quiz_id].get("due_at"):
            import datetime
            now = datetime.datetime.fromisoformat(_now_iso().replace("Z", ""))
            due = datetime.datetime.fromisoformat(d["quizzes"][quiz_id]["due_at"].replace("Z", ""))
            if now > due:
                raise ValueError(f"Quiz {quiz_id} is past due date")
        
        # Create the attempt
        start_time = _now_iso()
        d["quiz_attempts"][attempt_id] = {
            "attempt_id": attempt_id,
            "quiz_id": quiz_id,
            "student_tg_id": student_tg_id,
            "start_time": start_time,
            "end_time": None,
            "answers": {},  # question_id -> answer
            "score": None,
            "status": "in_progress",  # in_progress, completed, abandoned
            "created_at": start_time,
            "updated_at": start_time
        }
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "quiz_attempt_started",
            "actor": student_tg_id,
            "payload": {"quiz_id": quiz_id, "attempt_id": attempt_id},
            "ts": start_time
        })
        
        return d["quiz_attempts"][attempt_id]
    
    return save(mut)

def answer_question(attempt_id: str, question_id: str, answer: Any) -> Dict[str, Any]:
    """Record an answer for a question in a quiz attempt"""
    def mut(d):
        # Check if attempts dict exists
        if "quiz_attempts" not in d or attempt_id not in d["quiz_attempts"]:
            raise ValueError(f"Attempt {attempt_id} not found")
        
        # Check if attempt is in progress
        if d["quiz_attempts"][attempt_id]["status"] != "in_progress":
            raise ValueError(f"Attempt {attempt_id} is not in progress")
        
        # Check if question exists
        if "questions" not in d or question_id not in d["questions"]:
            raise ValueError(f"Question {question_id} not found")
        
        # Check if question belongs to the quiz
        if d["questions"][question_id]["quiz_id"] != d["quiz_attempts"][attempt_id]["quiz_id"]:
            raise ValueError(f"Question {question_id} does not belong to this quiz")
        
        # Record the answer
        d["quiz_attempts"][attempt_id]["answers"][question_id] = answer
        d["quiz_attempts"][attempt_id]["updated_at"] = _now_iso()
        
        return d["quiz_attempts"][attempt_id]
    
    return save(mut)

def complete_quiz_attempt(attempt_id: str) -> Dict[str, Any]:
    """Complete a quiz attempt and calculate the score"""
    def mut(d):
        # Check if attempts dict exists
        if "quiz_attempts" not in d or attempt_id not in d["quiz_attempts"]:
            raise ValueError(f"Attempt {attempt_id} not found")
        
        # Check if attempt is in progress
        if d["quiz_attempts"][attempt_id]["status"] != "in_progress":
            raise ValueError(f"Attempt {attempt_id} is not in progress")
        
        # Get quiz and questions
        quiz_id = d["quiz_attempts"][attempt_id]["quiz_id"]
        questions = [q for q in d["questions"].values() if q["quiz_id"] == quiz_id]
        
        # Calculate score
        total_points = sum(q["points"] for q in questions)
        earned_points = 0
        
        for question in questions:
            question_id = question["question_id"]
            if question_id not in d["quiz_attempts"][attempt_id]["answers"]:
                continue
            
            student_answer = d["quiz_attempts"][attempt_id]["answers"][question_id]
            
            # Check if answer is correct based on question type
            if question["question_type"] in ["multiple_choice", "true_false"]:
                if student_answer == question["correct_answer"]:
                    earned_points += question["points"]
            elif question["question_type"] == "short_answer":
                # Case-insensitive comparison for short answer
                if str(student_answer).lower() == str(question["correct_answer"]).lower():
                    earned_points += question["points"]
            # Essay questions need manual grading
        
        # Calculate percentage score
        score = round((earned_points / total_points) * 100) if total_points > 0 else 0
        
        # Update attempt
        d["quiz_attempts"][attempt_id]["end_time"] = _now_iso()
        d["quiz_attempts"][attempt_id]["score"] = score
        d["quiz_attempts"][attempt_id]["status"] = "completed"
        d["quiz_attempts"][attempt_id]["updated_at"] = _now_iso()
        
        # Add event
        d["events"].append({
            "id": f"E{time.time_ns()}",
            "type": "quiz_attempt_completed",
            "actor": d["quiz_attempts"][attempt_id]["student_tg_id"],
            "payload": {"quiz_id": quiz_id, "attempt_id": attempt_id, "score": score},
            "ts": _now_iso()
        })
        
        return d["quiz_attempts"][attempt_id]
    
    return save(mut)

def get_quiz_attempt(attempt_id: str) -> Optional[Dict[str, Any]]:
    """Get a quiz attempt by ID"""
    data = load()
    if "quiz_attempts" not in data:
        return None
    return data["quiz_attempts"].get(attempt_id)

def list_student_quiz_attempts(student_tg_id: int, quiz_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all quiz attempts for a student, optionally filtered by quiz_id"""
    data = load()
    if "quiz_attempts" not in data:
        return []
    
    attempts = [a for a in data["quiz_attempts"].values() if a["student_tg_id"] == student_tg_id]
    
    if quiz_id:
        attempts = [a for a in attempts if a["quiz_id"] == quiz_id]
    
    return attempts

def list_quiz_attempts(quiz_id: str) -> List[Dict[str, Any]]:
    """List all attempts for a quiz"""
    data = load()
    if "quiz_attempts" not in data:
        return []
    return [a for a in data["quiz_attempts"].values() if a["quiz_id"] == quiz_id]
