"""
savedata.py: Responsible for reading and writing to the save.json file and remembering certain useful things like passwords
Contributors: Andrew Combs
"""

import json
import errno
import os

# TODO: store data better
version = 1.0
authors = ["Jackson Elia", "Andrew Combs"]
functionality = "Full Auto"

visible = False
timeout = 15

username = ""
password = ""


class JSONManager(object):
    def __init__(self, fp: str=""):
    
        if os.path.exists(fp): 
            self.fp = fp + "\save.json"
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), fp)
            return
        
        # TODO: Have a better way of making sure that all options exist in the save file
        if not os.path.exists(self.fp):    
            self.buffer = {
                "version": version,
                "authors": authors,
                "functionality": functionality,
                "visible": visible,
                "timeout": timeout,
                "username": username,
                "password": password,
            }
            dump = json.dumps(self.buffer)
            with open(self.fp, "w") as jsonfile:
                jsonfile.write(dump)
        
        return
    
    def read(self) -> dict:
        with open(self.fp, "r") as jsonfile:
            data = jsonfile.read()
            self.buffer = json.loads(data)
          
        return self.buffer
    
    def write(self, data: dict):
        self.buffer = data
        dump = json.dumps(self.buffer)
        with open(self.fp, "w") as jsonfile:
            jsonfile.write(dump)
    