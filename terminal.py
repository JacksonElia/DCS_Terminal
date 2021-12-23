'''
terminal.py: Responsible for GUI and input handling
Contributors: Andrew Combs
'''

import os
import sys
import keyboard

# might remove the D in front of all the names but for now it helps with making it not generic

class DTheme(object):
    def __init__(self, defaul: tuple, log: tuple, error: tuple, syntax: tuple):
        self.default = default  # All effects applied to regular text (escape sequences)
        self.log = log  # All effects applied to logging data (in order: (brackets, info, message))
        self.error = error  # All effects applied to error messages
        self.syntax = syntax  # Syntax highlighting (in order: (keywords, comments, functions/classes, symbols, quotes))
        return

        
class DSettings(object):
    def __init__(self):
        self.verbose = 1  # How extensive the logging is (0-2)
        return

# Pain
class DColors(object):
    black = u"\u001b[30m"
    bblack = u"\u001b[30;1m"
    bg_black = u"\u001b[40m"
    bg_bblack = u"\u001b[40;1m"

    red = u"\u001b[31m"
    bred = u"\u001b[31;1m"
    bg_red = u"\u001b[41m"
    bg_bred = u"\u001b[41;1m"
    
    green = u"\u001b[32m"
    bgreen = u"\u001b[32;1m"
    bg_green = u"\u001b[42m"
    bg_bgreen = u"\u001b[42;1m"
    
    yellow = u"\u001b[33m"
    byellow = u"\u001b[33;1m"
    bg_yellow = u"\u001b[43m"
    bg_byellow = u"\u001b[43;1m"

    blue = u"\u001b[34m"
    bblue = u"\u001b[34;1m"
    bg_blue = u"\u001b[44m"
    bg_bblue = u"\u001b[44;1m"
    
    magenta = u"\u001b[35m"
    bmagenta = u"\u001b[35;1m"
    bg_magenta = u"\u001b[45m"
    bg_bmagenta = u"\u001b[45;1m"
    
    cyan = u"\u001b[36m"
    bcyan = u"\u001b[36;1m"
    bg_cyan = u"\u001b[46m"
    bg_bcyan = u"\u001b[46;1m"
    
    white = u"\u001b[36m"
    bwhite = u"\u001b[36;1m"
    bg_white = u"\u001b[46m"
    bg_bwhite = u"\u001b[46;1m"


# TODO: actually code, better function explanations
class DTerminal(object):
    def __init__(self, theme: DTheme, settings: DSettings):
        self.theme = theme
        self.settings = settings
        
        self.buffer = []
        
        # for windows this is required to get escape codes to work
        os.system("cls" if os.name == "nt" else "clear")
        
        return
        
    def startup(self):
        """
        Purely visual thing, just because it looks cool
        """
        title = """
888888ba   a88888b. .d88888b     d888888P                              oo                   dP 
88    `8b d8'   `88 88.    "'       88                                                      88 
88     88 88        `Y88888b.       88    .d8888b. 88d888b. 88d8b.d8b. dP 88d888b. .d8888b. 88 
88     88 88              `8b       88    88ooood8 88'  `88 88'`88'`88 88 88'  `88 88'  `88 88 
88    .8P Y8.   .88 d8'   .8P       88    88.  ... 88       88  88  88 88 88    88 88.  .88 88 
8888888P   Y88888P'  Y88888P        dP    `88888P' dP       dP  dP  dP dP dP    dP `88888P8 dP 
"""
        print(title)
        
    def cloc(self, x: int, y: int):
        """
        Changes cursor location.
        """
        print(f"\033[{y};{x}H")
    
    # Prompts user input
    def prompt(self) -> str:
        input("> ")
        return
    
    # Prints at a location
    def disp(self):
        return
    
    # Logs using vital info
    def log(self):
        return
    
    # Draws a sprite at a location
    def sprite_draw(self):
        return
        
    # Draws a block of code with syntax highlighting
    def code_block(self):
        return



# Test code
def main():
    return

if __name__ == "__main__":

    default = ()
    log = ()
    error = ()
    syntax = ()
    
    theme = DTheme(default, log, error, syntax)
    settings = DSettings()
    terminal = DTerminal(theme=theme, settings=settings)
    
    terminal.startup()
    terminal.prompt()