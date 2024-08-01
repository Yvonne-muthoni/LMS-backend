from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Subscription

class SubscriptionResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        subscription_id = request.json.get('subscription_id')
        subscription = Subscription.query.get(subscription_id)

        if not subscription:
            return make_response({"message": "Subscription not found"}, 400)
        
        if subscription in current_user.subscription:
            return make_response({"message": "Already subscribed"}, 400)
        
        current_user.subscriptions.append(subscription)
        db.session.commit()

        return make_response({"message": "Subscribed successfully"}, 201)
    

    @jwt_required()
    def delete(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        subscription_id = request.json.get('subscription_id')
        subscription = Subscription.query.get(subscription_id)

        if not subscription:
            return make_response({"message": "subscribtion not found"}, 404)
        
        if subscription not in current_user.subscription:
            return make_response({"message": "Not subscribed"}, 400)
        
        current_user.subscriptions.remove(subscription)
        db.session.commit()

        return make_response({"message": "Unsubscribed successfully"}, 200)
    

class SubscriptionAnalytics(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity
        current_user = User.query.get(current_user_id)


        total_subscriptions = Subscription.query.count()
        active_subscriptions = Subscription.query.filter_by(status='active').count()

        analytics = {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": total_subscriptions,
            "user_subscriptions_count": len(current_user.subscriptions)
        }

        return make_response(jsonify(analytics), 200)



    

