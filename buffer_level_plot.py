"""
buffer_level_plot.py:

This file has the responsibility to plot buffer levels at the end of the simulation.
"""

import matplotlib.pyplot as plt
import pandas

MERGED_LOG_PATH = 'logs\\2022.02.18-11.38-log\\merged_logs\\merged_logs.csv'

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

    print(data_frame.columns)
    print(data_frame)

    # Dropping unnecessary columns
    for col in data_frame.columns:
        if 'input' not in col and 'output' not in col and 'step' not in col:
            data_frame.drop(col, axis=1, inplace=True)

    print(data_frame.columns)

    plt.plot(data_frame['step'], data_frame['input Machine A'])
    plt.show()
