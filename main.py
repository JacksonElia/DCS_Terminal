'''
main.py: Responsible for all main functions and testing
Contributors: Jackson Elia, Andrew Combs
'''

import undetected_chromedriver as uc
from seleniummanager import SeleniumManager
from parser import Parser
from terminal import DTerminal, DColors, DTheme

# ⬇⬇⬇ What to Change ⬇⬇⬇ Placeholder until we get the json file and user input setup
email = "jgelia@students.chccs.k12.nc.us"
password = "lol"
link = "https://campus.datacamp.com/courses/joining-data-with-pandas/data-merging-basics?ex=7"
# ⬆⬆⬆ What to Change ⬆⬆⬆

# System commands
def cmd_exit():
    exit()
    
def cmd_info(t: DTerminal):
    # TODO: Store version data better
    t.disp(title="About", message="Version: 1.0\nFunctionality: Full Auto\nAuthors: Jackson Elia, Andrew Combs\n")


def main():
    active=True
    
    # This can be changed later
    theme = DTheme(
        default=(DColors.green+DColors.bold+DColors.reverse, DColors.bwhite, DColors.green),
        log=(DColors.yellow, DColors.red, DColors.bwhite),
        error=(DColors.red+DColors.bold+DColors.reverse, DColors.bred, DColors.rgb(200,70,70)),
        syntax=(DColors.green, DColors.blue, DColors.cyan, DColors.yellow, DColors.bred)
    )  
    terminal = DTerminal(theme=theme)
    # all commands need to be put in here
    commands = [
        ("exit", cmd_exit, [], [], {}),
        ("info", cmd_info, [], [], {"t": terminal})
    ]
    parser = Parser(commands)
    
    terminal.startup()
    
    while active:
        inp = terminal.prompt()
        if inp == "": continue
        info = parser.parse(inp)
        if info[0] == "ERROR":
            terminal.error(info[1], info[2])
            continue
            
        parser.execute(info)
    
    
    ''' This will be removed
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
    '''

if __name__ == "__main__":
    main()
