
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Course, User, Question, ProCourse
from flask_bcrypt import Bcrypt
import json
import random
import requests

bcrypt = Bcrypt()

course_bp = Blueprint('courses', __name__)
pro_course_bp = Blueprint('pro_courses', __name__)

def get_youtube_video_details(video_url):
    video_id = video_url.split('v=')[-1]
    api_key = 'AIzaSyAOnd-vRPTtOlNJNLiPKICI865oY-LkxdU'  
    api_url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}'    
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            snippet = data['items'][0]['snippet']
            return {
                'title': snippet['title'],
                'description': snippet['description'],
                'thumbnail': snippet['thumbnails']['high']['url']
            }
    return None

def generate_tech_stack():
    techs = ['Python', 'JavaScript', 'React', 'Node.js', 'Flask', 'Django', 'Vue.js', 'Angular', 'Express', 'MongoDB', 'PostgreSQL', 'Docker', 'Kubernetes', 'AWS', 'Google Cloud', 'Azure']
    return random.sample(techs, random.randint(3, 6))

def generate_learning_outcomes():
    outcomes = [
        "Build responsive web applications",
        "Implement RESTful APIs",
        "Design efficient database schemas",
        "Deploy applications to cloud platforms",
        "Implement authentication and authorization",
        "Optimize application performance",
        "Write clean and maintainable code",
        "Use version control effectively",
        "Implement automated testing",
        "Apply best practices in software development"
    ]
    return random.sample(outcomes, random.randint(4, 7))

@course_bp.route('/', methods=['POST'])
def add_course():
    data = request.json
    video_url = data.get('video', '')
    video_details = get_youtube_video_details(video_url) if video_url else None

    course = Course(
        title=video_details['title'] if video_details else data.get('title', ''),
        description=video_details['description'] if video_details else data.get('description', ''),
        image=video_details['thumbnail'] if video_details else data.get('image', ''),
        video=video_url,
        tech_stack=','.join(generate_tech_stack()),
        what_you_will_learn=json.dumps(generate_learning_outcomes())
    )
    db.session.add(course)
    db.session.commit()
    return jsonify(course.as_dict()), 201

@course_bp.route('/', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([course.as_dict() for course in courses])

@course_bp.route('/<int:id>', methods=['GET'])
def get_course(id):
    course = Course.query.get_or_404(id)
    return jsonify(course.as_dict())

@course_bp.route('/<int:id>', methods=['PUT'])
def update_course(id):
    course = Course.query.get_or_404(id)
    data = request.json
    
    video_url = data.get('video', course.video)
    if video_url != course.video:
        video_details = get_youtube_video_details(video_url)
        if video_details:
            course.title = video_details['title']
            course.description = video_details['description']
            course.image = video_details['thumbnail']

    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    course.image = data.get('image', course.image)
    course.video = video_url
    course.tech_stack = ','.join(generate_tech_stack())
    course.what_you_will_learn = json.dumps(generate_learning_outcomes())
    
    db.session.commit()
    return jsonify(course.as_dict())


@pro_course_bp.route('/', methods=['POST'])
def add_pro_course():
    data = request.json
    video_url = data.get('video', '')
    video_details = get_youtube_video_details(video_url) if video_url else None

    pro_course = ProCourse(
        title=video_details['title'] if video_details else data.get('title', ''),
        description=video_details['description'] if video_details else data.get('description', ''),
        image=video_details['thumbnail'] if video_details else data.get('image', ''),
        video=video_url,
        tech_stack=','.join(generate_tech_stack()),
        what_you_will_learn=json.dumps(generate_learning_outcomes()),
        is_active=data.get('is_active', True),
        requires_subscription=True  # Pro courses should require a subscription by default
    )
    db.session.add(pro_course)
    db.session.commit()
    return jsonify(pro_course.as_dict()), 201

@pro_course_bp.route('/', methods=['GET'])
def get_pro_courses():
    pro_courses = ProCourse.query.filter_by(requires_subscription=True).all()
    return jsonify([pro_course.as_dict() for pro_course in pro_courses])

@pro_course_bp.route('/<int:id>', methods=['GET'])
def get_pro_course(id):
    pro_course = ProCourse.query.get_or_404(id)
    return jsonify(pro_course.as_dict())

@pro_course_bp.route('/<int:id>', methods=['PUT'])
def update_pro_course(id):
    pro_course = ProCourse.query.get_or_404(id)
    data = request.json
    
    video_url = data.get('video', pro_course.video)
    if video_url != pro_course.video:
        video_details = get_youtube_video_details(video_url)
        if video_details:
            pro_course.title = video_details['title']
            pro_course.description = video_details['description']
            pro_course.image = video_details['thumbnail']

    pro_course.title = data.get('title', pro_course.title)
    pro_course.description = data.get('description', pro_course.description)
    pro_course.image = data.get('image', pro_course.image)
    pro_course.video = video_url
    pro_course.tech_stack = ','.join(generate_tech_stack())
    pro_course.what_you_will_learn = json.dumps(generate_learning_outcomes())
    pro_course.is_active = data.get('is_active', pro_course.is_active)
    
    db.session.commit()
    return jsonify(pro_course.as_dict())

@pro_course_bp.route('/<int:id>', methods=['DELETE'])
def delete_pro_course(id):
    pro_course = ProCourse.query.get_or_404(id)
    db.session.delete(pro_course)
    db.session.commit()
    return jsonify({'message': 'Pro course deleted successfully'})