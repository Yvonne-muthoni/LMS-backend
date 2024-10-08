from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

import base64

from datetime import datetime
import os
import logging
import json
import requests 

from flask import Flask, make_response, request, jsonify, Blueprint
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS

from models import db, User, Course, Question, Subscription, Payment, ProCourse, QuizResult
from routes import course_bp, pro_course_bp 

app = Flask(__name__)
load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret"

CORS(app, resources={r"/*": {"origins": "*"}})
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)
api = Api(app)

logging.basicConfig(level=logging.DEBUG)


CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
SHORTCODE = os.getenv('SHORTCODE')
LIPA_NA_MPESA_ONLINE_PASSKEY = os.getenv('LIPA_NA_MPESA_ONLINE_PASSKEY')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')


def get_mpesa_access_token():
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    api_key = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(api_key.encode()).decode()
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting access token: {e}")
        raise

def generate_password(shortcode, passkey):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(data_to_encode.encode()).decode('utf-8'), timestamp

class SubscriptionResource(Resource):
    def initiate_mpesa_payment(self, user_id, amount, phone_number):
        payment = Payment(user_id=user_id, amount=amount, phone_number=phone_number)
        db.session.add(payment)
        db.session.commit()

        access_token = get_mpesa_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        password, timestamp = generate_password(SHORTCODE, LIPA_NA_MPESA_ONLINE_PASSKEY)
        payload = {
            "BusinessShortCode": SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://bd09-105-163-157-135.ngrok-free.app/callback",  # Make sure this URL is accessible and secure
            "AccountReference": "SubscriptionPayment",
            "TransactionDesc": "Subscription payment"
        }

        try:
            response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                headers=headers,
                json=payload
            )
            response.raise_for_status()  # Raise HTTPError for bad responses
            response_data = response.json()
            logging.debug(f"M-Pesa response: {response_data}")

            if response_data.get('ResponseCode') == '0':
                payment.transaction_id = response_data['CheckoutRequestID']
                payment.status = 'initiated'
                db.session.commit()
                return {'message': 'Payment initiated successfully, waiting for callback'}, 201
            else:
                error_message = response_data.get('ResponseDescription', 'Failed to initiate payment')
                return {'error': error_message}, 400
        except requests.exceptions.HTTPError as e:
            logging.error(f'HTTP error during M-Pesa request: {e}')
            return {'error': 'Failed to connect to M-Pesa API'}, 500
        except requests.exceptions.RequestException as e:
            logging.error(f'Request exception during M-Pesa request: {e}')
            return {'error': 'Failed to connect to M-Pesa API'}, 500

    def post(self):
        data = request.get_json()
        app.logger.debug(f"Subscription POST data: {data}")

        user_id = data.get('user_id')
        if not user_id:
            return {'error': 'User ID is required'}, 400

        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        amount = data.get('amount')
        if not amount:
            return {'error': 'Amount is required'}, 400

        phone_number = data.get('phone_number')
        if not phone_number:
            return {'error': 'Phone number is required'}, 400

        subscription = Subscription(user_id=user.id, amount=amount)
        db.session.add(subscription)
        db.session.commit()

        payment_response = self.initiate_mpesa_payment(user_id, amount, phone_number)
        return payment_response

@app.route('/callback', methods=['POST'])
def mpesa_callback():
    try:
        data = request.json
        logging.debug(f"Callback data: {data}")

        callback_metadata = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {})
        items = callback_metadata.get('Item', [])

        if not items:
            return jsonify({"error": "CallbackMetadata or Item missing"}), 400

        amount = next((item['Value'] for item in items if item['Name'] == 'Amount'), None)
        if amount is None:
            return jsonify({"error": "'Amount' not found in CallbackMetadata"}), 400

        # Handle the callback data as needed
        return jsonify({"amount": amount}), 200

    except Exception as e:
        logging.error(f"Error processing callback: {e}")
        return jsonify({"error": "Internal server error"}), 500



class PaymentSummaryResource(Resource):
    def get(self):
        try:
            total_paid = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
            return {'total_paid': total_paid}, 200
        except Exception as e:
            app.logger.error(f"Error fetching payment summary: {e}")
            return {'error': 'Failed to fetch payment summary'}, 500

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
        


valid_categories = [
    'html', 'css', 'javascript', 'react', 'redux', 'typescript', 'node.js', 'express',
    'mongoDB', 'sql', 'python', 'django', 'flask', 'ruby', 'rails', 'php', 'laravel', 'java', 'spring'
]

class QuestionsPost(Resource):

    def post(self, category):
        try:
            if category not in valid_categories:
                return make_response({"message": "Invalid category"}, 400)

            data = request.json
            if not data or not isinstance(data, dict):
                return make_response({"message": "Invalid JSON data"}, 400)

            question_text = data.get("question_text")
            options = data.get("options")
            correct_answer = data.get("correct_answer")

            if not question_text or not options or not correct_answer:
                return make_response({"message": "Missing required fields"}, 400)

            new_question = Question(
                question_text=question_text,
                category=category,
                options=json.dumps(options),
                correct_answer=correct_answer
            )
            db.session.add(new_question)
            db.session.commit()
            return make_response({"question": new_question.as_dict(), "message": "Question created successfully"}, 201)
        except Exception as e:
            logging.error(f"Error creating question: {e}")
            return make_response({"message": "An error occurred"}, 500)


@app.route('/questions/<category>', methods=['POST'])
def add_question(category):
    if category not in valid_categories:
        return jsonify({"message": "Invalid category"}), 400

    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400
    if not all(k in data for k in ("question_text", "options", "correct_answer")):
        return jsonify({"message": "Missing required fields"}), 400

    try:
        new_question = Question(
            question_text=data["question_text"],
            category=category,
            options=json.dumps(data["options"]),
            correct_answer=data["correct_answer"]
        )
        db.session.add(new_question)
        db.session.commit()
        return jsonify({"question": new_question.as_dict(), "message": "Question created successfully"}), 201
    except Exception as e:
        return jsonify({"message": "An error occurred", "details": str(e)}), 500


