from app import db
import json

class Course(db.Model):
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
