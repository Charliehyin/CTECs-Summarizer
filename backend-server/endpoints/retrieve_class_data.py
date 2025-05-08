from flask import Blueprint, request, jsonify
from utils.openai_client import client
from config.config import load_config
from utils.connect_db import get_db_connection

class_data_bp = Blueprint('class_data', __name__)
config = load_config()

@class_data_bp.route('/retrieve_class_data', methods=['POST'])
def retrieve_class_data():
    course_number = request.json.get('course_number', None)
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # Use buffered cursor

        # Get the aggregated course data
        base_query = """
            SELECT 
                course_number,
                name,
                AVG(overall_rating_course) AS avg_course_rating,
                AVG(avg_hours) AS avg_hours_per_week,
                AVG(overall_rating_instruction) AS avg_instruction_rating,
                AVG(learned_rating) AS avg_learned_rating,
                AVG(challenge_effectiveness) AS avg_challenge_effectiveness,
                AVG(instructor_stimulating) AS avg_instructor_stimulating
            FROM Courses
            WHERE course_number = %s
            GROUP BY course_number, name
        """
        
        cursor.execute(base_query, (course_number,))
        course_data = cursor.fetchone()
        
        if not course_data:
            return jsonify({"error": "Course not found"}), 404
            
        # Get individual course instances
        instances_query = """
            SELECT 
                course_id,
                instructor,
                quarter,
                year,
                overall_rating_course,
                avg_hours,
                overall_rating_instruction,
                learned_rating,
                challenge_effectiveness,
                instructor_stimulating
            FROM Courses
            WHERE course_number = %s
            ORDER BY quarter DESC
        """
        
        cursor.execute(instances_query, (course_number,))
        instances = cursor.fetchall()
        
        # Get essays for each course instance
        essays_query = """
            SELECT 
                course_id,
                response
            FROM Course_Essays
            WHERE course_id IN (%s)
        """
        
        # Create a list of course_ids for the IN clause
        course_ids = [instance[0] for instance in instances]
        if course_ids:
            # Create the proper number of %s for the IN clause
            placeholders = ','.join(['%s'] * len(course_ids))
            cursor.execute(essays_query % placeholders, tuple(course_ids))
            essays = cursor.fetchall()
            
            # Create a dictionary of essays by course_id
            essays_by_course = {}
            for course_id, essay in essays:
                if course_id not in essays_by_course:
                    essays_by_course[course_id] = []
                essays_by_course[course_id].append(essay)
        else:
            essays_by_course = {}
        
        # Format the response
        formatted_data = {
            "course_number": course_data[0],
            "name": course_data[1],
            "avg_course_rating": float(course_data[2]) if course_data[2] is not None else None,
            "avg_hours_per_week": float(course_data[3]) if course_data[3] is not None else None,
            "avg_instruction_rating": float(course_data[4]) if course_data[4] is not None else None,
            "avg_learned_rating": float(course_data[5]) if course_data[5] is not None else None,
            "avg_challenge_effectiveness": float(course_data[6]) if course_data[6] is not None else None,
            "avg_instructor_stimulating": float(course_data[7]) if course_data[7] is not None else None,
            "instances": []
        }
        
        # Add individual course instances
        for instance in instances:
            instance_data = {
                "course_id": instance[0],
                "professor": instance[1],
                "quarter_taught": instance[2],
                "year": instance[3],
                "course_rating": float(instance[4]) if instance[4] is not None else None,
                "hours": float(instance[5]) if instance[5] is not None else None,
                "instruction_rating": float(instance[6]) if instance[6] is not None else None,
                "learned_rating": float(instance[7]) if instance[7] is not None else None,
                "challenge_effectiveness": float(instance[8]) if instance[8] is not None else None,
                "instructor_stimulating": float(instance[9]) if instance[9] is not None else None,
                "essays": essays_by_course.get(instance[0], [])
            }
            formatted_data["instances"].append(instance_data)
        
        return jsonify(formatted_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
