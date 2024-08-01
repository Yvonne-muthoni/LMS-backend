# import sys
sys.path.insert(0, '.')

from app import app, db
from models import Course, Student, Enrollment

with app.app_context():
    # Clear existing data
    db.drop_all()
    db.create_all()

    # Add sample data
    course1 = Course(id='1', title='Python Basics', description='Learn Python from scratch', url='http://example.com/python-basics')
    course2 = Course(id='2', title='Advanced Python', description='Deep dive into Python features', url='http://example.com/advanced-python')

    db.session.add(course1)
    db.session.add(course2)

    student1 = Student(name='John Doe', email='john.doe@example.com')
    student2 = Student(name='Jane Smith', email='jane.smith@example.com')

    db.session.add(student1)
    db.session.add(student2)

    enrollment1 = Enrollment(course_id='1', student_id=1, progress=0.5)
    enrollment2 = Enrollment(course_id='2', student_id=2, progress=0.8)

    db.session.add(enrollment1)
    db.session.add(enrollment2)

    db.session.commit()
