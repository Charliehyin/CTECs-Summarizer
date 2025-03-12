# Imports
from bs4 import BeautifulSoup
import re
import string
import pandas as pd
import io

class StandardRating:
    def __init__ (self, df):
        self.count = float(df[0].loc[0, "Value"])
        self.mean = float(df[0].loc[1, "Value"])


class ClassReport:
    def __init__ (self, soup):

        # Gets metadata
        metadata = soup.find("div", class_="metadata")
        self.project_title = metadata.find("dl", class_="cover-page-project-title").find("dd").find("span").get_text()
        audience_data = metadata.find("div", class_="audience-data").find_all("dd")
        self.class_size = audience_data[0].find("span").get_text()
        self.responses = audience_data[1].find("span").get_text()

        # Calculates block dict
        block_dict = {
            block.find("h4").find("span").get_text() : pd.read_html(io.StringIO(block.find("table").prettify()))
            for block in soup.find_all("div", class_="report-block")
        }

        # Course-related
        self.instruction_rating = StandardRating(block_dict["1. Provide an overall rating of the instruction."])
        self.course_rating = StandardRating(block_dict["2. Provide an overall rating of the course."])
        self.amount_learned = StandardRating(block_dict["3. Estimate how much you learned in the course."])
        self.challenge_level = StandardRating(block_dict["4. Rate the effectiveness of the course in challenging you intellectually."])
        self.instructor_stimulating_interest = StandardRating(block_dict["5. Rate the effectiveness of the instructor in stimulating your interest in the subject."])
        # Hours per week
        self.hours_per_week = block_dict["6. Estimate the average number of hours per week you spent on this course outside of class and lab time."][0]
        # Comments
        #self.comments = list(block_dict["Please summarize your reaction to this course focusing on the aspects that were most important to you."][0]["Comments"])
        # Less important stuff
        self.school = block_dict["What is the name of your school?"][0]
        self.reason_for_taking_course = block_dict["What is your reason for taking the course? (mark all that apply)"][0]
        self.previous_interest = block_dict["What was your Interest in this subject before taking the course?"][0]
        # Year
        self.year = block_dict["Your Class"][0]

        # Calculates some other vars
        self.year_average = float((self.year.loc[0, "Count"]*1 + 
                                   self.year.loc[1, "Count"]*2 + 
                                   self.year.loc[2, "Count"]*3 + 
                                   self.year.loc[3, "Count"]*4) / sum(list(self.year["Count"])))



#########################################################
if __name__ == "__main__":
    import time
    # Reads soup
    FILE_PATH = r"downloads\COMP_SCI\COMP_SCI 111-0\COMP_SCI 111-0=2024=Spring=Fundamentals of Computer Programming=Sara Owsley.html"
    
    start = time.perf_counter()
    with open(FILE_PATH) as f:
        soup = BeautifulSoup(f, 'html.parser')
    class_report = vars(ClassReport(soup))
    end =  time.perf_counter()

    print(class_report)
    print(f"Total time elapsed: {end-start}")