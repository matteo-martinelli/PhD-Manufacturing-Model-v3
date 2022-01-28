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
import pandas


# TODO: think about turning private the appropriate attributes.
# TODO: re-engineer the class fields: split into a super class and 2 subclasses with specified use.
class DataLogger(object):
    def __init__(self, path, filename_txt='none', filename_csv='none'):
        self.path = path
        self.save_path = path   # TODO: check and merge with self.path

        self.filename_txt = filename_txt
        self.complete_filename_txt = self.path + "\\" + self.filename_txt

        self.filename_csv = filename_csv
        self.heading = self.filename_csv.split("log.")[0].strip()
        self.complete_filename_csv = self.path + "\\" + self.filename_csv

        self.initialize_log_txt_file()
        self.initialize_log_csv_file()

    def initialize_log_txt_file(self):
        if self.filename_txt != 'none':
            try:
                os.remove(self.complete_filename_txt)
            except FileNotFoundError:
                print("The log file has not been found in the directory, creating a new one.")
                # os.makedirs(self.path)
                with open(self.complete_filename_txt, "w") as f:
                    f.close()

    def initialize_log_csv_file(self):
        if self.filename_csv != 'none':
            try:
                with open(self.complete_filename_csv, "w") as f:
                    f.close()
            except FileExistsError:
                print('The log file already exists, cleaning up and creating a new one.')
                os.remove(self.complete_filename_csv)
                with open(self.complete_filename_csv, "w") as f:
                    f.close()
            # TODO: Maybe instead of time process should be written the number of the processed material ...
            #  or should be added as a column
            with open(self.complete_filename_csv, "a") as f:
                f.write('step,input ' + self.heading + ',time process ' + self.heading + ',output ' +
                        self.heading + ',produced,failure ' + self.heading + ',MTTF ' + self.heading + ',MTTR '
                        + self.heading + '\n')
                f.close()

    def write_log_txt(self, text):
        with open(self.complete_filename_txt, "a") as f:
            f.write(text)
            f.close()

    def write_log_csv(self, data_list):
        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
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

        with open(self.complete_filename_csv, "a") as f:
            f.write(text)
            f.close()

    # TODO: split the "Moment" part of the time-step field of the csv file into a standalone field.
    def merge_logs(self, *args):
        # Initializing the merged_logs.csv file.
        try:
            os.remove(self.save_path + "\\merged_logs.csv")
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            # os.makedirs(self.path)
            with open(self.save_path + "\\merged_logs.csv", "w") as f:
                f.close()

        # Creating a list as a buffer to temporally save the data read from the CSVs files.
        df_list = list()
        # Appending the data in the list read from the CSVs files.
        for arg in args:
            df = pandas.read_csv(self.save_path + "\\" + arg)
            df_list.append(df)

        # Merging the first two dataframes.
        df1 = df_list[0]
        df2 = df_list[1]
        df_merge = pandas.merge(left=df1, right=df2, on='step', how="outer", sort=True)

        # Merging the remaining dataframes, if any.
        for element in range(len(df_list)):
            # Skipping the first two dataframes in the list, cause they have been merged few lines before.
            if element == 0 or element == 1:
                continue
            # Merging the remaining files.
            else:
                df_merge = pandas.merge(left=df_merge, right=df_list[element], on='step', how='outer', sort=True)

        # Handling missing data generated from machine breakdowns
        df_merge.fillna(method="ffill", inplace=True)

        # Saving the merged dataframe into a csv file.
        df_merge.to_csv(self.save_path + "\\merged_logs.csv")
