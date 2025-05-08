from flask import Blueprint, request, jsonify
from utils.openai_client import client
from config.config import load_config
from utils.connect_db import get_db_connection

homepage_bp = Blueprint('homepage', __name__)
config = load_config()

conn = get_db_connection()
cursor = conn.cursor()

@homepage_bp.route('/retrieve_homepage_data', methods=['GET'])
def retrieve_homepage_data():
    num_courses = request.args.get('num_courses', 10, type=int)
    order_by = request.args.get('order_by', 'class_name')
    
    try:
        cursor.execute("""
                       SELECT 
                       course_name,
                       AVG(overall_rating_course) AS avg_course_rating,
                       AVG(avg_hours) AS avg_hours_per_week,
                       AVG(overall_rating_instruction) AS avg_instruction_rating,
                       course_id
                       FROM Courses
                       GROUP BY course_name
                       ORDER BY %s
                       LIMIT %s
                       """, (order_by, num_courses))
        homepage_data = cursor.fetchall()
        return jsonify(homepage_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
