# Imports
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Makes req
page = requests.get("https://catalogs.northwestern.edu/undergraduate/courses-az/")
soup = BeautifulSoup(page.text, "html.parser")
# with open ("files\\category_list.html", "r") as f:
#     soup = BeautifulSoup(f.read(), "html.parser")

# Gets sitemap
sitemap = soup.find("div", class_="az_sitemap")
sitemap.find("div", class_="azMenu").decompose()

# Gets li list
li = [x.find("a") for x in sitemap.find_all("li")]
# Turns li list into list of info
cat_list = [[a.get_text().split("(")[-1][:-1], a.get_text().split("(")[0].strip(), "https://catalogs.northwestern.edu" + a['href']]
             for a in li]

# Turns into df
df = pd.DataFrame(cat_list, columns=['code', 'title', 'href'])
df["status"] = "todo"

# Saves as CSV
df.to_csv("files\\status.csv", index=False)