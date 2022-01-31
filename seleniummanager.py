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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from terminal import DTerminal

from typing import List, Tuple


# TODO: Integrate terminal instead of using self.t.log
class SeleniumManager:
    driver: selenium.webdriver

    def __init__(self, driver: selenium.webdriver, terminal: DTerminal):
        self.driver = driver
        self.t = terminal

    def login(self, username: str, password: str, link="https://www.datacamp.com/users/sign_in", timeout=15):
        """
        Logs into datacamp.
        :param username: Username or email for login
        :param password: Corresponding password for login
        :param link: The URL of the login page
        :param timeout: How long before the program quits when it cannot locate an element
        """
        self.driver.get(link)
        self.t.log("Website Loaded")
        try:
            # Username find and enter
            try:
                WebDriverWait(self.driver, timeout=timeout).until(
                    lambda d: d.find_element(By.ID, "user_email")).send_keys(username)
                self.t.log("Username Entered")
            except selenium.common.exceptions.ElementNotInteractableException:
                self.t.log("Username Error")
                return
            except selenium.common.exceptions.TimeoutException:
                self.t.log("Username Field Timed Out Before Found")
                return
            # Next button click
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="new_user"]/button')).click()
            # Password find and enter
            sleep(1)
            try:
                WebDriverWait(self.driver, timeout=timeout).until(
                    lambda d: d.find_element(By.ID, "user_password")).send_keys(password)
                self.t.log("Password Entered")
            except selenium.common.exceptions.ElementNotInteractableException:
                self.t.log("Password Error")
                return
            except selenium.common.exceptions.TimeoutException:
                self.t.log("Password Field Timed Out Before Found")
                return
            # Sign in button click
            WebDriverWait(self.driver, timeout=timeout).until(
                lambda d: d.find_element(By.XPATH, '//*[@id="new_user"]/div[1]/div[3]/input')).click()
            self.t.log("Signed In")
            # Finds the user profile to ensure that the login was registered
            try:
                WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH,
                    '//*[@id="single-spa-application:@dcmfe/mfe-app-atlas-header"]/nav/div[4]/div[2]/div/button'))
                self.t.log("Sign In Successful")
            except selenium.common.exceptions.TimeoutException:
                self.t.log("Error Verifying Sign In")
        except selenium.common.exceptions.TimeoutException:
            self.t.log("Next button or Sign in button not present")

    def get_solutions_and_exercises(self, link: str) -> Tuple[list, List[dict]]:
        """
        Uses a datacamp assignment link to get all the solutions for a chapter
        :param link: The URL of the page
        """
        self.driver.get(link)
        script = self.driver.find_element(By.XPATH, "/html/body/script[1]").get_attribute("textContent")
        script = unescape(script)
        solutions = []
        exercise_dicts = []

        for segment in script.split(",["):
            if ',"solution",' in segment and '"type","NormalExercise","id"' in segment:
                # Slices solution from src code
                solution = segment[segment.find('"solution","') + 12: segment.find('","type"')]
                # Formats solution into usable strings/code
                try:
                    solution = literal_eval('"' + unescape(literal_eval('"' + solution + '"')) + '"')
                    solutions.append(solution)
                # TODO: Find a better way of doing this
                # Every once and a while, if there is a string in the solution that represents a file path, it can break literal eval
                except SyntaxError:
                    # Filters segments to only get the solutions, then removes some of the slashes
                    solution = solution.replace("\\\\n", "\n")
                    solution = solution.replace("\\\\t", "\t")
                    deletion_index_list = []
                    for index, char in enumerate(solution):
                        if char == "\\":
                            # Other escape characters not that important like who uses \ooo lol
                            if solution[index + 1] != "n" and solution[index + 1] != "t" and solution[index - 2: index + 1] != ") \\":
                                deletion_index_list.append(index)
                    # Reverses list, so it doesn't mess with index when removing the character
                    for index in reversed(deletion_index_list):
                        solution = solution[:index] + solution[index + 1:]
                    solutions.append(solution)

        number_1_found = 0
        for segment in script.split(",["):
            if 'Exercise","title","' in segment:
                # Makes sure it only gets the full set of solutions once
                if ',"number",1,"' in segment:
                    number_1_found += 1
                    if number_1_found > 1:
                        break
                exercise_dict = {"type": segment[8:segment.find('Exercise","title","') + 8],
                                 "number": segment[segment.find(',"number",') + 10:segment.find(',"url","')],
                                 "link": segment[segment.find(',"url","') + 8:segment.find('"]]')]}
                exercise_dicts.append(exercise_dict)
        return solutions, exercise_dicts

    def auto_solve_course(self, starting_link: str, timeout=10, reset_course=False, wait_length=0):
        """
        Solves a whole Datacamp course.
        :param starting_link: The link of the Datacamp course to solve
        :param timeout: How long it waits for elements to appear
        :param reset_course: If the course and xp earned from the course should be reset
        :param wait_length: Delay in between exercises
        """
        if reset_course:
            self.driver.get(starting_link)
            self.reset_course(timeout)

        chapter_link = starting_link
        done_with_course = False
        while not done_with_course:
            solutions, exercises = self.get_solutions_and_exercises(chapter_link)
            next_chapter, chapter_link = self.auto_solve_chapter(exercise_list=exercises, solutions=solutions,
                                                                 timeout=timeout, wait_length=wait_length)
            done_with_course = not next_chapter

    # TODO: Let user set how long in between solving
    def auto_solve_chapter(self, exercise_list: List[dict], solutions: List[str], wait_length: int, timeout=10) -> Tuple[bool, str]:
        """
        Automatically solves a Datacamp chapter, if it desyncs it will redo the chapter.
        :param exercise_list: List of dicts that contain information about each exercise
        :param solutions: List of solutions for each exercises
        :param wait_length: Delay in between exercises
        :param timeout: How long it waits for elements to appear
        :return: A boolean for if there is another chapter in the course and a string with the url to that chapter
        """
        self.driver.get(exercise_list[0]["link"])
        max_tries = 2
        for exercise in exercise_list:
            exercise_solved = False
            tries = 0
            while not exercise_solved and tries < max_tries:
                self.driver.get(exercise["link"])
                # User can set this to add delay in between exercises
                sleep(wait_length)
                tries += 1
                match exercise["type"]:
                    case "VideoExercise":
                        self.t.log("Solving Video Exercise")
                        self.solve_video_exercise(timeout)
                        # It almost never messes up on video exercises
                        exercise_solved = True
                    case "NormalExercise":
                        self.t.log("Solving Normal Exercise")
                        if self.solve_normal_exercise(solutions[0], timeout):
                            solutions.pop(0)
                            exercise_solved = True
                        elif tries == max_tries:
                            solutions.pop(0)
                    case "BulletExercise":
                        self.t.log("Solving Bullet Exercise")
                        exercise_solved, solutions_used = self.solve_bullet_exercises(solutions, timeout)
                        if exercise_solved:
                            for i in range(solutions_used):
                                solutions.pop(0)
                        elif tries == max_tries:
                            for i in range(solutions_used):
                                solutions.pop(0)
                    # TODO: Find better way of managing solutions used for tab exercises, currently if it desyncs on a tab exercise it has to restart the module
                    case "TabExercise":
                        self.t.log("Solving Tab Exercise")
                        exercise_solved, solutions_used = self.solve_tab_exercises(solutions, timeout)
                        if exercise_solved:
                            for i in range(solutions_used):
                                solutions.pop(0)
                        elif tries == max_tries:
                            for i in range(solutions_used):
                                solutions.pop(0)
                    case "PureMultipleChoiceExercise":
                        self.t.log("Solving Pure Multiple Choice Exercise")
                        exercise_solved = self.solve_multiple1(timeout)
                    case "MultipleChoiceExercise":
                        self.t.log("Solving Multiple Choice Exercise")
                        exercise_solved = self.solve_multiple2(timeout)
                    case "DragAndDropExercise":
                        self.t.log("Solving Drag and Drop Exercise")
                        exercise_solved = self.solve_drag_and_drop(timeout)
                    case _:
                        self.t.log("What entered was an exercise not on this match statement")

        # Refreshes the page to deal with popup
        self.driver.refresh()
        if exercise_list[-1]["type"] == "VideoExercise":
            self.click_submit(timeout)
        else:
            # Clicks on the page, then enters in shortcut for the arrow button at the top
            try:
                WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="gl-aside"]')) \
                    .click()
            except (selenium.common.exceptions.TimeoutException, selenium.common.exceptions.ElementClickInterceptedException):
                self.t.log("The Exercise bar could not be clicked or found")
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("k").key_up(Keys.CONTROL).perform()
            self.t.log("Sent ctrl + k")
        # Waiting for next chapter to load
        sleep(timeout)
        if "https://app.datacamp.com/learn/courses" not in self.driver.current_url:
            self.t.log(self.driver.current_url)
            return True, self.driver.current_url
        else:
            self.t.log("Finished Course")
            return False, ""

    def reset_course(self, timeout: int):
        """
        Resets all progress on the Datacamp course. Used to make sure all of the solve functions work properly.
        :param timeout: How long it should wait to see certain buttons
        """
        try:
            course_outline_button = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.CLASS_NAME, "css-b29ve4"))
            course_outline_button.click()
            self.t.log("Course outline button clicked")
            reset_button = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, "//button[contains(@data-cy,'outline-reset')]"))
            # Several errors can happen with the rest button loading differently
            try:
                reset_button.click()
            except selenium.common.exceptions.ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", reset_button)
            sleep(.2)
            # Presses enter twice to deal with the popups
            Alert(self.driver).accept()
            sleep(.2)
            Alert(self.driver).accept()
        except selenium.common.exceptions.TimeoutException:
            self.t.log("The Course Outline Button was not found before timeout")

    def solve_video_exercise(self, timeout: int):
        """
        Solves a Video exercise by clicking the "Got it" button.
        :param timeout: How long it should wait to see the "Got it" button
        """
        exercise_url = self.driver.current_url
        self.click_submit(timeout=timeout)
        sleep(2)
        # Sometimes the got it button just doesn't get clicked
        if self.driver.current_url == exercise_url:
            try:
                got_it_button = WebDriverWait(self.driver, timeout=2).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-cy,'submit-button')]")))
                self.driver.execute_script("arguments[0].click();", got_it_button)
                self.t.log("Clicked the Got it button")
                return True
            except selenium.common.exceptions.ElementNotInteractableException:
                self.t.log("Got it button couldn't be clicked")
                return False
            except selenium.common.exceptions.TimeoutException:
                self.t.log("Got it button not found")
                return False

    def solve_normal_exercise(self, solution: str, timeout: int) -> bool:
        """
        Solves a Normal Exercise by pasting the solution into the editor tab, clicking the "Submit Answer" button and
        then clicking the "Continue" button.
        :param solution: The correct answer to the current Normal Exercise
        :param timeout: How long it should wait to sees certain elements in the normal exercise
        """
        try:
            script_margin = self.wait_for_element(timeout, class_name="margin-view-overlays")
            sleep(1)
            # Clicks on the script to put it in focus
            script_margin.click()
            action_chain = ActionChains(self.driver)
            # TODO: Make it work for OSX
            # Sends CTRL + A
            pyperclip.copy(solution)
            sleep(.2)
            action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            # Pastes the solution
            action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        except selenium.common.exceptions.TimeoutException:
            self.t.log("Editor tab not found, most likely not a normal exercise")
        self.click_submit(timeout=timeout)
        return self.find_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout)

    # TODO: Verify answers we correct through checking for if hints are given
    def solve_bullet_exercises(self, solutions: List[str], timeout: int) -> (bool, int):
        """
        Solves a Bullet exercise by pasting the solution into the editor tab, clicking the "Submit Answer" button,
        repeating this until it has completed all of the sub exercises, then clicking the "Continue" button.
        :param solutions: The correct answer to the current Bullet exercise
        :param timeout: How long it should wait to sees certain elements in the Bullet exercise
        :return: How many solutions were used; The number of Bullet exercises
        """
        answers_are_correct = True
        number_of_exercises = "0"
        try:
            number_of_exercises = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/h5')) \
                .text[-1]
            for i in range(int(number_of_exercises)):
                script_margin = self.wait_for_element(timeout, class_name="margin-view-overlays")
                sleep(3)  # Necessary for ctrl + a to select everything properly
                # Clicks on the script to put it in focus
                script_margin.click()
                action_chain = ActionChains(self.driver)
                # Sends CTRL + A
                action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                # Copies the solution to clipboard
                pyperclip.copy(solutions[i])
                # Pastes the solution
                # TODO: Make it work for OSX
                action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                self.click_submit(timeout=timeout)
                sleep(timeout)
                # TODO: Check if this is necessary anymore
                if self.check_for_incorrect_submission(timeout=timeout):
                    answers_are_correct = False
                # Clears clipboard
                pyperclip.copy("")
            if answers_are_correct:
                return self.find_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout), int(number_of_exercises)
            self.driver.refresh()
            return self.solve_bullet_exercises(solutions, timeout)
        except selenium.common.exceptions.TimeoutException:
            self.t.log("Editor tab timed out, most likely not a bullet exercise")
            return False, int(number_of_exercises)
        except TypeError:
            self.t.log("Exercises and solving desynced, wait for restart of course")
            return False, int(number_of_exercises)

    def solve_tab_exercises(self, solutions: List[str], timeout: int) -> (bool, int):
        """
        Solves a Tab exercise by pasting the final solution into the editor tab, clicking the "Submit Answer" button,
        repeating this until it has completed all of the sub exercises, then clicking the "Continue" button.
        :param solutions: The correct answer to the current Tab exercise
        :param timeout: How long it should wait to sees certain elements in the Tab exercise
        :return: How many solutions were used; The number of Tab exercises
        """
        solutions_used = 0
        try:
            number_of_exercises = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/h5')) \
                .text[-1]
            for i in range(int(number_of_exercises)):
                try:
                    WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div')) \
                        .click()
                except (selenium.common.exceptions.TimeoutException, selenium.common.exceptions.ElementClickInterceptedException):
                    self.t.log("The Instruction bar could not be clicked or found")
                ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
                # Some Tab exercises have multiple choice questions
                possible_multiple_choice_options = len(self.driver.find_elements_by_xpath("//ul[contains(@class,'exercise--multiple-choice')]/*"))
                if possible_multiple_choice_options > 0:
                    for j in range(possible_multiple_choice_options):
                        try:
                            radio_input_button = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH,
                                f'//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div/div/div/div/div[3]/ul/li[{j + 1}]/div/div/label'))
                            radio_input_button.click()
                            self.click_submit(timeout=timeout)
                            tab_number = int(WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/h5'))
                                .text[-3])
                            sleep(1)
                            if tab_number == i + 2:
                                break
                            # This is for if the multiple choice exercise is the last exercise
                            elif tab_number == number_of_exercises:
                                if self.find_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout):
                                    self.t.log(f"It used {solutions_used} solutions!")
                                    return True, solutions_used
                        except (selenium.common.exceptions.ElementNotInteractableException, selenium.common.exceptions.ElementClickInterceptedException):
                            self.t.log("Radio button couldn't be clicked")
                        except selenium.common.exceptions.TimeoutException:
                            self.t.log("Radio button not found")
                else:
                    script_margin = self.wait_for_element(timeout, class_name="margin-view-overlays")
                    sleep(3)  # Necessary for ctrl + a to select everything properly
                    script_margin.click()  # Sometimes doesn't work
                    # Copies the solution to clipboard
                    pyperclip.copy(solutions[solutions_used])
                    solutions_used += 1
                    # Clicks on the script to put it in focus
                    script_margin.click()
                    # Sends CTRL + A
                    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                    # Pastes the solution
                    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                    self.t.log("pasted answer")
                    self.click_submit(timeout=timeout)
                    self.wait_for_element(timeout=timeout, xpath="//button[contains(@data-cy,'submit-button')]")
                    self.t.log("Found submit")
                    # Clears clipboard
                    pyperclip.copy("")
            return self.find_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout), solutions_used
        except selenium.common.exceptions.ElementNotInteractableException:
            self.t.log("Editor tab couldn't be clicked")
        except selenium.common.exceptions.TimeoutException:
            self.t.log("Number of exercises or Editor tab not found, most likely not a bullet exercise")
            return False, solutions_used
        except TypeError:
            self.t.log("Exercises and solving desynced, wait for restart of course")
            return False, solutions_used

    def solve_multiple1(self, timeout: int) -> bool:
        """
        Solves a Pure Multiple Choice exercise by sending the number that corresponds to each multiple choice option and
        the enter key until it finds the correct answer, then it clicks the "Continue" button.
        :param timeout: How long it should wait to sees certain elements in the Pure Multiple Choice exercise
        """
        # Gets the amount of the child elements (the multiple choice options) in the parent element
        WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="root"]/div/main/div[1]/section/div/div[5]/div/div/ul'))
        multiple_choice_options = len(
            self.driver.find_elements_by_xpath('//*[@id="root"]/div/main/div[1]/section/div/div[5]/div/div/ul/*'))
        for i in range(multiple_choice_options):
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, "//body")).click()
            ActionChains(self.driver).send_keys(str(i + 1), Keys.ENTER).perform()
            if self.find_continue(xpath="//button[contains(@data-cy,'completion-pane-continue-button')]", timeout=timeout):
                return True
        return self.find_continue(xpath="//button[contains(@data-cy,'completion-pane-continue-button')]", timeout=timeout)

    def solve_multiple2(self, timeout: int) -> bool:
        """
        Solves a Multiple Choice exercise by going through each of the options and checking to see if it is the correct
        one.
        :param timeout: How long it should wait to sees certain elements in the Multiple Choice exercise
        """
        # Gets the length of the child elements (the multiple choice options) in the parent element
        # TODO: Find out if this is necessary
        try:
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH,
                '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul'))
        except selenium.common.exceptions.ElementNotInteractableException:
            self.t.log("Radio button couldn't be clicked")
        except selenium.common.exceptions.TimeoutException:
            self.t.log("Radio button not found")

        multiple_choice_options = len(self.driver.find_elements_by_xpath('//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul/*'))
        for i in range(multiple_choice_options):
            try:
                radio_input_button = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH,
                    f'//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul/li[{i + 1}]/div/div/label'))
                radio_input_button.click()
                self.t.log("Clicked a radio button")
                self.click_submit(timeout=timeout)
                if self.find_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout):
                    return True
            except selenium.common.exceptions.ElementNotInteractableException:
                self.t.log("Radio button couldn't be clicked")
            except selenium.common.exceptions.TimeoutException:
                self.t.log("Radio button not found")
            sleep(1)  # Might not be necessary
        return self.find_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout)

    def solve_drag_and_drop(self, timeout: int) -> bool:
        """
        Skips drag and drop by showing answer, clicking submit answer, and clicking continue.
        :param timeout: How long it should wait to sees certain elements in the drag and drop exercise
        """
        try:
            show_hint_button = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="root"]/div/main/div[2]/div/div[1]/section/div[1]/div[5]/div/section/nav/div/button'))
            show_hint_button.click()
            show_answer_button = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="root"]/div/main/div[2]/div/div[1]/section/div[1]/div[5]/div/section/nav/div/button'))
            show_answer_button.click()
            self.click_submit(timeout=timeout)
            sleep(1)
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            # It's hard for it to mess this up
            return True
        except selenium.common.exceptions.TimeoutException:
            self.t.log("One of the buttons not found before timeout, most likely was not a drag and drop exercise")
            return False

    # Only bullet exercises seem to be having this problem
    def check_for_incorrect_submission(self, timeout: int, xpath="//button[contains(@aria-label,'Incorrect')]") -> bool:
        """
        Checks to see if the answer entered was incorrect by checking for an element that marks it
        :param timeout: How long it should wait to find the element
        :param xpath: XPATH of the element, default should work
        :return: Boolean for if it found the element or not
        """
        try:
            WebDriverWait(self.driver, timeout=timeout / 2).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.t.log("Answer was wrong")
            return True
        except selenium.common.exceptions.TimeoutException:
            return False

    def click_submit(self, timeout: int, xpath="//button[contains(@data-cy,'submit-button')]") -> bool:
        """
        Clicks the submit button for an exercise.
        :param timeout: How long it should wait to find the submit button
        :param xpath: The xpath of the submit button, default value should work for all of them
        :return: A boolean for if it successfully clicked the submit button
        """
        try:
            WebDriverWait(self.driver, timeout=timeout).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            self.t.log("Clicked the Submit button")
            return True
        except selenium.common.exceptions.ElementNotInteractableException:
            self.t.log("Submit button couldn't be clicked")
            return False
        except selenium.common.exceptions.TimeoutException:
            self.t.log("Submit button not found")
            return False

    def wait_for_element(self, timeout: int, xpath="", class_name=""):
        """
        Waits for an element and returns one if found. Can use either xpath or class name to find the element.
        :param timeout: How long it should wait to find the element
        :param xpath: The xpath of the element (don't specify if searching by class name)
        :param class_name: The class name of the element (don't specify if searching by xpath)
        """
        try:
            element = None
            if xpath != "":
                element = WebDriverWait(self.driver, timeout=timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elif class_name != "":
                element = WebDriverWait(self.driver, timeout=timeout).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
            else:
                raise ValueError
            if type(element) == WebElement:
                return element
        except selenium.common.exceptions.StaleElementReferenceException:
            self.t.log("Element was stale")
            self.wait_for_element(timeout, xpath="//button[contains(@data-cy,'submit-button')]")
        except selenium.common.exceptions.TimeoutException:
            self.t.log("Element not found")
            return
        if xpath != "":
            self.wait_for_element(timeout, xpath=xpath)
        elif class_name != "":
            self.wait_for_element(timeout, class_name=class_name)

    def find_continue(self, xpath: str, timeout: int) -> bool:
        """
        Returns a boolean based on if the continue button was found or not.
        :param timeout: How long it should wait to find the continue button
        :param xpath: The xpath of the continue button
        """
        try:
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, xpath))
            self.t.log("Found the Continue button")
            return True
        except selenium.common.exceptions.TimeoutException:
            try:
                WebDriverWait(self.driver, timeout=2).until(lambda d: d.find_element(By.XPATH, '//*[@id="root"]/div/main/div[2]/div/div/div[3]/button'))
                self.t.log("Found the continue button")
                return True
            except selenium.common.exceptions.TimeoutException:
                self.t.log("Continue button not found")
                return False
