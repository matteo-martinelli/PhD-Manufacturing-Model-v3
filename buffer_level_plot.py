"""
buffer_level_plot.py:

This file has the responsibility to plot buffer levels at the end of the simulation.
"""

import matplotlib.pyplot as plt
from matplotlib import ticker
import pandas

MERGED_LOG_PATH = 'logs\\2022.03.14-11.54-log\\merged_logs\\merged_logs.csv'

if __name__ == "__main__":
    # Getting the output csv as a data_frame
    data_frame = pandas.read_csv(MERGED_LOG_PATH)

    # Splitting the "step" column into "step" and "moment" in 5 steps:
    # 1. Saving the column list and adding the future "moment" column in the right position
    columns_list = data_frame.columns
    columns_list = columns_list.insert(1, 'moment')
    # 2. Converting the step col into string type
    data_frame["step_str"] = data_frame["step"].astype(str)
    # 3. Using str.split to split the col at the "."
    # data_frame[["step", "moment"]] = data_frame.step_str.str.split('.', expand=True)
    data_frame[["step", "moment"]] = data_frame['step_str'].str.split('.', expand=True)
    # 4. Dropping the temp col
    data_frame.drop(columns=["step_str"], axis=1, inplace=True)
    # 5. Reordering the result
    data_frame = data_frame[columns_list]

    # Dropping unnecessary columns
    for col in data_frame.columns:
        if 'input' not in col and 'output' not in col and 'step' not in col and 'failure' not in col:
            data_frame.drop(col, axis=1, inplace=True)

    print(data_frame)
    print(data_frame.columns)
    data_frame_rows = data_frame.shape[0]

    """
    # Counting rows where there is no breakdowns for A and B and C. 5000 lines needs to be collected to print an example
    # graph
    count = 0
    row = 0

    for row in range(data_frame_rows):
        print('running')
        # At the first row, just continue ...
        if row == 0:
            continue
        # At the other rows, check if there are no breakdowns.
        if (data_frame.iloc[row, 3] == 0) and (data_frame.iloc[row, 6] == 0):
            # If no breakdowns, count 1
            count += 1

            # If total lines counted are 5000, then save the dataframe till that line and break the cycle.
            if count >= 5000:
                row = int(data_frame.iloc[count, 0])
                # row = row.astype(int)
                print(type(row))
                break
        # If there is a breakdown, set the count to 0 and restart looking for 400
        else:
            count = 0

    print('count: ', count)

    no_stops_df = data_frame.iloc[:row, :]
    x_no_stops = no_stops_df['step']
    yA_no_stops = no_stops_df['input Machine A']
    yB_no_stops = no_stops_df['input Machine B']
    plt.plot(x_no_stops, yA_no_stops)
    plt.plot(x_no_stops, yB_no_stops)
    plt.xticks(x_no_stops[::180],  rotation='vertical')
    # plt.plot(no_stops_df['step'], no_stops_df['output Machine C'])
    plt.show()
"""
    # Counting rows where there is a breakdowns for A. 5000 lines needs to be collected to print an example graph
    count = 0
    target_row = 0

    print((data_frame.iloc[0:1, 3:4] == 0).bool() and (data_frame.iloc[0:1, 6:7] == 0).bool())
"""
    for row in range(data_frame_rows):
        print('running')
        # At the first row, just continue ...
        if row == 0:
            continue
        # At the other rows, check if there is an A breakdown.
        if (data_frame.iloc[row-1:row, 3:4] == 1).bool():
            # If A breaks, count 1
            count += 1
            print(data_frame.iloc[row-1:row, 3:4])

            # If total lines counted are 5000, then save the dataframe till that line and break the cycle.
            if count >= 5000:
                target_row = int(data_frame.iloc[count, 0])
                # row = row.astype(int)
                print(type(target_row))
                break
            # If there is a breakdown, set the count to 0 and restart looking for 400
        else:
            count = 0

    print('count: ', count)
    print('row', target_row)

    no_stops_df = data_frame.iloc[:target_row, :]
    x_no_stops = no_stops_df['step']
    yA_no_stops = no_stops_df['input Machine A']
    yB_no_stops = no_stops_df['input Machine B']
    plt.plot(x_no_stops, yA_no_stops)
    plt.plot(x_no_stops, yB_no_stops)
    plt.xticks(x_no_stops[::180], rotation='vertical')
    # plt.plot(no_stops_df['step'], no_stops_df['output Machine C'])
    plt.show()
"""
