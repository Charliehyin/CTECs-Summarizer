import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.connect_db import get_db_connection

def expand_course_names():
    expansions = {
        "Digital Forensics and Incident": "Digital Forensics and Incident Response",
        "Dig Forensics & Incident Respo": "Digital Forensics and Incident Response",
        "CC": "Compiler Construction",
        "CAT": "Code Analysis and Transformation",
        "Fund Comp Prog": "Fundamentals of Computer Programming",
        "Tools and Tech WWW": "Tools and Technologies of the World Wide Web",
        "Fund of Computer Prog 1.5": "Fundamentals of Computer Programming 1.5",
        "Fundmtls of Computer Prog II": "Fundamentals of Computer Programming II",
        "Mathematical Found of Comp Sci": "Mathematical Foundations of Computer Science",
        "Data Mgmt / Info Proc": "Data Management and Information Processing",
        "Intro to the Data Science Pipe": "Introduction to the Data Science Pipeline",
        "Generative Methods": "Generative Methods for Interactive Systems",
        "Intro to Computational Photogr": "Introduction to Computational Photography",
        "Practicum Intelligent Info Sys": "Practicum in Intelligent Information Systems",
        "Intro to Theory of Computation": "Introduction to the Theory of Computation",
        "Design &Analysis of Algorithms": "Design and Analysis of Algorithms",
        "Dynamics of Programming Lang": "Dynamics of Programming Languages",
        "Intro to Robotics Lab": "Introduction to Robotics Laboratory",
        "Building Problem Solvers": "Building Intelligent Problem Solvers",
        "AI Programming": "Artificial Intelligence Programming",
        "Machine Perception of Music": "Machine Perception of Music and Audio",
        "Natural & Artificial Vision": "Natural and Artificial Vision",
        "Game Design and Development": "Game Design and Development",
        "Game Design Studio": "Game Design Studio",
        "Sw Eng Beyond Programming": "Software Engineering Beyond Programming",
        "Rapid Prototyping for Software": "Rapid Prototyping for Software Development",
        "Software Construction": "Software Construction and Maintenance",
        "Agile Software Development": "Agile Software Development Practices",
        "Conversational AI": "Conversational Artificial Intelligence",
        "Data Privacy": "Data Privacy and Security",
        "Database Systems": "Database Systems and Applications",
        "Massively Parallel Prog w/CUDA": "Massively Parallel Programming with CUDA",
        "Microcontroller System Design": "Microcontroller System Design and Programming",
        "Multi-Agent Modeling": "Multi-Agent Systems and Modeling",
        "Quantum Computing": "Quantum Computing and Information Theory",
        "Social Networks Analysis": "Social Network Analysis and Modeling",
        "Special Projects in CS": "Special Projects in Computer Science",
        "Tangible Interac Dsgn & Lrn": "Tangible Interaction Design and Learning",
        "Tangible Interaction Dsg & Lrn": "Tangible Interaction Design and Learning",
        "Technology & Human Interaction": "Technology and Human Interaction",
        "Intro to Law and Digita": "Introduction to Law and Digital Privacy",
        "Knowledge Representation and R": "Knowledge Representation and Reasoning",
        "Knowledge Representation": "Knowledge Representation and Reasoning",
        "Special Topics in CS": "Special Topics in Computer Science"
    }

    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()

        for short_name, full_name in expansions.items():
            if 'Intro ' in full_name:
                full_name = full_name.replace('Intro ', 'Introduction ')
            sql = f"UPDATE Courses SET name = '{full_name}' WHERE name = '{short_name}';"
            cursor.execute(sql)
            print(f"Updated: {short_name} -> {full_name}")

        conn.commit()
        print("Database successfully updated with expanded course names")
        return True

    except Exception as e:
        print(f"Error updating database: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
def remove_number_underscores():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    
    

def revamp_db():
    # Get database connection
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()

        # First, add the new columns if they don't exist
        sql = """
        SELECT COUNT(*)
        FROM information_schema.columns 
        WHERE table_name = 'Courses' 
        AND column_name = 'course_number';
        """
        cursor.execute(sql)
        if cursor.fetchone()[0] == 0:
            sql = """
            ALTER TABLE Courses 
            ADD COLUMN course_number VARCHAR(50),
            ADD COLUMN name VARCHAR(255);
            """
            cursor.execute(sql)

        # Update the new columns with extracted data
        sql = """
        UPDATE Courses
        SET 
            course_number = CASE
                -- Format 1: course_number_section: name
                WHEN course_name REGEXP '^COMP_SCI_[0-9]+-[0-9]+_[0-9]+:' THEN
                    SUBSTRING_INDEX(SUBSTRING_INDEX(course_name, ':', 1), '_', 3)
                -- Format 2: name(course_number_section: ...)
                WHEN course_name REGEXP '.*COMP_SCI_[0-9]+-[0-9]+_[0-9]+:' THEN
                    SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(course_name, '(', -1), ':', 1), '_', 3)
                ELSE NULL
            END,
            name = CASE
                -- Format 1: course_number_section: name
                WHEN course_name REGEXP '^COMP_SCI_[0-9]+-[0-9]+_[0-9]+:' THEN
                    TRIM(SUBSTRING_INDEX(course_name, ':', -1))
                -- Format 2: name(course_number_section: ...)
                WHEN course_name REGEXP '.*COMP_SCI_[0-9]+-[0-9]+_[0-9]+:' THEN
                    TRIM(SUBSTRING_INDEX(course_name, '(', 1))
                ELSE NULL
            END
        WHERE course_name REGEXP 'COMP_SCI_[0-9]+-[0-9]+_[0-9]+';
        """
        cursor.execute(sql)

        # Clean up the data
        sql = """
        UPDATE Courses
        SET 
            -- Replace HTML entities
            name = REPLACE(name, '&#44;', ','),
            -- Clean up any remaining HTML entities or special characters
            name = REGEXP_REPLACE(name, '&[^;]+;', ''),
            -- Remove any leading/trailing whitespace
            name = TRIM(name)
        WHERE course_number IS NOT NULL;
        """
        cursor.execute(sql)

        # Commit the changes
        conn.commit()
        print("Database successfully updated with new columns and data")
        return True
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def remove_name_underscores():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Update course_number to replace underscores with spaces
        sql = """
        UPDATE Courses
        SET course_number = REPLACE(course_number, '_', ' ')
        WHERE course_number IS NOT NULL;
        """
        cursor.execute(sql)
        
        rows_affected = cursor.rowcount
        conn.commit()
        print(f"Updated {rows_affected} course numbers, replaced underscores with spaces")
        return True
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    revamp_db()
    expand_course_names()
    remove_name_underscores() 