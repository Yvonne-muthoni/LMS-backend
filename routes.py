# from flask import Blueprint, request, jsonify
from app import db
from models import Course, Enrollment, Student
from flask import Blueprint, request, jsonify
# Blueprints
course_bp = Blueprint('courses', __name__)
enrollment_bp = Blueprint('enrollments', __name__)
student_bp = Blueprint('students', __name__)

# Course Routes
@course_bp.route('/', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([course.as_dict() for course in courses])

@course_bp.route('/', methods=['POST'])
def add_course():
    data = request.json
    course = Course(
        id=data['id'],
        title=data['title'],
        description=data.get('description', ''),
        url=data['url']
    )
    db.session.add(course)
    db.session.commit()
    return jsonify(course.as_dict()), 201

@course_bp.route('/<string:id>', methods=['GET'])
def get_course(id):
    course = Course.query.get_or_404(id)
    return jsonify(course.as_dict())

@course_bp.route('/<string:id>', methods=['PUT'])
def update_course(id):
    data = request.json
    course = Course.query.get_or_404(id)
    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    course.url = data.get('url', course.url)
    db.session.commit()
    return jsonify(course.as_dict())

@course_bp.route('/<string:id>', methods=['DELETE'])
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return '', 204

# Enrollment Routes
@enrollment_bp.route('/', methods=['GET'])
def get_enrollments():
    enrollments = Enrollment.query.all()
    return jsonify([enrollment.as_dict() for enrollment in enrollments])

@enrollment_bp.route('/', methods=['POST'])
def add_enrollment():
    data = request.json
    enrollment = Enrollment(
        course_id=data['course_id'],
        student_id=data['student_id'],
        progress=data.get('progress', 0.0)
    )
    db.session.add(enrollment)
    db.session.commit()
    return jsonify(enrollment.as_dict()), 201

@enrollment_bp.route('/<int:id>', methods=['GET'])
def get_enrollment(id):
    enrollment = Enrollment.query.get_or_404(id)
    return jsonify(enrollment.as_dict())

@enrollment_bp.route('/<int:id>', methods=['PUT'])
def update_enrollment(id):
    data = request.json
    enrollment = Enrollment.query.get_or_404(id)
    enrollment.course_id = data.get('course_id', enrollment.course_id)
    enrollment.student_id = data.get('student_id', enrollment.student_id)
    enrollment.progress = data.get('progress', enrollment.progress)
    db.session.commit()
    return jsonify(enrollment.as_dict())

@enrollment_bp.route('/<int:id>', methods=['DELETE'])
def delete_enrollment(id):
    enrollment = Enrollment.query.get_or_404(id)
    db.session.delete(enrollment)
    db.session.commit()
    return '', 204

# Student Routes
@student_bp.route('/', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.as_dict() for student in students])

@student_bp.route('/', methods=['POST'])
def add_student():
    data = request.json
    student = Student(
        id=data['id'],
        name=data['name'],
        email=data['email']
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(student.as_dict()), 201

@student_bp.route('/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify(student.as_dict())

@student_bp.route('/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.json
    student = Student.query.get_or_404(id)
    student.name = data.get('name', student.name)
    student.email = data.get('email', student.email)
    db.session.commit()
    return jsonify(student.as_dict())

@student_bp.route('/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return '', 204
