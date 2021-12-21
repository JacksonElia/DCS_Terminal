import undetected_chromedriver as uc
from SeleniumManager import *

# ⬇⬇⬇ What to Change ⬇⬇⬇ Placeholder until we get the json file and user input setup
email = "jgelia@students.chccs.k12.nc.us"
password = "L"
link = "https://campus.datacamp.com/courses/joining-data-with-pandas/merging-tables-with-different-join-types?ex=11"
# ⬆⬆⬆ What to Change ⬆⬆⬆


def main():
    # This Hides the browser, *set as an option for the user to decide later
    # options = uc.ChromeOptions()
    #
    # options.add_argument('--no-startup-window')  # Hides the window
    # options.add_argument('--headless')  # Headless
    # options.headless = True
    #
    # driver = uc.Chrome(options=options)

    driver = uc.Chrome()

    selenium_manager = SeleniumManager(driver)
    selenium_manager.login(email, password, timeout=10)
    solutions = selenium_manager.get_solutions(link)
    selenium_manager.solve_multiple1()
    #print(*solutions)
    sleep(10)
    driver.quit()  # Necessary for proper closing of driver, will leave a footprint in ram otherwise


if __name__ == "__main__":
    main()