class QuestionsGet(Resource):
    valid_categories = ['HTML', 'CSS', 'javascript', 'react', 'redux', 'typescript', 'node', 'express',
                        'mongodb', 'sql', 'python', 'django', 'flask', 'ruby', 'rails', 'php', 'laravel', 'java', 'spring']

    def get(self, category):
        try:
            if category not in valid_categories:
                return make_response({"message": "Invalid category"}, 400)

            questions = Question.query.filter_by(category=category).all()
            if not questions:
                return make_response({"message": "No questions found for this category"}, 404)

            questions_list = [question.as_dict() for question in questions]
            return make_response({"questions": questions_list}, 200)
        except Exception as e:
            logging.error(f"Error fetching questions: {e}")
            return make_response({"message": "An error occurred"}, 500)

@app.route('/save-quiz-result', methods=['POST'])
def save_quiz_result():
    data = request.json
    try:
        quiz_result = QuizResult(
            user_id=data['user_id'],
            category=data['category'],
            score=data['score'],
            total_questions=data['total_questions'],
            answers=data['answers'],  
            date_taken=datetime.utcnow()
        )
        db.session.add(quiz_result)
        db.session.commit()
        return jsonify({"message": "Quiz result saved successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
@app.route('/get-all-quiz-results', methods=['GET'])
def get_all_quiz_results():
    try:
        quiz_results = QuizResult.query.all()
        return jsonify([result.as_dict() for result in quiz_results]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/courses/<int:id>/archive', methods=['PUT'])
def archive_course(id):
    course = Course.query.get_or_404(id)
    course.archive()
    return jsonify({"message": f"Course with ID {id} has been archived."}), 200

@app.route('/courses/<int:id>/unarchive', methods=['PUT'])
def unarchive_course(id):
    course = Course.query.get_or_404(id)
    course.unarchive()
    return jsonify({"message": f"Course with ID {id} has been unarchived."}), 200

@app.route('/courses', methods=['GET'])
def get_courses():
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    if active_only:
        courses = Course.query.filter_by(is_active=True).all()
    else:
        courses = Course.query.all()
    return jsonify([course.as_dict() for course in courses])

@app.route('/courses/count', methods=['GET'])
def count_active_courses():
    try:
        
        count = Course.query.filter_by(is_active=True).count()
        return jsonify({"count": count}), 200
    except SQLAlchemyError as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
    except Exception as e:
        app.logger.error(f"General error: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


class ProCourseResource(Resource):
    def get(self, course_id=None):
        """Get a single pro course or all pro courses."""
        if course_id:
            # Get a specific pro course
            course = ProCourse.query.get(course_id)
            if not course:
                return {'message': 'Pro course not found'}, 404
            course_data = {
                'title': course.title,
                'description': course.description,
                'video': course.video,
                'image': course.image,
                'techStack': course.tech_stack.split(',') if course.tech_stack else [],
                'whatYouWillLearn': json.loads(course.what_you_will_learn) if course.what_you_will_learn else [],
                'is_active': course.is_active,
                'requires_subscription': course.requires_subscription
            }
            return {'course': course_data}, 200
        else:
            # Get all pro courses
            pro_courses = ProCourse.query.filter_by(requires_subscription=True).all()
            courses_list = [{
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'video': course.video,
                'image': course.image,
                'techStack': course.tech_stack.split(',') if course.tech_stack else [],
                'whatYouWillLearn': json.loads(course.what_you_will_learn) if course.what_you_will_learn else [],
                'is_active': course.is_active,
                'requires_subscription': course.requires_subscription
            } for course in pro_courses]
            return {'courses': courses_list}, 200

    def post(self):
        """Create a new pro course."""
        data = request.get_json()
        if not data:
            return {'error': 'No data provided'}, 400

        new_course = ProCourse(
            title=data.get('title'),
            description=data.get('description'),
            video=data.get('video'),
            image=data.get('image'),
            tech_stack=','.join(data.get('techStack', [])),
            what_you_will_learn=json.dumps(data.get('whatYouWillLearn', [])),
            is_active=data.get('is_active', True),
            requires_subscription=True
        )
        db.session.add(new_course)
        db.session.commit()
        return {'course': {
            'id': new_course.id,
            'title': new_course.title,
            'description': new_course.description,
            'video': new_course.video,
            'image': new_course.image,
            'techStack': new_course.tech_stack.split(','),
            'whatYouWillLearn': json.loads(new_course.what_you_will_learn),
            'is_active': new_course.is_active,
            'requires_subscription': new_course.requires_subscription
        }}, 201
        
    def delete(self, course_id):
        """Delete a pro course."""
        course = ProCourse.query.get(course_id)
        if not course:
            return {'message': 'Pro course not found'}, 404

        db.session.delete(course)
        db.session.commit()
        return {'message': 'Pro course deleted successfully'}, 200


    
api.add_resource(Users, '/users')
api.add_resource(Login, '/login')
api.add_resource(VerifyToken, '/verify-token')
api.add_resource(Courses, '/courses')
api.add_resource(SubscriptionResource,'/subscribe')
api.add_resource(QuestionsGet, '/questions/<category>')
app.register_blueprint(course_bp, url_prefix='/courses') 
api.add_resource(PaymentSummaryResource, '/payment-summary')
api.add_resource(ProCourseResource, '/pro-courses', '/pro-courses/<int:course_id>')
app.register_blueprint(pro_course_bp, url_prefix='/pro-courses')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    