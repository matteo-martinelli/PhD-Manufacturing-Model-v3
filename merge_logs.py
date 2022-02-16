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
import time

import pandas
import shutil
from global_variables import GlobalVariables


# TODO: check merging data and convert every float into int.
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

        # print("1: ", df_merge.head(5))
        # Handling missing data generated from machine breakdowns
        df_merge.fillna(method="ffill", inplace=True)
        # print("2: ", df_merge.head(5))
        # Converting all the data into int comprised Trues and Falses
        df_merge.iloc[:, 1:] = df_merge.iloc[:, 1:].astype('int')
        # print("3: ", df_merge.head(5))
        # Saving the merged dataframe into a csv file.
        df_merge.to_csv(output_path + "\\" + output_name, index=False)

    @staticmethod
    def reformat_step(path):
        dataframe = pandas.read_csv(path)
        # dataframe.iloc[:, :0] = dataframe.iloc[:, :0].astype('string').replace(".", ":")
        dataframe.iloc[:, 1:] = dataframe.iloc[:, 1:].astype('int')
        dataframe.to_csv(path, index=False)


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

    data_frame = pandas.read_csv(merged_log_path + '\\merged_logs.csv')
    print(data_frame.dtypes)
    data_frame.iloc[:, 1:] = data_frame.iloc[:, 1:].astype('Int64') # WORKS.
    print(data_frame.dtypes)
    print(data_frame.head(5))
    # time.sleep(1)

    # log_merger.reformat_step(merged_log_path)

    # global_log_merger.reformat_step('C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\'
    #                                 'Phd-Manufacturing-Model-v3\\logs\\merged_logs\\merged_logs.csv')
    # Copying the merged logs file to the Colab folder.
    # shutil.copy('C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\Phd-Manufacturing-Model-v3\\logs\\'
    #            'merged_logs.csv', 'C:\\Users\\wmatt\\Desktop\\GDrive\\Colab Notebooks\\My Notebooks\\PhD Notebooks\\'
    #            'Colab-Manufacturing-Model-Learning\\Causal-Manufacturing-Learning-v1\\dataset')
