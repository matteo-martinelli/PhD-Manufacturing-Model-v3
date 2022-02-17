"""
merge_logs.py file: MergeLogs class

the class responsibility is to enable the log capabilities for the instantiated model objects, and to save it into a csv
file. Because of the similarity, the logs are also saved into a plain text .txt file and printed on the console.

the second class responsibility is to take all the log output of the simulator and merge it into one unique csv file.
The merged file has to be consistent with time order.

The responsibility is achieved leveraging pandas, turning the log files into dataframes and then merging them performing
a full-outer-join.

"""

import os
import time
import pandas
import shutil
from global_variables import GlobalVariables


class MergeLogs(object):
    def __init__(self):
        pass

    # TODO: split the "Moment" part of the time-step field of the csv file into a standalone field.

    @staticmethod
    def merge_logs(input_path, output_path, output_name, *args):
        # Initializing the merged_logs.csv file.
        try:
            os.remove(output_path + "\\" + output_name)
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            with open(output_path + "\\" + output_name, "w") as f:
                f.close()

        # Creating a list as a buffer to temporally save the data read from the CSVs files.
        df_list = list()
        # Appending the data in the list read from the CSVs files.
        for arg in args:
            df = pandas.read_csv(input_path + "\\" + arg)
            df_list.append(df)

        # Merging the first two dataframes.
        df1 = df_list[0]
        df2 = df_list[1]
        df_merge = pandas.merge(left=df1, right=df2, on='step', how="outer", sort=True)

        # Merging the remaining dataframes, if any.
        for element in range(len(df_list)):
            # Skipping the first two dataframes in the list, because they have been merged few lines before.
            if element == 0 or element == 1:
                continue
            # Merging the remaining files.
            else:
                df_merge = pandas.merge(left=df_merge, right=df_list[element], on='step', how='outer', sort=True)

        # Handling missing data generated from machine breakdowns
        df_merge.fillna(method="ffill", inplace=True)
        # Converting all the data into int comprised Trues and Falses
        df_merge.iloc[:, 1:] = df_merge.iloc[:, 1:].astype('Int64')
        # Saving the merged dataframe into a csv file.
        df_merge.to_csv(output_path + "\\" + output_name, index=False)


# TODO: implement if name = main to do proper tests easily.
# File Main entry point.
if __name__ == "__main__":
    raw_log_path = GlobalVariables.LOG_PATH
    merged_log_path = "C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\Phd-Manufacturing-Model-v3\\" \
                      "logs\\merged_logs"

    # Merging each machine log with the respect expected products log.
    log_merger = MergeLogs()
    log_merger.merge_logs(raw_log_path, merged_log_path, "merged_Mach_A.csv", "Machine A log.csv",
                          "Machine A exp_prod_flag.csv")
    log_merger.merge_logs(raw_log_path, merged_log_path, "merged_Mach_B.csv", "Machine B log.csv",
                          "Machine B exp_prod_flag.csv")
    log_merger.merge_logs(raw_log_path, merged_log_path, "merged_Mach_C.csv", "Machine C log.csv",
                          "Machine C exp_prod_flag.csv")

    # Merging into 1.
    log_merger.merge_logs(merged_log_path, merged_log_path, "merged_logs.csv", "merged_Mach_A.csv", "merged_Mach_B.csv",
                          "merged_Mach_C.csv")

    # Copying the merged logs file to the Colab folder.
    # shutil.copy('C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\Phd-Manufacturing-Model-v3\\logs\\'
    #            'merged_logs.csv', 'C:\\Users\\wmatt\\Desktop\\GDrive\\Colab Notebooks\\My Notebooks\\PhD Notebooks\\'
    #            'Colab-Manufacturing-Model-Learning\\Causal-Manufacturing-Learning-v1\\dataset')
