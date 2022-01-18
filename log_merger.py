"""
LogMerger.py class:

the class responsibility is to take all the log output of the simulator and merge it into one unique csv file.
The merged file has to be consistent with time order.
"""

import os
import pandas
from global_variables import *


class LogMerger(object):

    def __init__(self, save_path):
        self.save_path = save_path

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

        # Saving the merged dataframe into a csv file.
        df_merge.to_csv(self.save_path + "\\merged_logs.csv")
