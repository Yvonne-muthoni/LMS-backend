# from app import db

# class Course(db.Model):
#     id = db.Column(db.String(20), primary_key=True)  # Assuming video_id is a string
#     title = db.Column(db.String(100), nullable=False)  # Video title
#     description = db.Column(db.String(255), nullable=True)  # Video description
#     url = db.Column(db.String(255), nullable=False)  # Video URL

# class Student(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)

# class Enrollment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
#     progress = db.Column(db.Float, default=0.0)

#     course = db.relationship('Course', backref=db.backref('enrollments', lazy=True))
#     student = db.relationship('Student', backref=db.backref('enrollments', lazy=True))

# def as_dict(self):
#     return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Course.as_dict = as_dict
# Student.as_dict = as_dict
# Enrollment.as_dict = as_dict
from app import db

class Course(db.Model):
    id = db.Column(db.String(20), primary_key=True)  # Assuming video_id is a string
    title = db.Column(db.String(100), nullable=False)  # Video title
    description = db.Column(db.String(255), nullable=True)  # Video description
    url = db.Column(db.String(255), nullable=False)  # Video URL

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'url': self.url
        }

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.String(20), db.ForeignKey('course.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)

    course = db.relationship('Course', backref=db.backref('enrollments', lazy=True))
    student = db.relationship('Student', backref=db.backref('enrollments', lazy=True))

    def as_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'student_id': self.student_id,
            'progress': self.progress
        }
