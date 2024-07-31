from app import create_app, db
from models import Course, Student, Enrollment

def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Seed Courses
        courses = [
            Course(name='Introduction to Programming', description='Learn the basics of programming.'),
            Course(name='Data Structures and Algorithms', description='An in-depth look at data structures and algorithms.'),
            Course(name='Database Systems', description='Understanding database design and management.')
        ]
        db.session.add_all(courses)

        # Seed Students
        students = [
            Student(name='Alice Johnson', email='alice.johnson@example.com'),
            Student(name='Bob Smith', email='bob.smith@example.com'),
            Student(name='Charlie Brown', email='charlie.brown@example.com')
        ]
        db.session.add_all(students)

        # Seed Enrollments
        enrollments = [
            Enrollment(course_id=1, student_id=1, progress=75.0),
            Enrollment(course_id=1, student_id=2, progress=85.0),
            Enrollment(course_id=2, student_id=2, progress=90.0),
            Enrollment(course_id=3, student_id=3, progress=60.0)
        ]
        db.session.add_all(enrollments)

        # Commit the changes
        db.session.commit()

if __name__ == '__main__':
    seed_database()
    print("Database seeded successfully.")
