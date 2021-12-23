"""
seleniummanager.py: Responsible for everything to do with Selenium including launching the webdriver, getting the
the solutions to the Datacamp questions, and solving the questions.
Contributors: Jackson Elia, Andrew Combs
"""
import pyperclip
import selenium
import selenium.common.exceptions
from ast import literal_eval
from html import unescape
from selenium.webdriver import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep


class SeleniumManager:
    driver: selenium.webdriver

    def __init__(self, driver: selenium.webdriver):
        self.driver = driver

    def login(self, username: str, password: str, link="https://www.datacamp.com/users/sign_in",
              timeout=15):
        """
        Logs into datacamp.
        :param username: Username or email for login
        :param password: Corresponding password for login
        :param link: The URL of the login page
        :param timeout: How long before the program quits when it cannot locate an element
        """

        self.driver.get(link)
        print("Website Loaded")

        # Username find and enter
        try:
            user_log = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.ID, "user_email"))
            user_log.send_keys(username)
            print("Username Entered")
        except selenium.common.exceptions.ElementNotInteractableException:  # Might not be necessary
            print("Username Error")
            return
        except selenium.common.exceptions.TimeoutException:
            print("Username Field Timed Out Before Found")
            return

        # Next button click
        self.driver.find_element(By.XPATH, '//*[@id="new_user"]/button').click()
        sleep(0.2)  # Might not be necessary
        print("Clicked Next")

        # Password find and enter
        try:
            user_pass = WebDriverWait(self.driver, timeout=timeout).until(
                lambda d: d.find_element(By.ID, "user_password"))
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
        """
        Uses a datacamp assignment link to get all the solutions for a chapter
        :param link: The URL of the page
        """
        self.driver.get(link)
        script = self.driver.find_element(By.XPATH, "/html/body/script[1]").get_attribute("textContent")
        script = unescape(script)
        solutions = []
        exercise_dicts = []

        number_1_found = 0
        for segment in script.split(",["):
            if ',"solution",' in segment and '"type","NormalExercise","id"' in segment:
                # Slices solution from src code
                solution = segment[segment.find('"solution","') + 12: segment.find('","type"')]
                # Formats solution into usable strings/code
                solution = literal_eval('"' + unescape(literal_eval('"' + solution + '"')) + '"')
                solutions.append(solution)
                # print(segment)
            elif 'Exercise","title","' in segment:
                # Makes sure it only gets the full set of solutions once
                if ',"number",1,"' in segment:
                    number_1_found += 1
                    if number_1_found > 1:
                        break
                exercise_dict = {}
                exercise_dict["type"] = segment[8:segment.find('Exercise","title","') + 8]
                exercise_dict["number"] = segment[segment.find(',"number",') + 10:segment.find(',"url","')]
                exercise_dict["link"] = segment[segment.find(',"url","') + 9:segment.find('"]]')]
                exercise_dicts.append(exercise_dict)
        return solutions

    def reset_course(self, timeout: int):
        """
        Resets all progress on the Datacamp course. Used to make sure all of the solve functions work properly.
        :param timeout: How long it should wait to see the "Got it" button
        """
        try:
            course_outline_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH, '//*[@id="root"]/div/header/div[2]/div/nav/button'))
            course_outline_button.click()
            print("Course outline button clicked")
            bruh = self.driver.find_elements_by_class_name("css-1gv579o")
            for item in bruh:
                print(item)
            reset_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.CLASS_NAME, 'css-1gv579o'))
            reset_button.click()
            sleep(.2)
            # Presses enter twice to deal with the popups
            alert = Alert(self.driver)
            alert.accept()
            sleep(.2)
            alert.accept()
        except selenium.common.exceptions.TimeoutException:
            print("One of the buttons, most likely Course Outline Button not found before timeout")

    # Clicks the got it button
    def solve_video_exercise(self, timeout: int) -> bool:
        """
        Solves a Video exercise by clicking the "Got it" button.
        :param timeout: How long it should wait to see the "Got it" button
        :return: Boolean for true if it successfully solved a Video exercise
        """
        solved_exercise = False
        try:
            got_it_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH, '//*[@id="root"]/div/main/div[1]/section/div[2]/button[2]'))
            got_it_button.click()
            print("Got it button clicked")
            solved_exercise = True
            return solved_exercise
        except selenium.common.exceptions.TimeoutException:
            print("Got it button not found before timeout, most likely was not a video exercise")
            return solved_exercise

    # Clicks on the python script, doing ctrl + a, inputting the solution, clicking the next button
    def solve_normal_exercise(self, solution: str, timeout: int) -> bool:
        """
        Solves a Normal Exercise by pasting the solution into the editor tab, clicking the "Submit Answer" button and
        then clicking the "Continue" button.
        :param solution: The correct answer to the current Normal Exercise
        :param timeout: How long it should wait to sees certain elements in the normal exercise
        :return: Boolean for true if it successfully solved a normal exercise
        """
        solved_exercise = False
        try:
            xp_amount = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/strong'))
            # TODO: Find cleaner way of identifying normal exercises
            if xp_amount.text == "100 XP":
                script_margin = WebDriverWait(self.driver, timeout=timeout) \
                    .until(lambda d: d.find_element(By.XPATH,
                                                    '//*[@id="rendered-view"]/div/div/div[3]/div[1]'))
                # Clicks on the script to put it in focus
                script_margin.click()

                sleep(1)  # Might not be necessary

                action_chain = ActionChains(self.driver)
                # Sends CTRL + A
                action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                pyperclip.copy(solution)
                # Pastes the solution
                # TODO: Make it work for OSX
                action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
            else:
                print("Most likely not a normal exercise")
                return solved_exercise
        except selenium.common.exceptions.TimeoutException:
            print("Python script not found, most likely not a normal exercise")
            return solved_exercise

        try:
            submit_answer_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="gl-editorTabs-files/script.py"]/div/div/div[2]/div[2]/button[3]'))
            sleep(3)  # Might not be necessary TODO: Fix this
            submit_answer_button.click()
            print("Submit Answer button clicked")
            continue_button = WebDriverWait(self.driver, timeout=3) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="gl-aside"]/div/aside/div[2]/div/div[3]/button'))
            continue_button.click()
            print("Clicked the continue button")
            solved_exercise = True
            return solved_exercise
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Submit Answer or Continue button couldn't be clicked")
        except selenium.common.exceptions.TimeoutException:
            print("Submit Answer or Continue button not found, most likely not a normal exercise")
            return solved_exercise

    def solve_bullet_exercises(self, solutions: [str], timeout: int) -> bool:
        """
        Solves a Bullet exercise by pasting the solution into the editor tab, clicking the "Submit Answer" button,
        repeating this until it has completed all of the sub exercises, then clicking the "Continue" button.
        :param solutions: The correct answer to the current Bullet exercise
        :param timeout: How long it should wait to sees certain elements in the Bullet exercise
        :return: Boolean for true if it successfully solved a Bullet exercise
        """
        solved_exercise = False
        try:
            xp_amount = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/strong'))
            # TODO: Find better way of doing this, won't always work
            number_of_exercises = (WebDriverWait(self.driver, timeout=timeout)
                                   .until(lambda d: d.find_element(By.XPATH,
                                                                   '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/h5'))).text[-1]
            if xp_amount.text != "100 XP" and len(solutions) == int(number_of_exercises):
                for solution in solutions:
                    script_margin = WebDriverWait(self.driver, timeout=timeout) \
                        .until(lambda d: d.find_element(By.XPATH,
                                                        '//*[@id="rendered-view"]/div/div/div[3]/div[1]'))
                    # Clicks on the script to put it in focus
                    script_margin.click()

                    sleep(1)  # Might not be necessary, doesn't select everything

                    action_chain = ActionChains(self.driver)

                    # Sends CTRL + A
                    action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                    # Types the solution
                    # Doesn't always work because it is too slow and messes up with Datacamps's autocomplete
                    # action_chain.send_keys(solution).perform()
                    # Copies the solution to clipboard
                    pyperclip.copy(solution)
                    # Pastes the solution
                    # TODO: Make it work for OSX
                    action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

                    submit_answer_button = WebDriverWait(self.driver, timeout=timeout) \
                        .until(lambda d: d.find_element(By.XPATH,
                                                        '/html/body/div[1]/div/main/div[1]/div/div/div[3]/div[1]/div/div[2]/div/div/div/div/div/div[2]/div[2]/button[3]'))
                    sleep(4)  # Might not be necessary
                    submit_answer_button.click()
                    print("Submit Answer button clicked")
                    # Clears clipboard
                    pyperclip.copy("")

                continue_button = WebDriverWait(self.driver, timeout=3) \
                    .until(lambda d: d.find_element(By.XPATH,
                                                    '//*[@id="gl-aside"]/div/aside/div[2]/div/div[3]/button'))
                continue_button.click()
                print("Clicked the continue button")
                solved_exercise = True
                return solved_exercise
            else:
                print("Maybe not a bullet exercise")
                return solved_exercise
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Continue button couldn't be clicked")
        except selenium.common.exceptions.TimeoutException:
            print("Python script not found, most likely not a bullet exercise")
            return solved_exercise

    # Basically the same as bullet exercises, but the final solution works for each part
    def solve_tab_exercises(self, solutions: [str], timeout: int) -> bool:
        """
        Solves a Tab exercise by pasting the final solution into the editor tab, clicking the "Submit Answer" button,
        repeating this until it has completed all of the sub exercises, then clicking the "Continue" button.
        :param solutions: The correct answer to the current Tab exercise
        :param timeout: How long it should wait to sees certain elements in the Tab exercise
        :return: Boolean for true if it successfully solved a Tab exercise
        """
        solved_exercise = False
        try:
            xp_amount = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/strong'))
            number_of_exercises = (WebDriverWait(self.driver, timeout=timeout)
                                   .until(lambda d: d.find_element(By.XPATH,
                                                                   '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/h5'))).text[-1]
            if xp_amount.text != "100 XP" and len(solutions) == int(number_of_exercises):
                # Copies the solution to clipboard
                pyperclip.copy(solutions[-1])
                for i in range(len(solutions)):
                    script_margin = WebDriverWait(self.driver, timeout=timeout) \
                        .until(lambda d: d.find_element(By.XPATH,
                                                        '//*[@id="rendered-view"]/div/div/div[3]/div[1]'))
                    # Clicks on the script to put it in focus
                    script_margin.click()
                    sleep(1)  # Might not be necessary, doesn't select everything
                    action_chain = ActionChains(self.driver)
                    # Sends CTRL + A
                    action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                    # Pastes the solution
                    action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                    submit_answer_button = WebDriverWait(self.driver, timeout=timeout) \
                        .until(lambda d: d.find_element(By.XPATH,
                                                        '/html/body/div[1]/div/main/div[1]/div/div/div[3]/div[1]/div/div[2]/div/div/div/div/div/div[2]/div[2]/button[3]'))
                    sleep(4)  # Might not be necessary
                    submit_answer_button.click()
                    print("Submit Answer button clicked")
                    # Clears clipboard
                    pyperclip.copy("")

                continue_button = WebDriverWait(self.driver, timeout=3) \
                    .until(lambda d: d.find_element(By.XPATH,
                                                    '//*[@id="gl-aside"]/div/aside/div[2]/div/div[3]/button'))
                continue_button.click()
                print("Clicked the continue button")
                solved_exercise = True
                return solved_exercise
            else:
                print("Maybe not a bullet exercise")
                return solved_exercise
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Continue button couldn't be clicked")
        except selenium.common.exceptions.TimeoutException:
            print("Python script not found, most likely not a bullet exercise")
            return solved_exercise

    # TODO: Optimize timeouts
    # There are different multiple choice problems, this one allows the user to press a number to select an answer
    # Gets the number of multiple choice options, then enters 1, 2, 3 etc and presses enter after each until it gets the right one
    def solve_multiple1(self) -> bool:
        """
        Solves a Pure Multiple Choice exercise by sending the number that corresponds to each multiple choice option and
        the enter key until it finds the correct answer, then it clicks the "Continue" button.
        :return: Boolean for true if it successfully solved a Pure Multiple Choice exercise
        """
        solved_exercise = False
        try:
            # Checks if its a multiple choice question by finding the multiple choice otions
            WebDriverWait(self.driver, 5) \
                .until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                        '//*[@id="root"]/div/main/div[1]/section/div/div[5]/div/div/ul')))
        except selenium.common.exceptions.TimeoutException:
            print("Multiple Choice options couldn't be found, most likely not multiple choice type 1")
            return solved_exercise

        # Gets the amount of the child elements (the multiple choice options) in the parent element
        multiple_choice_options = len(self.driver.find_elements_by_xpath(
            '//*[@id="root"]/div/main/div[1]/section/div/div[5]/div/div/ul/*'))
        print(multiple_choice_options)
        for i in range(0, multiple_choice_options):
            action_chain = ActionChains(self.driver)
            action_chain.send_keys(str(i + 1), Keys.ENTER).perform()
            try:
                continue_button = WebDriverWait(self.driver, timeout=3) \
                    .until(lambda d: d.find_element(By.XPATH,
                                                    '//*[@id="root"]/div/main/div[1]/div/div/div/div[2]/button'))
                continue_button.click()
                print("Clicked the continue button")
                solved_exercise = True
                return solved_exercise
            except selenium.common.exceptions.ElementNotInteractableException:
                print("Continue button couldn't be clicked")
            except selenium.common.exceptions.TimeoutException:
                print("Continue button not found")
            sleep(1)  # Might not be necessary
        return solved_exercise

    # There are different multiple choice problems, this one has the python script open with it
    # Gets how many multiple choice options there are, goes through each one checking if it is the right answer
    def solve_multiple2(self) -> bool:
        """
        Solves a Multiple Choice exercise by going through each of the options and checking to see if it is the correct
        one.
        :return: Boolean for true if it successfully solved a Pure Multiple Choice exercise
        """
        solved_exercise = False
        try:
            WebDriverWait(self.driver, 5) \
                .until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                        '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul')))
        except selenium.common.exceptions.TimeoutException:
            print("Multiple Choice options couldn't be found, most likely not multiple choice type 2")
            return solved_exercise

        try:
            # Gets the length of the child elements (the multiple choice options) in the parent element
            multiple_choice_options = len(self.driver.find_elements_by_xpath(
                '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul/*'))
            for i in range(0, multiple_choice_options):
                radio_input_button = WebDriverWait(self.driver, timeout=3) \
                    .until(lambda d: d.find_element(By.XPATH,
                                                    f'//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul/li[{i + 1}]/div/div/label'))
                radio_input_button.click()
                print("Clicked a radio button")
                try:
                    submit_button = WebDriverWait(self.driver, timeout=3) \
                        .until(lambda d: d.find_element(By.XPATH,
                                                        '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[1]/button'))
                    submit_button.click()
                    print("Clicked the submit button")
                    continue_button = WebDriverWait(self.driver, timeout=5) \
                        .until(lambda d: d.find_element(By.XPATH,
                                                        '//*[@id="gl-aside"]/div/aside/div[2]/div/div[3]/button'))
                    continue_button.click()
                    print("Clicked the continue button")
                    solved_exercise = True
                    return solved_exercise
                except selenium.common.exceptions.ElementNotInteractableException:
                    print("Continue or submit button couldn't be clicked")
                except selenium.common.exceptions.TimeoutException:
                    print("Continue or submit button not found")
                sleep(1)  # Might not be necessary
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Radio input button couldn't be clicked")
            return solved_exercise
        except selenium.common.exceptions.TimeoutException:
            print("Radio input button not found, most likely not a multiple choice exercise")
            return solved_exercise

    # TODO: Make drag and drop work
    def solve_drag_and_drop(self, timeout: int) -> bool:
        """
        Skips drag and drop by showing answer, clicking submit answer, and clicking continue.
        :param timeout: How long it should wait to sees certain elements in the drag and drop exercise
        :return:
        """
        solved_exercise = False
        try:
            show_hint_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="root"]/div/main/div[2]/div/div[1]/section/div[1]/div[5]/div/section/nav/div/button'))
            show_hint_button.click()
            show_answer_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="root"]/div/main/div[2]/div/div[1]/section/div[1]/div[5]/div/section/nav/div/button'))
            show_answer_button.click()
            submit_answer_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="root"]/div/main/div[2]/div/div[3]/div/div/div[2]/div/button[2]'))
            '//*[@id="root"]/div/main/div[2]/div/div[1]/section/div[1]/div[5]/div/section/nav/div/button'
            submit_answer_button.click()
            continue_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH,
                                                '//*[@id="root"]/div/main/div[2]/div/div[1]/div/div/div/div[2]/button'))
            continue_button.click()
            solved_exercise = True
            return solved_exercise
        except selenium.common.exceptions.TimeoutException:
            print("One of the buttons not found before timeout, most likely was not a drag and drop exercise")
            return solved_exercise

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
