# Imports
import selenium
import time
import html

import numpy as np
import undetected_chromedriver as uc

from ast import literal_eval
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


def login(driver: selenium.webdriver, username: str, password: str, link="https://www.datacamp.com/users/sign_in",
          timeout=15):
    '''
    Logs into datacamp.
    driver: Any selenium webdriver
    username: Username or email for login
    password: Corresponding password for login
    link: The URL of the login page
    timeout: How long before the program quits when it cannot locate an element
    '''

    driver.get(link)
    print("Website Loaded")

    # Username find and enter
    try:
        user_log = WebDriverWait(driver, timeout=timeout).until(lambda d: d.find_element(By.ID, "user_email"))
        user_log.send_keys(username)
        print("Username Entered")
    except selenium.common.exceptions.ElementNotInteractableException:
        print("Username Error")
        return
    except selenium.common.exceptions.TimeoutException:
        print("Username Field Timed Out Before Found")
        return

    # Next button click
    driver.find_element(By.XPATH, '//*[@id="new_user"]/button').click()
    time.sleep(0.2)  # Might not be necessary
    print("Clicked Next")

    # Password find and enter
    try:
        user_pass = WebDriverWait(driver, timeout=timeout).until(lambda d: d.find_element(By.ID, "user_password"))
        user_pass.send_keys(password)
        print("Password Entered")
    except selenium.common.exceptions.ElementNotInteractableException:
        print("Password Error")
        return
    except selenium.common.exceptions.TimeoutException:
        print("Password Field Timed Out Before Found")
        return

    # Sign in button click
    driver.find_element(By.XPATH, '//*[@id="new_user"]/div[1]/div[3]/input').click()
    print("Signed In")

    # Finds the user profile to ensure that the login was registered
    try:
        WebDriverWait(driver, timeout=timeout) \
            .until(lambda d: d.find_element(By.XPATH,
                                            '//*[@id="single-spa-application:@dcmfe/mfe-app-atlas-header"]/nav/div[4]/div[2]/div/button'))
        print("Sign In Successful")
    except selenium.common.exceptions.TimeoutException:
        print("Error Verifying Sign In")


# def get_page_source(driver: selenium.webdriver, link: str) -> str:
#     '''
#     Returns the full HTML page source of a given link.
#     driver: Any selenium webdriver
#     link: The URL of the page
#     '''
#     driver.get(link)
#     return driver.page_source


def get_page_ids(driver: selenium.webdriver, link: str) -> list:
    '''
    Uses a datacamp assignment link to get all the required IDs for an API lookup
    driver: Any selenium webdriver
    link: The URL of the page
    '''
    driver.get(link)

    script = driver.find_element(By.XPATH, "/html/body/script[1]").get_attribute("textContent")
    script = html.unescape(script)
    ids = []
    for p in script.split("],"):
        if '"NormalExercise",' in p and '"id",' in p:
            i_start = p.find('"id",') + 5
            i_end = p[i_start:].find(",")
            if i_end == -1: i_end = p[i_start:].find("]")
            id = p[i_start:i_end + i_start]
            ids.append(int(id))

    return list(np.unique(ids))


def api_lookup(driver: selenium.webdriver, ids: list,
               api_link="https://campus-api.datacamp.com/api/exercises/{}/get_solution") -> list:
    '''
    Looks up a list of IDs and returns the API solution.
    driver: Any selenium webdriver
    ids: All IDs that will be looked up
    api_link: A formattable string with place for an ID
    '''
    pages = []
    for id in ids:
        driver.get(api_link.format(id))
        source = driver.find_element(By.XPATH, "/html/body/pre")
        element = literal_eval(source.get_attribute("textContent"))
        solution = html.unescape(element["solution"])
        pages.append(solution)

    return pages


# Main function
def main():

    # options = uc.ChromeOptions()
    #
    # options.add_argument('--no-startup-window')  # Hides the window
    # options.add_argument('--headless')  # Headless
    # options.headless = True
    #
    # driver = uc.Chrome(options=options)

    driver = uc.Chrome()

    login(driver, "jgelia@students.chccs.k12.nc.us", "Greenpig1!", timeout=10)
    ids = get_page_ids(driver,
                       "https://campus.datacamp.com/courses/joining-data-with-pandas/advanced-merging-and-concatenating?ex=4")
    answers = api_lookup(driver, ids)
    [print(f"\nAnswer #{i + 1}:\n{a}\n") for i, a in enumerate(answers)]


# Main
if __name__ == "__main__":
    main()