"""
main.py: Responsible for all main functions and testing
Contributors: Jackson Elia, Andrew Combs
"""
import os

from terminal_parser import Parser
from terminal import DTerminal, DColors, DTheme
from savedata import JSONManager
from seleniummanager import SeleniumManager
from webdriver_auto_update import check_driver

import time
import undetected_chromedriver as uc
import selenium


# System commands
def cmd_exit(t: DTerminal, driver: selenium.webdriver):
    t.log("Quitting chrome driver...")
    driver.quit()
    t.log("Driver successfully quit.")
    exit()


def cmd_info(t: DTerminal, data: dict):
    # TODO: make less ugly
    t.disp(title="About",
           message=f"Version: {data['version']}\nFunctionality: {data['functionality']}\nAuthors: {', '.join(data['authors'])}\n")


def cmd_clear(t: DTerminal):
    t.clear()
    hcolor = DColors.rgb(20, 148, 20)
    t.header("DCS Terminal", DColors.bold + DColors.reverse + hcolor + DColors.bg_black)


def cmd_modify_savedata(data_name: str, new_data: object, t: DTerminal, jm: JSONManager):
    data = jm.read()
    if data_name not in data.keys():
        return "ERROR", "Data block not found", f'Data block "{data_name}" was not found in save file'

    data[data_name] = new_data
    jm.write(data)
    t.disp("New Save Data Written", f"{new_data} was written to {data_name}")

    return


def cmd_help(command: str, t: DTerminal, p: Parser):
    # Gives an type description of commands
    if command not in p.lookup.keys():
        t.disp("", f"Command '{command}' does not exist.")
        return

    func = p.lookup[command]
    title = f"Command: {command}"
    # t.log(str(func))
    info = ""
    if len(func[1]) == 0:
        info = "This command takes no arguments\n"
    else:
        info = f"This command takes {len(func[1])} argument(s).\nOrder: {(', '.join([str(i) for i in func[1]]))}\n"
    if len(func[2]) == 0:
        info += "\nThis command has no flags\n"
    else:
        info += f"\nThis command takes {len(func[2])} argument(s).\n{(', '.join([str(i) for i in func[2]]))}\n"
    t.disp(title, info)
    return


def cmd_cmdlist(t: DTerminal, p: Parser):
    for cmd in p.lookup.keys():
        t.disp("", f"{cmd}")


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


def cmd_checkcredentials(t: DTerminal, jm: JSONManager, autoclear=False):
    settings = jm.read()
    t.log(f"Current Username: {settings['username']}")
    t.log(f"Current Password: {settings['password']}\n")
    if autoclear:
        time.sleep(3)
        cmd_clear(t)


def cmd_login(sm: SeleniumManager, t: DTerminal, jm: JSONManager):
    settings = jm.read()
    sm.login(settings["username"], settings["password"], timeout=15)
    return


def cmd_course_autosolve(start_link: str, sm: SeleniumManager, t: DTerminal, jm: JSONManager, autoreset=False):
    settings = jm.read()
    sm.auto_solve_course(starting_link=start_link, timeout=settings["timeout"], reset_course=autoreset,
                         wait_length=settings["wait"])
    return


def cmd_get_answers(start_link: str, sm: SeleniumManager, t: DTerminal):
    solutions, info = sm.get_solutions_and_exercises(start_link)
    for i, b in zip(info, solutions):
        title = f"{i['type']} {i['number']} ({i['link']})"
        t.disp(title, b + "\n")


def main():
    # Makes sure chromedriver is up to date
    check_driver("")

    theme = DTheme(
        default=(DColors.green + DColors.bold + DColors.reverse, DColors.bwhite, DColors.green),
        log=(DColors.bgreen + DColors.rgb(10, 60, 10, True), DColors.green + DColors.rgb(10, 60, 10, True),
             DColors.bwhite + DColors.rgb(70, 200, 70)),
        error=(DColors.red + DColors.bold + DColors.reverse, DColors.bred, DColors.rgb(200, 70, 70)),
    )

    terminal = DTerminal(theme=theme)
    terminal.startup()

    dir = os.path.dirname(os.path.realpath(__file__))
    jsonmanager = JSONManager(fp=dir)
    terminal.log("JSON manager loaded")
    settings = jsonmanager.read()

    options = uc.ChromeOptions()
    terminal.log("Selenium options loaded")
    if not settings["visible"]:
        terminal.log("Chrome startup window disabled.")
        options.add_argument('--no-startup-window')
        options.add_argument('--headless')
    # options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile": {"password_manager_enabled": False}})
    driver = uc.Chrome(options=options)
    terminal.log("--Undetected driver successfully created--")

    seleniummanager = SeleniumManager(driver=driver, terminal=terminal)
    terminal.log("*Selenium manager initialized*")

    # all commands need to be put in here
    commands = [
        ("exit", cmd_exit, [], [], {"t": terminal, "driver": driver}),
        ("info", cmd_info, [], [], {"t": terminal, "data": settings}),
        ("clear", cmd_clear, [], [], {"t": terminal}),
        ("modify", cmd_modify_savedata, [str, object], [], {"t": terminal, "jm": jsonmanager}),
        ("setcreds", cmd_setcredentials, [str, str], [], {"t": terminal, "jm": jsonmanager}),
        ("checkcreds", cmd_checkcredentials, [], ["--autoclear"], {"t": terminal, "jm": jsonmanager}),
        ("login", cmd_login, [], [], {"sm": seleniummanager, "t": terminal, "jm": jsonmanager}),
        ("solvecourse", cmd_course_autosolve, [str], ["--autoreset"],
         {"sm": seleniummanager, "t": terminal, "jm": jsonmanager}),
        ("answers", cmd_get_answers, [str], [], {"sm": seleniummanager, "t": terminal})
    ]
    parser = Parser(commands)
    parser.add_command("help", cmd_help, [str], [], {"t": terminal, "p": parser})
    parser.add_command("cmdlist", cmd_cmdlist, [], [], {"t": terminal, "p": parser})

    terminal.log("Parser initialized.")
    terminal.log("Startup successful.")

    time.sleep(1)

    terminal.clear()
    terminal.header("DCS Terminal", DColors.bold + DColors.reverse + DColors.rgb(20, 148, 20) + DColors.bg_black)

    while True:
        inp = terminal.prompt()
        if inp == "": continue
        info = parser.parse(inp)

        if info[0] == "ERROR":
            terminal.error(info[1], info[2])
            continue

        result = parser.execute(info)
        # Rough error logging
        if result and result[0] == "ERROR":
            terminal.error(result[1], result[2])
            continue


if __name__ == "__main__":
    main()
