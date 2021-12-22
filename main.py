import undetected_chromedriver as uc
from SeleniumManager import *

# ⬇⬇⬇ What to Change ⬇⬇⬇ Placeholder until we get the json file and user input setup
email = "jgelia@students.chccs.k12.nc.us"
password = "lol"
link = "https://campus.datacamp.com/courses/joining-data-with-pandas/data-merging-basics?ex=7"
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
    solution = """# Merge the licenses and biz_owners table on account
licenses_owners = licenses.merge(biz_owners, on='account')

# Group the results by title then count the number of accounts
counted_df = licenses_owners.groupby('title').agg({'account':'count'})

# Sort the counted_df in desending order
sorted_df = counted_df.sort_values(by='account', ascending=False)

# Use .head() method to print the first few rows of sorted_df
print(sorted_df.head())"""

    selenium_manager.solve_normal_exercise(solution, 10)
    print(*solutions)
    sleep(100)
    driver.quit()  # Necessary for proper closing of driver, will leave a footprint in ram otherwise


if __name__ == "__main__":
    main()
