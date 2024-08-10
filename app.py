from dotenv import load_dotenv
import base64
from datetime import datetime
import os
from models import db, User, Subscription, Payment
import logging
from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import json
import random
import requests
from routes import course_bp


load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret"



logging.basicConfig(level=logging.DEBUG)


CORS(app, resources={r"/*": {"origins": "*"}})

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)
api = Api(app)


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
        json_response = response.json()
        return json_response['access_token']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting access token: {e}")
        raise Exception(f"Error getting access token: {e}")

def generate_password(shortcode, passkey):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = f"{shortcode}{passkey}{timestamp}"
    encoded_string = base64.b64encode(data_to_encode.encode())
    return encoded_string.decode('utf-8'), timestamp
class SubscriptionResource(Resource):
    def initiate_mpesa_payment(self, user_id, amount, phone_number):
        # Create payment record
        payment = Payment(user_id=user_id, amount=amount, phone_number=phone_number)
        db.session.add(payment)
        db.session.commit()

        # Initiate M-Pesa payment
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
            "CallBackURL": "https://0688-105-163-157-135.ngrok-free.app/callback",
            "AccountReference": "SubscriptionPayment",
            "TransactionDesc": "Subscription payment"
        }

        try:
            response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                headers=headers,
                json=payload
            )
            response_data = response.json()
            logging.debug(f"M-Pesa response: {response_data}")
        except requests.exceptions.RequestException as e:
            logging.error(f'Error calling M-Pesa API: {e}')
            return {'error': 'Failed to connect to M-Pesa API'}, 500
        except ValueError:
            logging.error(f'Invalid JSON response: {response.text}')
            return {'error': 'Invalid response from M-Pesa API'}, 500

        if response_data.get('ResponseCode') == '0':
            payment.transaction_id = response_data['CheckoutRequestID']
            payment.status = 'initiated'
            db.session.commit()
            return {'message': 'Payment initiated successfully'}, 201
        else:
            return {'error': 'Failed to initiate payment'}, 400

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
            app.logger.error('Phone number is missing from the request data')
            return {'error': 'Phone number is required'}, 400
    
        # Create subscription record before initiating payment
        subscription = Subscription(user_id=user.id, amount=amount)
        db.session.add(subscription)
        db.session.commit()

        # Prepare payment data
        payment_response = self.initiate_mpesa_payment(user_id, amount, phone_number)

        # Check the status code of the payment response
        if payment_response[1] != 201:
            return {'error': 'Failed to initiate payment'}, 400

        return {
            'message': 'Subscription created and payment initiated successfully',
            'subscription_id': subscription.id,
            'payment_response': payment_response
        }, 201



@app.route('/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()
    if not data:
        return jsonify({"ResultCode": 1, "ResultDesc": "No data received"}), 400

    try:
        stk_callback = data['Body']['stkCallback']
        checkout_request_id = stk_callback['CheckoutRequestID']
        result_code = stk_callback['ResultCode']
        result_desc = stk_callback['ResultDesc']
    except KeyError as e:
        return jsonify({"ResultCode": 1, "ResultDesc": "Invalid data format"}), 400

    payment = Payment.query.filter_by(transaction_id=checkout_request_id).first()
    if payment:
        if result_code == 0:
            payment.status = 'completed'
        else:
            payment.status = 'failed'
        payment.result_desc = result_desc
        payment.timestamp = datetime.now()
        db.session.commit()
        return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200
    else:
        return jsonify({"ResultCode": 1, "ResultDesc": "Payment record not found"}), 404


    
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

class QuestionsPost(Resource):
    def post(self):
        try:
            data = request.json
            new_question = Question(
                question_text=data.get("question_text"),
                category=data.get("category"),
                options=json.dumps(data.get("options")),  
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
api.add_resource(QuestionsGet, '/questions/<string:category>')  
api.add_resource(QuestionsPost, '/questions')  
api.add_resource(SubscriptionResource, '/subscribe')


app.register_blueprint(course_bp, url_prefix='/courses') 



if __name__ == '__main__':
    app.run(debug=True)
    CORS(app)
