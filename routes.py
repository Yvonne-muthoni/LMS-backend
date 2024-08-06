from flask import Blueprint, request, jsonify
from app import db
from models import Course
import json
import random
import requests

course_bp = Blueprint('courses', __name__)

# Helper function to get video details from YouTube
def get_youtube_video_details(video_url):
    video_id = video_url.split('v=')[-1]
    api_key = 'AIzaSyAuu1LOJKCFPEg1dXLAYgL5DrUOFgSMbP4'  # Replace with your actual YouTube API key
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

# Helper function to generate random tech stack
def generate_tech_stack():
    techs = ['Python', 'JavaScript', 'React', 'Node.js', 'Flask', 'Django', 'Vue.js', 'Angular', 'Express', 'MongoDB', 'PostgreSQL', 'Docker', 'Kubernetes', 'AWS', 'Google Cloud', 'Azure']
    return random.sample(techs, random.randint(3, 6))

# Helper function to generate random learning outcomes
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
    
    course.video = video_url
    course.tech_stack = ','.join(data.get('techStack', course.tech_stack.split(',')))
    course.what_you_will_learn = json.dumps(data.get('whatYouWillLearn', json.loads(course.what_you_will_learn)))
    
    db.session.commit()
    return jsonify(course.as_dict())

@course_bp.route('/<int:id>', methods=['DELETE'])
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return '', 204