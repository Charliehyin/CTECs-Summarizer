import mysql.connector
import html  # Import for decoding HTML entities

# **MySQL Database Connection**
conn = mysql.connector.connect(
    host="ctecdb.cl6gmcm2s7td.us-east-2.rds.amazonaws.com", 
    user="admin",      
    password="ctecparser123",  
    database="ctecdb"
)
cursor = conn.cursor()

# **Fetch essays with course details, including the year**
cursor.execute("""
    SELECT c.course_name, c.instructor, c.quarter, c.year, ce.response 
    FROM Course_Essays ce
    JOIN Courses c ON ce.course_id = c.course_id
    ORDER BY c.course_name
""")
essays = cursor.fetchall()

# **Write essays to file**
with open("course_essays.txt", "w", encoding="utf-8") as f:
    for course_name, instructor, quarter, year, response in essays:
        # **Decode HTML entities and format course name**
        course_name = html.unescape(course_name).replace("_", " ").replace("-", " ")  # Fix underscores/dashes
        instructor = html.unescape(instructor)
        quarter = html.unescape(quarter)
        year = str(year)  # Convert year to string
        response = html.unescape(response)

        # **Write each response with full course details (INCLUDING YEAR)**
        f.write(f"{course_name}, taught by {instructor}, during {quarter} {year}: {response}\n")

cursor.close()
conn.close()
print("Course essays file updated successfully!")
