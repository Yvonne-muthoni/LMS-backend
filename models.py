from database import db

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique= True, nullable= False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String)
    status = db.Column(db.String, nullable=False)

    user_id = db.column(db.Integer, db.ForeignKey('user.id'), nullable = False)


    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'status': self.status,
            'user_id': self.user_id

        }

