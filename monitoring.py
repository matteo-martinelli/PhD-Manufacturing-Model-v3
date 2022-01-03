"""
Monitoring.py class:

Class containing the global variables for the model.
"""

import os


class DataLogger(object):
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.complete_filename = self.path + "\\" + self.filename
        self.initialize_log_file()

    def write_log(self, text):
        with open(self.complete_filename, "a") as f:
            f.write(text)
            f.close()

    def initialize_log_file(self):
        try:
            os.remove(self.complete_filename)
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            os.makedirs(self.path)
            with open(self.complete_filename, "w") as f:
                f.close()
