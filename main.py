"""
main.py: Responsible for all main functions and testing
Contributors: Jackson Elia, Andrew Combs
"""

import os

from parser import Parser
from terminal import DTerminal, DColors, DTheme
from savedata import JSONManager
from seleniummanager import SeleniumManager

import time
import undetected_chromedriver as uc
import selenium

# ⬇⬇⬇ What to Change ⬇⬇⬇ Placeholder until we get the json file and user input setup
email = "jgelia@students.chccs.k12.nc.us"
password = "sfjle"
link = "https://campus.datacamp.com/courses/joining-data-in-sql/set-theory-clauses?ex=14"
reset_course = False
wait_length = 0
# ⬆⬆⬆ What to Change ⬆⬆⬆

# System commands
def cmd_exit(t: DTerminal, driver: selenium.webdriver):
    t.log("Quitting chrome driver...")
    driver.quit()
    t.log("Driver successfully quit.")
    exit()
    
def cmd_info(t: DTerminal, data: dict):
    # TODO: make less ugly
    t.disp(title="About", message=f"Version: {data['version']}\nFunctionality: {data['functionality']}\nAuthors: {', '.join(data['authors'])}\n")

def cmd_clear(t: DTerminal):
    t.clear()
    hcolor = DColors.rgb(20, 148, 20)
    t.header("DCS Terminal", DColors.bold+DColors.reverse+hcolor+DColors.bg_black)

# Selenium Manager shell commands
# THIS MIGHT NOT BE A GOOD WAY TO DO IT !

# TODO: add error checking and better logging
def cmd_setcredentials(username: str, password: str, t: DTerminal, jm: JSONManager):
    settings = jm.read()
    settings["username"] = username
    t.log(f"Set new username: {username}")
    settings["password"] = password
    t.log(f"Set new password: {password}")
    jm.write(settings)
    t.log("Successfully set username and password.\n")
    
    
    return

def cmd_login(sm: SeleniumManager, t: DTerminal, jm: JSONManager):
    settings = jm.read()
    sm.login(settings["username"], settings["password"], timeout=15)
    return

def main():
    
    # TODO: make this look good
    theme = DTheme(
        default=(DColors.green+DColors.bold+DColors.reverse, DColors.bwhite, DColors.green),
        log=(DColors.bgreen+DColors.rgb(10, 60, 10, True), DColors.green+DColors.rgb(10, 60, 10, True), DColors.bwhite+DColors.rgb(70,200,70)),
        error=(DColors.red+DColors.bold+DColors.reverse, DColors.bred, DColors.rgb(200,70,70)),
        syntax=(DColors.green, DColors.blue, DColors.cyan, DColors.yellow, DColors.bred)
    )  
    
    terminal = DTerminal(theme=theme)
    terminal.startup()
    
    dir = os.path.dirname(os.path.realpath(__file__))
    jsonmanager = JSONManager(fp=dir)
    terminal.log("JSON manager loaded.")
    settings = jsonmanager.read()
    
    options = uc.ChromeOptions()
    terminal.log("Chrome options loaded.")
    if not settings["visible"]: 
        terminal.log("Chrome startup window disabled.")
        options.add_argument('--no-startup-window')
    options.add_argument('--headless')
    # options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile": {"password_manager_enabled": False}})
    driver = uc.Chrome(options=options)
    terminal.log("Chrome driver successfully created.")
    
    seleniummanager = SeleniumManager(driver)
    terminal.log("Selenium manager initialized.")
    
    # all commands need to be put in here
    commands = [
        ("exit", cmd_exit, [], [], {"t": terminal, "driver": driver}),
        ("info", cmd_info, [], [], {"t": terminal, "data": settings}),
        ("clear", cmd_clear, [], [], {"t": terminal}),
        ("setcreds", cmd_setcredentials, [str, str], [], {"t": terminal, "jm": jsonmanager}),
        ("login", cmd_login, [], [], {"sm": seleniummanager, "t": terminal, "jm": jsonmanager})
    ]
    parser = Parser(commands)
    terminal.log("Parser initialized.")
    terminal.log("Startup successful.")
    
    time.sleep(1)
    
    terminal.clear()
    terminal.header("DCS Terminal", DColors.bold+DColors.reverse+DColors.rgb(20, 148, 20)+DColors.bg_black)
    
    while True:
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

    options = uc.ChromeOptions()
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile": {"password_manager_enabled": False}})

    driver = uc.Chrome(options=options)
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
