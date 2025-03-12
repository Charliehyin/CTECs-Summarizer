# Created by Joshua Lee on October 19, 2024 (previous versions for different purposes created earlier)
# Webdriver utility to help with basic webscraping tasks

# Imports
import glob
from selenium import webdriver
import undetected_chromedriver as ucdriver
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
# Unused Imports
# from bs4 import BeautifulSoup
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver import FirefoxOptions


def create_chromedriver():
    '''
    Returns a chrome webdriver object that can be used to make searches
    '''
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = ucdriver.Chrome(
        executable_path='chromedriver.exe', 
        chrome_options=options)
    return driver


def create_firefoxdriver(headless=False):
    '''
    Returns a firefox webdriver object that can be used to make searches
    '''
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    return driver


def create_default_download_driver(download_dir="temp", headless=True):
    full_download_dir = os.path.join(os.getcwd(), download_dir)
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #options.add_argument("--window-size=720,1280")
    options.add_argument('--log-level=3')
    options.add_experimental_option("prefs", {"download.default_directory": full_download_dir})
    if headless:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver


def create_default_driver():
    '''
    Most pipelines call this for utility
    '''
    #return create_firefoxdriver()
    return create_firefoxdriver()


def get_downloaded_file_name(start_time, glob_search_format='temp\\*.csv', max_wait_time = 20):
    '''
    TODO: write docstring
    '''
    download_initialization_time = time.time()
    while True: 
        # Gets a list of all files in the folder
        list_of_files = glob.glob(glob_search_format)
        latest_file = max(list_of_files, key=os.path.getctime, default=None)
        local_time = time.time()
        # Checks for the latest file fulling 3 requirements: 1) it exists, 2) its creation date is after the start time 3) its creation date is before the current local time
        if latest_file and os.path.getctime(latest_file) > start_time and os.path.getctime(latest_file) < local_time:
            return latest_file
        # If the local time is 
        if time.time() - download_initialization_time > max_wait_time:
            return None
        # Sleeps for 1 second in order not to kill the computer
        time.sleep(1)