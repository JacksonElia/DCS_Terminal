"""
savedata.py: Responsible for reading and writing to the save.json file and remembering certain useful things like passwords
Contributors: Andrew Combs
"""

import json
import sys
import os


class JSONManager(object):
    def __init__(self, fp: str=""):
        