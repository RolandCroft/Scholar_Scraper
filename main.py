"""
Scrape all publications of a given google scholar user.
Requires manual input to solve reCAPTCHA.
"""

import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

current_year = 0    # Track year being scraped


def get_entries_on_file(driver, wait, txt_file='publications.txt'):
    """
    Scrape the title, author and venue for each publication.
    Store results to a .txt file.
    """
    
    f = open(txt_file, 'a')
    # Get list of publications
    publications = driver.find_elements_by_class_name('gsc_a_tr')
    for p in publications:
        # Get year
        year = p.find_element_by_class_name('gsc_a_y')
        global current_year
        if int(year.text) != current_year:
            current_year = int(year.text)
            f.write('\n' + ('#'*5) + str(current_year) + ('#'*5) + '\n')
        # Get title
        info = p.find_element_by_class_name("gsc_a_at")
        title = info.text
        # Get author and venue
        details = p.find_elements_by_class_name('gs_gray')
        author = details[0].text
        venue = details[1].text.split(',')[0]
        # Write
        f.write(f'{author}, "{title}", {venue}.\n\n')
    f.close()


def main(user, num):
    """
    Initialise a headless browser to scrape publication entries.

    Parameters
    ----------
    user: The user to scrape for.
    year: The year to scrape until, otherwise scrape all entries.
    """

    # Set up driver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver_path = "/mnt/c/Windows/chromedriver.exe"
    driver = webdriver.Chrome(
        executable_path=driver_path, options=chrome_options)
    # Global Wait
    wait = WebDriverWait(driver, 40)

    query = f'http://www.scholar.google.com/citations?hl=en&user={user}' + \
            '&view_op=list_works&sortby=pubdate'
    driver.get(query)
    time.sleep(10)

    # Load the desired number of entries
    if num < 20:
        pages = 0
    else:
        pages = int((num+99)/100)      # (100 per page)
    for i in range(pages):
        button = driver.find_element_by_id('gsc_bpf_more').click()
        time.sleep(5)

    get_entries_on_file(driver, wait)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape Google Scholar')
    parser.add_argument('-u', type=str, required=True, metavar='User')
    parser.add_argument(
        '-n', type=int, nargs='?', const=0, metavar='Number to retrieve.')
    args = parser.parse_args()

    main(args.u, args.n)
