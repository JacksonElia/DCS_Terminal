'''
parser.py: Responsible for parsing command arguments, may include further functions for formatting terminal text
Contributors: Andrew Combs
'''

import types
from ast import literal_eval


# TODO: Better naming conventions
class Parser(object):

    def __init__(self, commands: list):
        self.lookup = {}

        for command in commands:
            self.add_command(*command)
    
    
    def add_command(self, command: str, function: types.FunctionType, args: list, flags: list):
        '''
        Adds a command to the parser's local dictionary.
        command [str]: The name of the argument
        function [function]: The function the command passes arguments for
        args [list]: A list of types in order of how arguments should be passed
        flags [list]: A list of strings containing the name of boolean flag values
        '''
        self.lookup[command] = (function, args, flags)

    # TODO: Make code more readable
    def parse(self, given: str) -> tuple:
        '''
        Parses a string using the local parser's dictionary
        given [str]: input string to be parsed
        '''
        nodes = given.split(" ")
        nodes = [n for n in nodes if n]

        cmd = nodes[0]
        if cmd not in self.lookup.keys(): return ("ERROR", "COMMAND NOT FOUND", f"{cmd} DOES NOT EXIST")
        func = self.lookup[cmd]

        args = nodes[1:]
        flags = [i for i in args if "--" in i]

        # this is rather janky
        # Parsing arguments (*args)
        std_types = [int, float, str]
        parsed_args = []
        for t, arg in zip(func[1], args):
            try:
                if t in std_types:
                    parsed_args.append(t(arg))
                else:
                    parsed_args.append(t(literal_eval(arg)))
            except ValueError:
                return ("ERROR", "MISMATCHED TYPES", f"{type(arg)} IS NOT {t}")

        # Parsing flags (**kwargs)
        parsed_flags = {}
        for flag in flags:
            if flag in func[2]:
                parsed_flags[flag[2:]] = True
            else:
                return ("ERROR", "FLAG NOT FOUND", f"FLAG {flag} DOES NOT EXIT IN FUNCTION")
        
        info = (cmd, tuple(parsed_args), parsed_flags)
        return info

    # TODO: Better error checking/logging
    def execute(self, info=None):
        '''
        Executes a function given info parameters
        info [tuple]: info required in order of (command_name, args, kwargs)
        '''
        cmd = info[0]

        # Actual error logging needed here
        if cmd == "ERROR": return info
        if cmd not in self.lookup.keys(): return ("ERROR", "COMMAND NOT FOUND", f"{cmd} DOES NOT EXIST")

        func = self.lookup[cmd]
        return func[0](*info[1], **info[2])