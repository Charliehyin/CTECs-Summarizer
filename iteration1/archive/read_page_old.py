import string
import re
import pandas as pd
import io


VALID_CHARS = string.ascii_uppercase+string.digits+"_"+"-"
def split_string_by_invalid_chars(input_string, valid_chars=VALID_CHARS):
    # Create a regex pattern that matches any character not in valid_chars
    pattern = f"[^{re.escape(''.join(valid_chars))}]+"  # Join valid chars and escape them
    # Use re.split to split the string
    return [s for s in re.split(pattern, input_string) if s]  # Remove empty strings

def split_string_by_multiple_delimiters(input_string, delimiters):
    # Create a regex pattern that matches any of the delimiters
    pattern = '|'.join(map(re.escape, delimiters))
    # Use re.split to split the string by the pattern
    return re.split(pattern, input_string)



def get_page_info(soup):
    '''
    Input: soup
    Output: 
    '''
    # Gets class names and instructor names
    title = soup.find("header", class_="cover-page").find("h2").get_text()
    split_chars = list(map(split_string_by_invalid_chars, title.split(":")[:-1]))
    class_names = list(map(lambda x: x[-1], split_chars))
    instructor_name = split_string_by_multiple_delimiters(title, "()")[-2]
    
    # Gets season
    project_title = soup.find("dl", class_="cover-page-project-title").find("dd").find("span").get_text()
    season, year = project_title.strip().strip("Course and Teacher Evaluations CTEC ").strip().split()
    season = season.lower()
    year = int(year)

    # Gets all report blocks
    report_blocks = soup.find_all("div", class_="report-block")
    report_blocks_analyzed = list(map(lambda x: [x.find("h4").find("span").get_text(),
                                                pd.read_html(io.StringIO(x.find("table").prettify()))], report_blocks))

    # Returns
    return report_blocks_analyzed