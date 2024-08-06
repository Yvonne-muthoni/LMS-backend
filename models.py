from app import db
import json

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    video = db.Column(db.String(255), nullable=True)
    tech_stack = db.Column(db.String(255), nullable=True)  # Store as comma-separated values
    what_you_will_learn = db.Column(db.Text, nullable=True)  # Store as JSON string

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'video': self.video,
            'techStack': self.tech_stack.split(',') if self.tech_stack else [],
            'whatYouWillLearn': json.loads(self.what_you_will_learn) if self.what_you_will_learn else []
        }