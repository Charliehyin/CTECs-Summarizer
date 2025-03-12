import mysql.connector
import html  # Import for decoding HTML entities

conn = mysql.connector.connect(
    host="ctecdb.cl6gmcm2s7td.us-east-2.rds.amazonaws.com", 
    user="admin",      
    password="ctecparser123",  
    database="ctecdb"
)
cursor = conn.cursor()

cursor.execute("""
    SELECT course_name, instructor, quarter, avg_hours, overall_rating_instruction, 
           overall_rating_course, learned_rating, challenge_effectiveness, instructor_stimulating
    FROM Courses
""")
courses = cursor.fetchall()

with open("course_summary.txt", "w", encoding="utf-8") as f:
    for course in courses:
        # Decode any HTML entities in course name and instructor
        course_name = html.unescape(course[0])  # Fixes &#44; to ,
        instructor = html.unescape(course[1])
        quarter = course[2]
        avg_hours, instruction_rating, course_rating, learned_rating, challenge_effectiveness, instructor_stimulating = course[3:]

        summary = (
            f"{course_name}, taught by {instructor} during {quarter}. "
            f"Average weekly hours spent: {avg_hours}. "
            f"Average score for professor instruction: {instruction_rating}. "
            f"Average score for course overall: {course_rating}. "
            f"Average score for how much students learned: {learned_rating}. "
            f"Average score for challenge effectiveness: {challenge_effectiveness}. "
            f"Average score for instructor stimulation: {instructor_stimulating}.\n"
        )

        f.write(summary)

cursor.close()
conn.close()
