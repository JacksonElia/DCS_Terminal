# Imports
import selenium
import time
from ast import literal_eval
from html import unescape
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


class SeleniumManager:
    driver: selenium.webdriver

    def __init__(self, driver: selenium.webdriver):
        self.driver = driver

    def login(self, username: str, password: str, link="https://www.datacamp.com/users/sign_in",
              timeout=15):
        '''
        Logs into datacamp.
        username: Username or email for login
        password: Corresponding password for login
        link: The URL of the login page
        timeout: How long before the program quits when it cannot locate an element
        '''

        self.driver.get(link)
        print("Website Loaded")

        # Username find and enter
        try:
            user_log = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.ID, "user_email"))
            user_log.send_keys(username)
            print("Username Entered")
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Username Error")
            return
        except selenium.common.exceptions.TimeoutException:
            print("Username Field Timed Out Before Found")
            return

        # Next button click
        self.driver.find_element(By.XPATH, '//*[@id="new_user"]/button').click()
        time.sleep(0.2)  # Might not be necessary
        print("Clicked Next")

        # Password find and enter
        try:
            user_pass = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.ID, "user_password"))
            user_pass.send_keys(password)
            print("Password Entered")
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Password Error")
            return
        except selenium.common.exceptions.TimeoutException:
            print("Password Field Timed Out Before Found")
            return

        # Sign in button click
        self.driver.find_element(By.XPATH, '//*[@id="new_user"]/div[1]/div[3]/input').click()
        print("Signed In")

        # Finds the user profile to ensure that the login was registered
        try:
            WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="single-spa-application:@dcmfe/mfe-app-atlas-header"]/nav/div[4]/div[2]/div/button'))
            print("Sign In Successful")
        except selenium.common.exceptions.TimeoutException:
            print("Error Verifying Sign In")

    def get_solutions(self, link: str) -> list:
        '''
        Uses a datacamp assignment link to get all the solutions for a chapter
        link: The URL of the page
        '''
        self.driver.get(link)
        script = self.driver.find_element(By.XPATH, "/html/body/script[1]").get_attribute("textContent")
        script = unescape(script)
        solutions = []
        for segment in script.split(",["):
            if ',"solution",' in segment and '"type","NormalExercise","id"' in segment:
                # Slices solution from src code
                solution = segment[segment.find('"solution","') + 12: segment.find('","type"')]
                # Formats solution into usable strings/code
                solution = literal_eval('"'+unescape(literal_eval('"'+solution+'"'))+'"')
                solutions.append(solution)
        return solutions

# Legacy methods
    # def get_page_source(driver: selenium.webdriver, link: str) -> str:
    #     '''
    #     Returns the full HTML page source of a given link.
    #     driver: Any selenium webdriver
    #     link: The URL of the page
    #     '''
    #     driver.get(link)
    #     return driver.page_source

    # def get_page_ids(self, link: str) -> list:
    #     '''
    #     Uses a datacamp assignment link to get all the required IDs for an API lookup
    #     driver: Any selenium webdriver
    #     link: The URL of the page
    #     '''
    #     self.driver.get(link)
    #
    #     script = self.driver.find_element(By.XPATH, "/html/body/script[1]").get_attribute("textContent")
    #     script = html.unescape(script)
    #     ids = []
    #     for p in script.split("],"):
    #         if '"NormalExercise",' in p and '"id",' in p:
    #             i_start = p.find('"id",') + 5
    #             i_end = p[i_start:].find(",")
    #             if i_end == -1: i_end = p[i_start:].find("]")
    #             id = p[i_start:i_end + i_start]
    #             ids.append(int(id))
    #
    #     return list(np.unique(ids))
    #
    # def api_lookup(self, ids: list,
    #                api_link="https://campus-api.datacamp.com/api/exercises/{}/get_solution") -> list:
    #     '''
    #     Looks up a list of IDs and returns the API solution.
    #     driver: Any selenium webdriver
    #     ids: All IDs that will be looked up
    #     api_link: A formattable string with place for an ID
    #     '''
    #     pages = []
    #     for id in ids:
    #         self.driver.get(api_link.format(id))
    #         source = self.driver.find_element(By.XPATH, "/html/body/pre")
    #         element = literal_eval(source.get_attribute("textContent"))
    #         solution = html.unescape(element["solution"])
    #         pages.append(solution)
    #
    #     return pages
