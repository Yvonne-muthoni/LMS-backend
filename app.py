from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from config import Config
from database import db
from routes import SubscriptionResource, SubscriptionAnalytics

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'


db.init_app(app)
api = Api(app)

api.add_resource(SubscriptionResource, '/subscriptions')
api.add_resource(SubscriptionAnalytics, '/analytics')


with app.app_context():
    db.create_all()


if __name__ == '__main_':
    app.run(debug=True)
   