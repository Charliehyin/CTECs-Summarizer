# Imports
import io
import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
from requests_html import HTMLSession

def save_html(soup:BeautifulSoup):
    with open("saved.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())

def remove_duplicate_whitespaces(string):
    while "  " in string:
        string = string.replace("  ", " ").replace("\n ", "\n")
    return string.strip()


def parse_courseblock(soup:BeautifulSoup):
    courseblocktitle = soup.find(class_=["courseblocktitle", "couresblocktitle"]).find("strong").get_text().replace(u'\xa0', ' ')
    desc = soup.find(class_=["courseblockdesc", "couresblocktitle"]).get_text().replace(u'\xa0', ' ')

    extras = soup.find_all(class_='courseblockextra')
    if len(extras) > 0:
        desc = remove_duplicate_whitespaces(desc + " " + " ".join([p.get_text() for p in extras]))

    # Necessary evils
    courseblocksplit = courseblocktitle.split()
    category = courseblocksplit[0]
    number = courseblocksplit[1]
    code = f"{category} {number}"
    title = "(".join(courseblocktitle.split("(")[:-1]).replace(code, "").strip()
    units = courseblocktitle.split("(")[-1].strip().strip(" Unit)")

    # Returns
    return [code, category, number, title, units, desc]


# Reads status df
status_df = pd.read_csv("files\\status.csv")

# Creates HTML session
s = HTMLSession()

# Iterates over rows
for index, row in status_df.iterrows():
    if row["status"] != "success":
        try:

            # Makes HTML request
            response = s.get(row["href"])
            #response.html.render()

            # Finds and parses courseblocks
            soup = BeautifulSoup(response.text, "html.parser")
            page_container = soup.find("div", class_="page_content")
            courseblocks = page_container.find_all("div", class_="courseblock")
            courseblocks_parsed = list(map(parse_courseblock, courseblocks))

            # Turns to DF and saves as file
            df = pd.DataFrame(courseblocks_parsed, columns=["code", "category", "number", "title", "units", "desc"])
            df.to_csv(f"files\\downloads\\{row["code"]}.csv", index=False)

            # Updates status file
            status_df.iloc[index,-1] = "success"
            status_df.to_csv("files\\status.csv", index=False)

            # Printout
            print(f"SUCCESS: {row["code"]}")

        except Exception as e:
            # Updates status file
            status_df.iloc[index,-1] = "failure"
            status_df.to_csv("files\\status.csv", index=False)
            # Printout
            print(f"FAILURE: {row["code"]}, {e}")