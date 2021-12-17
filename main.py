import undetected_chromedriver as uc
from SeleniumManager import *

# ⬇⬇⬇ What to Change ⬇⬇⬇ Placeholder until we get the json file and user input setup
email = "johnsmith@gmail.com"
password = "573869837"
link = "https://campus.datacamp.com/courses/joining-data-with-pandas/advanced-merging-and-concatenating?ex=4"
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
    ids = selenium_manager.get_page_ids(link)
    answers = selenium_manager.api_lookup(ids)
    # [print(f"\nAnswer #{i + 1}:\n{a}\n") for i, a in enumerate(answers)]
    driver.quit()  # Necessary for proper closing of driver, will leave a footprint in ram otherwise


if __name__ == "__main__":
    main()