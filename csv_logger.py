"""
csv_logger.py file: CsvLogger class

the class responsibility is to enable the log capabilities for the instantiated model objects and to save them as a .csv
file.
"""

import os
import time


class CsvLogger(object):
    def __init__(self, csv_log_path, csv_log_filename):
        self._csv_log_path = csv_log_path
        # self.folder_name = time.strftime('%Y.%m.%d - %H:%M Log')
        self._csv_log_filename = csv_log_filename

        # Add later: + self.folder_name + "\\"
        self._complete_csv_filename = self._csv_log_path + "\\" + self._csv_log_filename

        # TODO: make the csv_name standard in the machine class. -> What does it mean?
        self._heading = self._csv_log_filename.split("log.")[0].strip()

    def initialise_csv_log_file(self, head):
        try:
            with open(self._complete_csv_filename, "w") as f:
                f.close()
        except FileExistsError:
            print('The log file already exists, cleaning up and creating a new one.')
            os.remove(self._complete_csv_filename)
            with open(self._complete_csv_filename, "w") as f:
                f.close()
        # TODO: Maybe instead of time process should be written the number of the processed material ...
        #  or should be added as a column
        with open(self._complete_csv_filename, "a") as f:
            f.write(head)
            f.close()

    def write_csv_log_file(self, data_list):
        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR, expectation_not_met
        text = ''

        # For each line in the data_list ...
        for i in range(len(data_list)):
            # Adding comma between data, avoiding comma at the end of the line
            # ... for each element in the data_list ...
            for j in range(len(data_list[i])):
                # ... if the element is the last in the line ...
                if j + 1 == len(data_list[i]):
                    # ... add the string to the text and a newline character.
                    text = text + str(data_list[i][j]) + "\n"
                else:
                    # ... else, just add the string to the text.
                    text = text + str(data_list[i][j]) + ","

                # TODO: NOT WORKING: modify in order to make it work. Pandas could help -> Conversion made in the log
                #  merger. Delete the following code.
                # Refactor True or False into 1 or 0.
                # ... if the element is a True ...
                if data_list[i][j] == "True":
                    # Refactor into 1
                    data_list[i][j] = 1
                # ... if the element is a False ...
                if data_list[i][j] == "False":
                    # Refactor into 0
                    data_list[i][j] = 0

        with open(self._complete_csv_filename, "a") as f:
            f.write(text)
            f.close()
