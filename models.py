
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
import json
import re

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(129), nullable=False)
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=db.func.now())

    subscriptions = db.relationship('Subscription', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    @validates('email')
    def validate_email(self, key, email):
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.match(regex, email):
            raise ValueError("Invalid email address")
        return email

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": str(self.created_at),
        }


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    video = db.Column(db.String(255), nullable=True)
    tech_stack = db.Column(db.String(255), nullable=True)
    what_you_will_learn = db.Column(db.Text, nullable=True)

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.truncate_description(self.description),
            'image': self.image,
            'video': self.video,
            'techStack': self.tech_stack.split(',') if self.tech_stack else [],
            'whatYouWillLearn': json.loads(self.what_you_will_learn) if self.what_you_will_learn else []
        }

    def truncate_description(self, description, max_length=200):
        """Truncate description to a maximum length and add ellipsis."""
        if description and len(description) > max_length:
            return description[:max_length] + '...'
        return description


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  
    options = db.Column(db.JSON, nullable=False)  # Use JSON type if SQLAlchemy version supports it
    correct_answer = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'questionText': self.question_text,
            'category': self.category,
            'options': self.options,  # Directly return the JSON data
            'correctAnswer': self.correct_answer
        }

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text}>"
    
class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subscription id={self.id} user_id={self.user_id} amount={self.amount}>'

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(50), default='pending')
    result_desc = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment id={self.id} user_id={self.user_id} amount={self.amount} status={self.status}>'
