from flask import Blueprint, request, jsonify
from utils.openai_client import client
from config.config import load_config
from utils.connect_db import get_db_connection

homepage_bp = Blueprint('homepage', __name__)
config = load_config()

conn = get_db_connection()
cursor = conn.cursor()

@homepage_bp.route('/retrieve_homepage_data', methods=['POST'])
def retrieve_homepage_data():
    num_courses = request.json.get('num_courses', 10)
    order_by = request.json.get('order_by', 'class_name')
    search_query = request.json.get('search_query', None)
    # order_by options: class_name, highest_avg_course_rating, highest_avg_hours_per_week, highest_avg_instruction_rating, lowest_avg_course_rating, lowest_avg_hours_per_week, lowest_avg_instruction_rating

    data_requirements = request.json.get('data_requirements', None)
    # data_requirements format: {"hours_max": 10, "hours_min": 0, "rating_max": 5, "rating_min": 0, "instruction_rating_max": 5, "instruction_rating_min": 0}
    
    try:
        # Base query with filtering
        base_query = """
            SELECT 
                course_number,
                name,
                AVG(overall_rating_course) AS avg_course_rating,
                AVG(avg_hours) AS avg_hours_per_week,
                AVG(overall_rating_instruction) AS avg_instruction_rating
            FROM Courses
            WHERE course_number IS NOT NULL
        """

        params = []
        if search_query:
            base_query += " AND (LOWER(name) LIKE LOWER(%s) OR LOWER(course_number) LIKE LOWER(%s))"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param])
        
        base_query += " GROUP BY course_number, name"
        
        # Add WHERE clauses if data_requirements exist
        if data_requirements:
            where_clauses = []
            if 'hours_min' in data_requirements:
                where_clauses.append("AVG(avg_hours) >= %s")
            if 'hours_max' in data_requirements:
                where_clauses.append("AVG(avg_hours) <= %s")
            if 'rating_min' in data_requirements:
                where_clauses.append("AVG(overall_rating_course) >= %s")
            if 'rating_max' in data_requirements:
                where_clauses.append("AVG(overall_rating_course) <= %s")
            if 'instruction_rating_min' in data_requirements:
                where_clauses.append("AVG(overall_rating_instruction) >= %s")
            if 'instruction_rating_max' in data_requirements:
                where_clauses.append("AVG(overall_rating_instruction) <= %s")
            
            if where_clauses:
                base_query += " HAVING " + " AND ".join(where_clauses)
        
        # Handle different order_by options
        order_clause = "ORDER BY "
        if order_by == 'class_name':
            order_clause += "name ASC"
        elif order_by == 'highest_avg_course_rating':
            order_clause += "avg_course_rating DESC"
        elif order_by == 'lowest_avg_course_rating':
            order_clause += "avg_course_rating ASC"
        elif order_by == 'highest_avg_hours_per_week':
            order_clause += "avg_hours_per_week DESC"
        elif order_by == 'lowest_avg_hours_per_week':
            order_clause += "avg_hours_per_week ASC"
        elif order_by == 'highest_avg_instruction_rating':
            order_clause += "avg_instruction_rating DESC"
        elif order_by == 'lowest_avg_instruction_rating':
            order_clause += "avg_instruction_rating ASC"
        else:
            order_clause += "name ASC"  # default fallback
        
        base_query += " " + order_clause + " LIMIT %s"
        
        # Prepare parameters for the query
        if data_requirements:
            if 'hours_min' in data_requirements:
                params.append(data_requirements['hours_min'])
            if 'hours_max' in data_requirements:
                params.append(data_requirements['hours_max'])
            if 'rating_min' in data_requirements:
                params.append(data_requirements['rating_min'])
            if 'rating_max' in data_requirements:
                params.append(data_requirements['rating_max'])
            if 'instruction_rating_min' in data_requirements:
                params.append(data_requirements['instruction_rating_min'])
            if 'instruction_rating_max' in data_requirements:
                params.append(data_requirements['instruction_rating_max'])
        params.append(num_courses)
        
        cursor.execute(base_query, tuple(params))
        homepage_data = cursor.fetchall()
        
        # Format the response
        formatted_data = []
        for row in homepage_data:
            formatted_data.append({
                "course_number": row[0],
                "name": row[1],
                "avg_course_rating": float(row[2]) if row[2] is not None else None,
                "avg_hours_per_week": float(row[3]) if row[3] is not None else None,
                "avg_instruction_rating": float(row[4]) if row[4] is not None else None
            })
        
        return jsonify(formatted_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
