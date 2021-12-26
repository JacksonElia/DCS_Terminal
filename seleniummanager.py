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
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep


class SeleniumManager:
    driver: selenium.webdriver

    def __init__(self, driver: selenium.webdriver):
        self.driver = driver

    # TODO: Handle when the user isn't logged in correctly
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
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.ID, "user_email")).send_keys(username)
            print("Username Entered")
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Username Error")
            return
        except selenium.common.exceptions.TimeoutException:
            print("Username Field Timed Out Before Found")
            return

        # Next button click
        self.driver.find_element(By.XPATH, '//*[@id="new_user"]/button').click()
        sleep(1)

        # Password find and enter
        try:
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.ID, "user_password")).send_keys(password)
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
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="single-spa-application:@dcmfe/mfe-app-atlas-header"]/nav/div[4]/div[2]/div/button'))
            print("Sign In Successful")
        except selenium.common.exceptions.TimeoutException:
            print("Error Verifying Sign In")

    def get_solutions_and_exercises(self, link: str) -> (list, [dict]):
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

                    # Reverses list so it doesn't mess with index when removing the character
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

    def auto_solve_course(self, starting_link: str, timeout=10, reset_course=True):
        if reset_course:
            self.driver.get(starting_link)
            self.reset_course(timeout)
        chapter_link = starting_link
        done_with_course = False
        while not done_with_course:
            solutions, exercises = self.get_solutions_and_exercises(chapter_link)
            next_chapter, chapter_link = self.auto_solve_chapter(exercise_list=exercises, solutions=solutions, timeout=timeout)
            done_with_course = not next_chapter

    # TODO: Let user set how long in between solving
    def auto_solve_chapter(self, exercise_list: [dict], solutions: [str], wait_length=0, timeout=10) -> (bool, str):
        """
        Automatically solves a Datacamp chapter, if it desyncs it will redo the chapter.
        :param exercise_list: List of dicts that contain information about each exercise
        :param solutions: List of solutions for each exercises
        :param wait_length: Delay in between exercises
        :param timeout: How long it waits for elements to appear
        :return: A boolean for if there is another chapter in the course and a string with the url to that chapter
        """
        self.driver.get(exercise_list[0]["link"])
        for exercise in exercise_list:
            # User can set this to add delay in between exercises
            sleep(wait_length)
            match exercise["type"]:
                case "VideoExercise":
                    print("Solving Video Exercise")
                    self.solve_video_exercise(timeout)
                case "NormalExercise":
                    print("Solving Normal Exercise")
                    self.solve_normal_exercise(solutions[0], timeout)
                    solutions.pop(0)
                case "BulletExercise":
                    print("Solving Bullet Exercise")
                    solutions_used = self.solve_bullet_exercises(solutions, timeout)
                    for i in range(solutions_used):
                        solutions.pop(0)
                case "TabExercise":
                    print("Solving Tab Exercise")
                    solutions_used = self.solve_tab_exercises(solutions, timeout)
                    for i in range(solutions_used):
                        solutions.pop(0)
                case "PureMultipleChoiceExercise":
                    print("Solving Pure Multiple Choice Exercise")
                    self.solve_multiple1(timeout)
                case "MultipleChoiceExercise":
                    print("Solving Multiple Choice Exercise")
                    self.solve_multiple2(timeout)
                case "DragAndDropExercise":
                    print("Solving Drag and Drop Exercise")
                    self.solve_drag_and_drop(timeout)
                case _:
                    print("What entered was an exercise not on this match statement")
        # Refreshes the page to deal with popup
        self.driver.refresh()
        if exercise_list[-1]["type"] == "VideoExercise":
            self.click_submit(timeout)
        else:
            # Clicks on the page, then enters in shortcut for the arrow button at the top
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, "//body")).click()
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys("k").key_up(Keys.CONTROL).perform()
            print("Sent ctrl + k")
        # Waiting for next chapter to load
        sleep(timeout)
        if "https://app.datacamp.com/learn/courses" not in self.driver.current_url:
            return True, self.driver.current_url
        else:
            print("Finished Course")
            return False, ""

    def reset_course(self, timeout: int):
        """
        Resets all progress on the Datacamp course. Used to make sure all of the solve functions work properly.
        :param timeout: How long it should wait to see certain buttons
        """
        try:
            course_outline_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.CLASS_NAME, "css-b29ve4"))
            course_outline_button.click()
            print("Course outline button clicked")
            reset_button = WebDriverWait(self.driver, timeout=timeout) \
                .until(lambda d: d.find_element(By.XPATH, "//button[contains(@data-cy,'outline-reset')]"))
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
            print("The Course Outline Button was not found before timeout")

    def solve_video_exercise(self, timeout: int):
        """
        Solves a Video exercise by clicking the "Got it" button.
        :param timeout: How long it should wait to see the "Got it" button
        """
        self.click_submit(timeout=timeout)
        # Continue only appears about 1/6 of the time
        self.click_continue(xpath='//*[@id="root"]/div/main/div[2]/div/div/div[3]/button', timeout=timeout)

    def solve_normal_exercise(self, solution: str, timeout: int):
        """
        Solves a Normal Exercise by pasting the solution into the editor tab, clicking the "Submit Answer" button and
        then clicking the "Continue" button.
        :param solution: The correct answer to the current Normal Exercise
        :param timeout: How long it should wait to sees certain elements in the normal exercise
        """
        try:
            script_margin = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="rendered-view"]/div/div/div[3]/div[1]'))
            # Clicks on the script to put it in focus
            script_margin.click()

            sleep(1)

            action_chain = ActionChains(self.driver)
            # TODO: Make it work for OSX
            # Sends CTRL + A
            action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            pyperclip.copy(solution)
            # Pastes the solution
            action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
        except selenium.common.exceptions.TimeoutException:
            print("Editor tab not found, most likely not a normal exercise")
        self.click_submit(timeout=timeout)
        self.click_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout)

    def solve_bullet_exercises(self, solutions: [str], timeout: int) -> int:
        """
        Solves a Bullet exercise by pasting the solution into the editor tab, clicking the "Submit Answer" button,
        repeating this until it has completed all of the sub exercises, then clicking the "Continue" button.
        :param solutions: The correct answer to the current Bullet exercise
        :param timeout: How long it should wait to sees certain elements in the Bullet exercise
        :return: How many solutions were used; The number of Bullet exercises
        """
        solutions_used = 0
        try:
            number_of_exercises = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[1]/div/div/h5')) \
                .text[-1]
            for i in range(int(number_of_exercises)):
                script_margin = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="rendered-view"]/div/div/div[3]/div[1]'))
                # Clicks on the script to put it in focus
                script_margin.click()
                sleep(2)  # Necessary for ctrl + a to select everything properly
                action_chain = ActionChains(self.driver)
                # Sends CTRL + A
                action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                # Copies the solution to clipboard
                pyperclip.copy(solutions[i])
                # Pastes the solution
                # TODO: Make it work for OSX
                action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                sleep(2)
                self.click_submit(timeout=timeout)
                # Clears clipboard
                pyperclip.copy("")
            self.click_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout)
            solutions_used = int(number_of_exercises)
            return solutions_used
        except selenium.common.exceptions.TimeoutException:
            print("Editor tab timed out, most likely not a bullet exercise")
            return solutions_used
        except TypeError:
            print("Exercises and solving desynced, wait for restart of course")

    def solve_tab_exercises(self, solutions: [str], timeout: int) -> int:
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
                script_margin = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, '//*[@id="rendered-view"]/div/div/div[3]/div[1]'))
                # Some Tab exercises have multiple choice questions
                possible_multiple_choice_options = len(self.driver.find_elements_by_xpath('//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div/div/div/div/div[3]/ul/*'))
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
                            elif tab_number == number_of_exercises:
                                self.click_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout)
                                return solutions_used
                        except selenium.common.exceptions.ElementNotInteractableException:
                            print("Radio button couldn't be clicked")
                        except selenium.common.exceptions.TimeoutException:
                            print("Radio button not found")
                else:
                    # Copies the solution to clipboard
                    pyperclip.copy(solutions[solutions_used])
                    solutions_used += 1
                    # Clicks on the script to put it in focus
                    script_margin.click()
                    sleep(2)  # Necessary, selects things incorrectly if this isn't 2 seconds
                    action_chain = ActionChains(self.driver)
                    # Sends CTRL + A
                    action_chain.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                    # Pastes the solution
                    action_chain.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()
                    print("pasted answer")
                    sleep(2)
                    self.click_submit(timeout=timeout)
                    # Clears clipboard
                    pyperclip.copy("")
            self.click_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout)
            return solutions_used
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Editor tab couldn't be clicked")
        except selenium.common.exceptions.TimeoutException:
            print("Number of exercises or Editor tab not found, most likely not a bullet exercise")
            return solutions_used
        except ValueError:
            print("Exercises and solving desynced, wait for restart of course")

    # TODO: Optimize timeouts
    def solve_multiple1(self, timeout: int):
        """
        Solves a Pure Multiple Choice exercise by sending the number that corresponds to each multiple choice option and
        the enter key until it finds the correct answer, then it clicks the "Continue" button.
        :param timeout: How long it should wait to sees certain elements in the Pure Multiple Choice exercise
        """
        # Gets the amount of the child elements (the multiple choice options) in the parent element
        multiple_choice_options = len(self.driver.find_elements_by_xpath('//*[@id="root"]/div/main/div[1]/section/div/div[5]/div/div/ul/*'))
        for i in range(multiple_choice_options):
            ActionChains(self.driver).send_keys(str(i + 1), Keys.ENTER).perform()
            if self.click_continue(xpath="//button[contains(@data-cy,'completion-pane-continue-button')]", timeout=timeout):
                break

    def solve_multiple2(self, timeout: int):
        """
        Solves a Multiple Choice exercise by going through each of the options and checking to see if it is the correct
        one.
        :param timeout: How long it should wait to sees certain elements in the Multiple Choice exercise
        """
        # Gets the length of the child elements (the multiple choice options) in the parent element
        multiple_choice_options = len(self.driver.find_elements_by_xpath(
            '//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul/*'))
        for i in range(multiple_choice_options):
            try:
                radio_input_button = WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH,
                    f'//*[@id="gl-aside"]/div/aside/div/div/div/div[2]/div[2]/div/div/div[2]/ul/li[{i + 1}]/div/div/label'))
                radio_input_button.click()
                print("Clicked a radio button")
                self.click_submit(timeout=timeout)
                if self.click_continue(xpath="//button[contains(@data-cy,'next-exercise-button')]", timeout=timeout):
                    break
            except selenium.common.exceptions.ElementNotInteractableException:
                print("Radio button couldn't be clicked")
            except selenium.common.exceptions.TimeoutException:
                print("Radio button not found")
            sleep(1)  # Might not be necessary

    # TODO: Make drag and drop work
    def solve_drag_and_drop(self, timeout: int):
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
            return
        except selenium.common.exceptions.TimeoutException:
            print("One of the buttons not found before timeout, most likely was not a drag and drop exercise")

    def click_submit(self, timeout: int, xpath="//button[contains(@data-cy,'submit-button')]") -> bool:
        """
        Clicks the submit button for an exercise.
        :param timeout: How long it should wait to find the submit button
        :param xpath: The xpath of the submit button, default value should work for all of them
        :return: A boolean for if it successfully clicked the submit button
        """
        try:
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, xpath)).click()
            print("Clicked the Submit button")
            return True
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Submit button couldn't be clicked")
            return False
        except selenium.common.exceptions.TimeoutException:
            print("Submit button not found")
            return False

    def click_continue(self, xpath: str, timeout: int) -> bool:
        """
        Clicks the continue button for an exercise and deals with the randomly occurring full page continue button.
        :param timeout: How long it should wait to find the continue button
        :param xpath: The xpath of the continue button
        :return: A boolean for if it successfully clicked the continue button
        """
        try:
            WebDriverWait(self.driver, timeout=timeout).until(lambda d: d.find_element(By.XPATH, xpath)).click()
            print("Clicked the Continue button")
            return True
        except selenium.common.exceptions.ElementNotInteractableException:
            print("Continue button couldn't be clicked")
            return False
        except selenium.common.exceptions.TimeoutException:
            try:
                WebDriverWait(self.driver, timeout=2).until(lambda d: d.find_element(By.XPATH, '//*[@id="root"]/div/main/div[2]/div/div/div[3]/button')).click()
                print("Clicked the continue button")
                return True
            except selenium.common.exceptions.ElementNotInteractableException:
                print("Continue button couldn't be clicked")
                return False
            except selenium.common.exceptions.TimeoutException:
                print("Continue button not found")
                return False
