# Imports
import io
import os
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# Local Imports
from formatting_util import slugify_filename
from webdriver_util import create_default_driver


# Max wait time for webdriver
WAIT_TIME = 300

# Gets CAESAR instance
def get_CAESAR_instance():
    '''
    Opens an instance of CAESAR (requires user to authenticate using DUO)
    Returns a driver with CAESAR loaded on it
    '''
    # Creats driver and gets CAESAR login
    driver = create_default_driver()
    driver.get("https://caesar.ent.northwestern.edu/")
    # Waits for page to load
    WebDriverWait(driver, 1000).until(EC.presence_of_element_located((By.CLASS_NAME, "ps_grid-div")))
    # Returns driver
    return driver


def close_other_tabs(driver):
    # Get the current window handle
    current_window = driver.current_window_handle
    # Get a list of all open window handles (tabs)
    all_windows = driver.window_handles
    # Loop through all window handles and close them except the current one
    for window in all_windows:
        if window != current_window:
            driver.switch_to.window(window)
            driver.close()
    # Switch back to the current window
    driver.switch_to.window(current_window)


SEARCH_STRING = "https://caesar.ent.northwestern.edu/psc/CS860PRD/EMPLOYEE/SA/c/NWCT.NW_CT_PUB_RSLT_FL.GBL?Page=NW_CTEC_RSLT2_FL&NW_CTEC_SRCH_CHOIC=C&ACAD_CAREER=UGRD&SUBJECT={}"
def get_class_category(driver, category):
    '''
    Inputs
    - driver: expects a webdriver with a CAESAR instance
    - category: expects a string category of class (ex. COMP_SCI)
    Outputs:
    - driver with the class category instance'''
    # Switches to new tab
    driver.switch_to.new_window("tab")
    # Gets the URL for the class category
    driver.get(SEARCH_STRING.format(category))
    # Closes all other tabs
    time.sleep(0.8)
    close_other_tabs(driver)
    # Waits for classes to load
    WebDriverWait(driver,100).until(EC.presence_of_element_located((By.ID, "PT_PAGETITLE1")))


def iterate_through_past_classes(driver, category, class_num):
    '''
    Goes through each class under the class table and saves the data. Expects to already be at a class page
    '''

    # Gets category
    get_class_category(driver, category)

    # Waits for class to load, then clicks on the element
    xpath = f"//tr[.//span[contains(@class, 'ps_box-value') and contains(text(), '{class_num}')]]"
    tr = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, xpath)))
    driver.execute_script(tr.get_attribute("onclick"))
        
    # Waits for table to load, then gets its soup
    table_xpath = "//div[contains(@class, 'ps_main') and .//table]"
    table = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    table_body = table.find_element(By.TAG_NAME, "tbody")
    soup_table = BeautifulSoup(table_body.get_attribute('innerHTML'), "html.parser")

    # Iterates over all tablee rows (the past sessions)
    for table_row in soup_table.find_all("tr"):
        
        # Switches to rightmost tab
        driver.switch_to.window(driver.window_handles[-1])

        # Waits for page to load (and also puts driver in memory? unsure tbh)
        WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, table_xpath)))

        # Gets some basic information about the class section
        element_list = table_row.find_all("td")
        year, season = element_list[0].find("span").get_text().split()
        class_name_total = element_list[1].find("span").get_text()
        class_id = '-'.join(class_name_total.split("-")[:2]) # 
        class_category = class_id.split()[0]
        class_name = ' '.join(class_name_total.split()[2:])
        instructor_name = element_list[2].find("span").get_text()

        # Executes tab switch script
        driver.execute_script(table_row['onclick'])
        time.sleep(0.3)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(0.1)
        WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, "//body[@id='reportView']")))
        time.sleep(0.675)

        # Saves file
        file_name = f"{class_id}={year}={season}={slugify_filename(class_name)}={instructor_name}"
        with open(f"downloads\\{class_category}\\{class_id}\\{file_name}.html", 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        driver.close()

        # Waits
        time.sleep(0.6)


def cover_one_category(driver, category):

    # Gets class cateogry
    get_class_category(driver=driver, category=category)
    
    # Waits for table to load. Turns table into soup
    table_xpath = "//div[contains(@class, 'ps_masterlist-group') and .//table]"
    table = WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    table_body = table.find_element(By.TAG_NAME, "tbody")
    soup_table = BeautifulSoup(table_body.get_attribute('innerHTML'), "html.parser")

    for table_row in soup_table.find_all("tr"):
        # Gets class info
        element_list = table_row.find_all("td")
        class_name_total = element_list[0].find("span", class_="ps_box-value").get_text()
        class_num = class_name_total.split(":")[0].strip()
        # Makes dir
        os.makedirs(f"downloads\\{category}\\{category} {class_num}", exist_ok=True)
        # Waits for page to load (and also puts driver in memory? unsure tbh)
        driver.switch_to.window(driver.window_handles[-1])
        WebDriverWait(driver, WAIT_TIME).until(EC.presence_of_element_located((By.XPATH, table_xpath)))
        # Downloads files
        iterate_through_past_classes(driver, category, class_num=class_num)
        # Prints "done"
        print(f"ITERATED THROUGH {class_num}")


if __name__ == "__main__":
    # Opens a CAESAR instance
    driver = get_CAESAR_instance()
    # Covers CS in its entirety
    CLASS_CATEGORY = "COMP_SCI"
    cover_one_category(driver=driver, category=CLASS_CATEGORY)