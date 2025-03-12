from bs4 import BeautifulSoup
import json


with open ("CTEC.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

select = soup.find("select", {"id": "NW_CT_PB_SRCH_SUBJECT", "class":"ps-dropdown"})
option_list = select.find_all("option")[1:]

option_dict = {option['value']: " - ".join(option.get_text().split(" - ")[1:]) for option in option_list}

with open("class_categories.json", "w") as outfile: 
    json.dump(option_dict, outfile, indent=4)

for key, value in option_dict.items():
    print(f"{key}: {value}")