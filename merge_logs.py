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
import data_logger


# TODO: check better hereditary of the class because is made very very badly.
class MergeLogs(data_logger.DataLogger):
    def __init__(self, path):
        super().__init__(path)

        # self.filename_txt = filename_txt
        # self.complete_filename_txt = self.path + "\\" + self.filename_txt

        # self.filename_csv = filename_csv
        # self.heading = self.filename_csv.split("log.")[0].strip()
        # self.complete_filename_csv = self.path + "\\" + self.filename_csv

    # TODO: split the "Moment" part of the time-step field of the csv file into a standalone field.
    def merge_logs(self, *args):
        # Initializing the merged_logs.csv file.
        try:
            os.remove(self.path + "\\merged_logs.csv")
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            # os.makedirs(self.path)
            with open(self.path + "\\merged_logs.csv", "w") as f:
                f.close()

        # Creating a list as a buffer to temporally save the data read from the CSVs files.
        df_list = list()
        # Appending the data in the list read from the CSVs files.
        for arg in args:
            df = pandas.read_csv(self.path + "\\" + arg)
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
        df_merge.to_csv(self.path + "\\merged_logs.csv")
