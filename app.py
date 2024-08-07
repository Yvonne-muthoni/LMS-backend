
from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Course, Question  
from flask_cors import CORS
import json
import random
import requests
from routes import course_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"
CORS(app, resources={r"/*": {"origins": "*"}})

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)
api = Api(app)

class Users(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        users = User.query.all()
        users_list = [user.to_dict() for user in users]
        return make_response({"count": len(users_list), "users": users_list}, 200)

    def post(self):
        email = User.query.filter_by(email=request.json.get('email')).first()
        if email:
            return make_response({"message": "Email already taken"}, 422)

        new_user = User(
            username=request.json.get("username"),
            email=request.json.get("email"),
            password=bcrypt.generate_password_hash(request.json.get("password")).decode('utf-8'),
            role=request.json.get("role", "user")
        )

        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity=new_user.id)
        return make_response({"user": new_user.to_dict(), "access_token": access_token, "success": True, "message": "User has been created successfully"}, 201)

class Login(Resource):
    def post(self):
        email = request.json.get('email')
        password = request.json.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            return make_response({
                "user": user.to_dict(),
                "access_token": access_token,
                "success": True,
                "message": "Login successful"
            }, 200)
        return make_response({"message": "Invalid credentials"}, 401)

class VerifyToken(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user:
            return make_response({
                "user": user.to_dict(),
                "success": True,
                "message": "Token is valid"
            }, 200)
        return make_response({"message": "Invalid token"}, 401)

class Courses(Resource):
    def get(self):
        try:
            print("GET /courses route accessed") 
            courses = Course.query.all()
            courses_list = [course.as_dict() for course in courses]
            return make_response({"courses": courses_list}, 200)
        except Exception as e:
            print(f"Error fetching courses: {e}")
            return make_response({"message": "An error occurred"}, 500)

    def post(self):
        try:
            data = request.json
            new_course = Course(
                title=data.get("title"),
                description=data.get("description"),
                image=data.get("image"),
                video=data.get("video"),
                tech_stack=data.get("tech_stack"),
                what_you_will_learn=json.dumps(data.get("what_you_will_learn"))
            )
            db.session.add(new_course)
            db.session.commit()
            return make_response({"course": new_course.as_dict(), "message": "Course created successfully"}, 201)
        except Exception as e:
            print(f"Error creating course: {e}")
            return make_response({"message": "An error occurred"}, 500)

    def delete(self):
        try:
            data = request.json
            course = Course.query.get(data.get("id"))
            if course:
                db.session.delete(course)
                db.session.commit()
                return make_response({"message": "Course deleted successfully"}, 200)
            return make_response({"message": "Course not found"}, 404)
        except Exception as e:
            print(f"Error deleting course: {e}")
            return make_response({"message": "An error occurred"}, 500)

# Define a separate resource class for GET requests
class QuestionsGet(Resource):
    def get(self, category):
        try:
            print(f"GET /questions/{category} route accessed")
            questions = Question.query.filter_by(category=category).all()
            questions_list = [question.as_dict() for question in questions]
            return make_response({"questions": questions_list}, 200)
        except Exception as e:
            print(f"Error fetching questions: {e}")
            return make_response({"message": "An error occurred"}, 500)

# Define a separate resource class for POST requests
class QuestionsPost(Resource):
    def post(self):
        try:
            data = request.json
            new_question = Question(
                question_text=data.get("question_text"),
                category=data.get("category"),
                options=json.dumps(data.get("options")),  # Store options as a JSON string
                correct_answer=data.get("correct_answer")
            )
            db.session.add(new_question)
            db.session.commit()
            return make_response({"question": new_question.as_dict(), "message": "Question created successfully"}, 201)
        except Exception as e:
            print(f"Error creating question: {e}")
            return make_response({"message": "An error occurred"}, 500)
@app.route('/questions/<int:id>', methods=['GET'])
def get_question(id):
    question = Question.query.get(id)
    if question:
        return jsonify(question.as_dict()), 200
    else:
        return jsonify({"error": "Question not found"}), 404


api.add_resource(Users, '/users')
api.add_resource(Login, '/login')
api.add_resource(VerifyToken, '/verify-token')
api.add_resource(Courses, '/courses')
api.add_resource(QuestionsGet, '/questions/<string:category>')  # GET requests for a specific category
api.add_resource(QuestionsPost, '/questions')  # POST requests

app.register_blueprint(course_bp, url_prefix='/courses') 

if __name__ == '__main__':
    app.run(debug=True)
