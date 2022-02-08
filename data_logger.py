"""
Monitoring.py class:

the class responsibility is to enable the log capabilities for the instantiated model objects, and to save it into a csv
file. Because of the similarity, the logs are also saved into a plain text .txt file and printed on the console.

the second class responsibility is to take all the log output of the simulator and merge it into one unique csv file.
The merged file has to be consistent with time order.

The responsibility is achieved leveraging pandas, turning the log files into dataframes and then merging them performing
a full-outer-join.

"""

import os


# TODO: set initialization as private.
class DataLogger(object):
    def __init__(self, path, global_filename_txt='none', single_filename_txt='none', single_filename_csv='none'):
        self.path = path

        self.global_filename_txt = global_filename_txt
        self.complete_global_filename_txt = self.path + "\\" + self.global_filename_txt

        self.single_filename_txt = single_filename_txt
        self.complete_single_filename_txt = self.path + "\\" + self.single_filename_txt

        self.single_filename_csv = single_filename_csv
        self.heading = self.single_filename_csv.split("log.")[0].strip()
        self.complete_single_filename_csv = self.path + "\\" + self.single_filename_csv

        self._initialize_global_log_txt_file()
        self._initialize_single_log_txt_file()
        self._initialize_single_log_csv_file()

    def _initialize_global_log_txt_file(self):
        if self.global_filename_txt != 'none':
            try:
                os.remove(self.complete_global_filename_txt)
            except FileNotFoundError:
                print("The log file has not been found in the directory, creating a new one.")
                with open(self.complete_global_filename_txt, "w") as f:
                    f.close()

    def _initialize_single_log_txt_file(self):
        if self.single_filename_txt != 'none':
            try:
                os.remove(self.complete_single_filename_txt)
            except FileNotFoundError:
                print("The log file has not been found in the directory, creating a new one.")
                with open(self.complete_single_filename_txt, "w") as f:
                    f.close()

    def _initialize_single_log_csv_file(self):
        if self.single_filename_csv != 'none':
            try:
                with open(self.complete_single_filename_csv, "w") as f:
                    f.close()
            except FileExistsError:
                print('The log file already exists, cleaning up and creating a new one.')
                os.remove(self.complete_single_filename_csv)
                with open(self.complete_single_filename_csv, "w") as f:
                    f.close()
            # TODO: Maybe instead of time process should be written the number of the processed material ...
            #  or should be added as a column
            with open(self.complete_single_filename_csv, "a") as f:
                f.write('step,input ' + self.heading + ',time process ' + self.heading + ',output ' +
                        self.heading + ',produced,failure ' + self.heading + ',MTTF ' + self.heading + ',repair time '
                        + self.heading + ', expectation_not_met''\n')
                f.close()

    def write_global_log_txt(self, text):
        with open(self.complete_global_filename_txt, "a") as f:
            f.write(text)
            f.close()

    def write_single_log_txt(self, text):
        with open(self.complete_single_filename_txt, "a") as g:
            g.write(text)
            g.close()

    def write_log_csv(self, data_list):
        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR, expectation_not_met
        text = ''
        # For each line in the data_list ...
        for i in range(len(data_list)):
            # Refactoring True and False into 1 and 0
            # ... for each element in the data_list ...
            for j in range(len(data_list[i])):
                # ... if the element is a True ...
                if data_list[i][j] is True:
                    data_list[i][j] = 1
                # ... if the element is a False ...
                if data_list[i][j] is False:
                    data_list[i][j] = 0
                #
                # ... if the element is the last in the line ...
                if j+1 == len(data_list[i]):
                    # ... add the string to the text and a newline character.
                    text = text + str(data_list[i][j]) + "\n"
                else:
                    # ... else, just add the string to the text.
                    text = text + str(data_list[i][j]) + ","

        with open(self.complete_single_filename_csv, "a") as f:
            f.write(text)
            f.close()
