from flask import Blueprint, request, jsonify
from app import db

# Existing blueprints
course_bp = Blueprint('courses', __name__)
enrollment_bp = Blueprint('enrollments', __name__)

# New blueprint for students
student_bp = Blueprint('students', __name__)

@course_bp.route('/', methods=['GET'])
def get_courses():
    from models import Course
    courses = Course.query.all()
    return jsonify([course.as_dict() for course in courses])

@course_bp.route('/', methods=['POST'])
def add_course():
    from models import Course
    data = request.json
    course = Course(name=data['name'], description=data.get('description', ''))
    db.session.add(course)
    db.session.commit()
    return jsonify(course.as_dict()), 201

@enrollment_bp.route('/', methods=['GET'])
def get_enrollments():
    from models import Enrollment
    enrollments = Enrollment.query.all()
    return jsonify([enrollment.as_dict() for enrollment in enrollments])

@enrollment_bp.route('/', methods=['POST'])
def add_enrollment():
    from models import Enrollment
    data = request.json
    enrollment = Enrollment(course_id=data['course_id'], student_id=data['student_id'], progress=data.get('progress', 0.0))
    db.session.add(enrollment)
    db.session.commit()
    return jsonify(enrollment.as_dict()), 201

@student_bp.route('/', methods=['GET'])
def get_students():
    from models import Student
    students = Student.query.all()
    return jsonify([student.as_dict() for student in students])

@student_bp.route('/', methods=['POST'])
def add_student():
    from models import Student
    data = request.json
    student = Student(name=data['name'], email=data['email'])
    db.session.add(student)
    db.session.commit()
    return jsonify(student.as_dict()), 201

@student_bp.route('/<int:id>', methods=['GET'])
def get_student(id):
    from models import Student
    student = Student.query.get_or_404(id)
    return jsonify(student.as_dict())

@student_bp.route('/<int:id>', methods=['PUT'])
def update_student(id):
    from models import Student
    data = request.json
    student = Student.query.get_or_404(id)
    student.name = data.get('name', student.name)
    student.email = data.get('email', student.email)
    db.session.commit()
    return jsonify(student.as_dict())

@student_bp.route('/<int:id>', methods=['DELETE'])
def delete_student(id):
    from models import Student
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return '', 204
