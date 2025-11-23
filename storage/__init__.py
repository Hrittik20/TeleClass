"""
Noētica LMS - Storage Module

This module handles all data persistence for the LMS system.
Uses a file-based JSON database with atomic writes for data integrity.

Modules:
    storage.py - Core storage operations (classes, assignments, submissions)
    quiz.py - Quiz-related storage operations
"""

from .storage import (
    # Core functions
    load,
    save,
    
    # Teachers
    ensure_teacher,
    
    # Students
    ensure_student,
    get_student,
    
    # Classes
    link_class,
    get_class,
    get_course_by_code,
    
    # Enrollments
    enroll_student,
    is_student_enrolled,
    get_student_courses,
    
    # Assignments
    create_assignment,
    set_assignment_message_id,
    list_assignments,
    list_course_assignments,
    get_assignment,
    update_assignment,
    
    # Submissions
    add_submission,
    list_submissions,
    has_student_submitted,
    get_student_submission,
    export_submissions_csv,
    
    # Utilities
    build_snapshot_text,
)

# Create a singleton instance for convenience
class Storage:
    """
    Singleton storage instance providing access to all storage operations.
    
    Usage:
        from storage import storage
        storage.create_assignment(...)
    """
    
    def __init__(self):
        # Import all functions as methods
        self.load = load
        self.save = save
        
        # Teachers
        self.ensure_teacher = ensure_teacher
        
        # Students
        self.ensure_student = ensure_student
        self.get_student = get_student
        
        # Classes
        self.link_class = link_class
        self.get_class = get_class
        self.get_course_by_code = get_course_by_code
        
        # Enrollments
        self.enroll_student = enroll_student
        self.is_student_enrolled = is_student_enrolled
        self.get_student_courses = get_student_courses
        
        # Assignments
        self.create_assignment = create_assignment
        self.set_assignment_message_id = set_assignment_message_id
        self.list_assignments = list_assignments
        self.list_course_assignments = list_course_assignments
        self.get_assignment = get_assignment
        self.update_assignment = update_assignment
        
        # Submissions
        self.add_submission = add_submission
        self.list_submissions = list_submissions
        self.has_student_submitted = has_student_submitted
        self.get_student_submission = get_student_submission
        self.export_submissions_csv = export_submissions_csv
        
        # Utilities
        self.build_snapshot_text = build_snapshot_text

# Create singleton instance
storage = Storage()

__all__ = [
    'storage',
    'Storage',
    # Export individual functions too
    'load',
    'save',
    'ensure_teacher',
    'ensure_student',
    'get_student',
    'link_class',
    'get_class',
    'get_course_by_code',
    'enroll_student',
    'is_student_enrolled',
    'get_student_courses',
    'create_assignment',
    'set_assignment_message_id',
    'list_assignments',
    'list_course_assignments',
    'get_assignment',
    'update_assignment',
    'add_submission',
    'list_submissions',
    'has_student_submitted',
    'get_student_submission',
    'export_submissions_csv',
    'build_snapshot_text',
]

