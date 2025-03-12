import os
import mysql.connector
import pandas as pd
from bs4 import BeautifulSoup
import re

# MySQL Database Connection
conn = mysql.connector.connect(
    host="ctecdb.cl6gmcm2s7td.us-east-2.rds.amazonaws.com", 
    user="admin",      
    password="ctecparser123",  
    database="ctecdb"
)
cursor = conn.cursor()

# Path to the COMP_SCI folder (now containing all HTML files)
html_folder = r"C:\Users\jacob\Downloads\COMP_SCI"  # Change this to your actual path

# Reset the database
cursor.execute("DROP TABLE IF EXISTS Course_Essays")
cursor.execute("DROP TABLE IF EXISTS Courses")

# Recreate tables
cursor.execute("""
CREATE TABLE Courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    instructor VARCHAR(255) NOT NULL,
    quarter VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    avg_hours DECIMAL(4,2) NOT NULL,
    overall_rating_instruction DECIMAL(4,2) NOT NULL,
    overall_rating_course DECIMAL(4,2) NOT NULL,
    learned_rating DECIMAL(4,2) NOT NULL,
    challenge_effectiveness DECIMAL(4,2) NOT NULL,
    instructor_stimulating DECIMAL(4,2) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE Course_Essays (
    essay_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    response TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
)
""")

conn.commit()

def parse_ctec_html(html_path):
    """Parses a single HTML file and inserts data into MySQL."""
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    text = soup.get_text("\n")

    # Extract course name and instructor
    header_match = re.search(r"Student Report for (.+?)\s*\((['\-\w\sA-Za-zÀ-ÖØ-öø-ÿ]*?)\)\n", text)
    instructor = header_match.group(2).strip() if header_match else "Unknown Instructor"
    course_name = header_match.group(1).strip() if header_match else "Unknown Course"

    # Extract quarter and year
    quarter_year_match = re.search(r"CTEC (\w+) (\d{4})", text)
    if quarter_year_match:
        quarter, year = quarter_year_match.groups()
        year = int(year)
    else:
        quarter, year = "Unknown", 0

    # **Calculate Average Weekly Hours**
    time_survey_match = re.search(
        r"Estimate the average number of hours per week.*?Options\s+Count\s+Percentage(.*?)ESSAY QUESTIONS",
        text, re.DOTALL
    )

    avg_hours = 0
    if time_survey_match:
        time_survey_text = time_survey_match.group(1).strip()
        cleaned_lines = []
        raw_lines = time_survey_text.split("\n")

        for i in range(len(raw_lines) - 2):
            if raw_lines[i].strip() in ["3 or fewer", "4 - 7", "8 - 11", "12 - 15", "16 - 19", "20 or more"]:
                cleaned_lines.append(f"{raw_lines[i].strip()} {raw_lines[i+1].strip()} {raw_lines[i+2].strip()}")

        time_ranges = {
            "3 or fewer": 1.5,
            "4 - 7": 5.5,
            "8 - 11": 9.5,
            "12 - 15": 13.5,
            "16 - 19": 17.5,
            "20 or more": 20.0
        }

        weighted_sum = 0
        total_percentage = 0

        for line in cleaned_lines:
            match = re.match(r"(3 or fewer|4 - 7|8 - 11|12 - 15|16 - 19|20 or more) (\d+) ([\d.]+)%", line.strip())
            if match:
                range_label, count, percentage = match.groups()
                percentage = float(percentage) / 100  
                weighted_sum += time_ranges[range_label] * percentage
                total_percentage += percentage

        avg_hours = round(weighted_sum / total_percentage, 2) if total_percentage > 0 else 0

    # **Extract Course Ratings**
    course_questions_match = re.search(r"COURSE QUESTIONS(.*?)TIME-SURVEY QUESTION", text, re.DOTALL)
    if course_questions_match:
        ratings = re.findall(r"Mean\s+([\d.]+)", course_questions_match.group(1))
        if len(ratings) >= 5:
            overall_rating_instruction, overall_rating_course, learned_rating, challenge_effectiveness, instructor_stimulating = map(float, ratings[:5])
        else:
            overall_rating_instruction = overall_rating_course = learned_rating = challenge_effectiveness = instructor_stimulating = 0
    else:
        overall_rating_instruction = overall_rating_course = learned_rating = challenge_effectiveness = instructor_stimulating = 0

    # **Insert Course Data into MySQL**
    cursor.execute("""
        INSERT INTO Courses (course_name, instructor, quarter, year, avg_hours, overall_rating_instruction, overall_rating_course, learned_rating, challenge_effectiveness, instructor_stimulating) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (course_name, instructor, quarter, year, avg_hours, overall_rating_instruction, overall_rating_course, learned_rating, challenge_effectiveness, instructor_stimulating))
    
    conn.commit()
    course_id = cursor.lastrowid

    # **Extract and Insert Essay Responses**
    essays_match = re.search(r"ESSAY QUESTIONS(.*?)DEMOGRAPHICS", text, re.DOTALL)
    if essays_match:
        raw_essays = essays_match.group(1)
        raw_essays = re.sub(r"^.*?Comments", "", raw_essays, flags=re.DOTALL)
        lines = raw_essays.strip().split('\n')
        current_comment = ""
        essays = []

        for line in lines:
            line = line.strip()
        
            # **Skip unwanted entries**
            if not line or line in ["Back | Top of Page", "Back | Top"]:  # Ensure this line is removed
                continue
        
            if current_comment:
                current_comment += " " + line
            else:
                current_comment = line

            if re.search(r'[.!?]$', line):  # Check if the line ends a complete sentence
                essays.append(current_comment.strip())
                current_comment = ""

        if current_comment:
            essays.append(current_comment.strip())

        # **Insert only valid essay responses**
        for essay in essays:
            if essay and essay not in ["Back | Top of Page", "Back | Top"]:  # Extra safety check
                cursor.execute(
                    "INSERT INTO Course_Essays (course_id, response) VALUES (%s, %s)",
                    (course_id, essay)
                )

    conn.commit()

# **Process all HTML files in the COMP_SCI folder (NO subfolders)**
html_files = [f for f in os.listdir(html_folder) if f.endswith(".html")]

for html_file in html_files:
    file_path = os.path.join(html_folder, html_file)
    print(f"Processing: {file_path}")
    parse_ctec_html(file_path)

cursor.close()
conn.close()
print("All HTML files in COMP_SCI processed successfully!")
