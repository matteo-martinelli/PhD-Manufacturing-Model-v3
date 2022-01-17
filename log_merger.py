"""
LogMerger.py class:

the class responsibility is to take all the log output of the simulator and merge it into one unique csv file.
The merged file has to be consistent with time order.
"""

import os
from global_variables import *


class LogMerger(object):

    def __init__(self, save_path):
        self.save_path = save_path

    def merge_logs(self, *args):
        # Initializing the merged_logs.txt file.
        try:
            os.remove(self.save_path + "\\merged_logs.txt")
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            # os.makedirs(self.path)
            with open(self.save_path + "\\merged_logs.txt", "w") as f:
                f.close()

        # Populating the merged_logs.txt file with the merged heading.
        for arg in args:
            try:
                # Read the head in the first passed file.
                with open(self.save_path + "\\" + arg, "r") as input_file:
                    line = input_file.readline()
                    input_file.close()

                # Write the head in the merged file.
                # If is the first file, add the step column at the file beginning.
                if args.index(arg) == 0:
                    with open(self.save_path + "\\merged_logs.txt", "a") as output_file:
                        output_file.write(line[:-1])
                        output_file.close()

                # If is not the first file, do not add the first column at the file.
                else:
                    with open(self.save_path + "\\merged_logs.txt", "a") as output_file:
                        output_file.write(line[4:-1])
                        output_file.close()

                print("Heading {0} merged.".format(str(args.index(arg) + 1)))
            except FileNotFoundError:
                print('The input log file does not exists!')
            except FileExistsError:
                print('The output log file does not exists!')

        print("Headings merged.")

        # Populating the time step column in the txt file. Every simulation time step will be displayed.
        with open(self.save_path + "\\merged_logs.txt", "a") as output_file:
            output_file.write("\n")
            output_file.write("-1, \n")
            for i in range(GlobalVariables.SIM_TIME):
                output_file.write(str(i) + ", \n")
            output_file.close()

        # Populating the merged_logs.txt file with the merged heading.
        sel = 0
        for arg in args:
            # Open the machine log file.
            with open(self.save_path + "\\" + arg, "r") as input_file:
                # The selector will be multiplied with the column size counter
                # TODO: implement the column size counter in the DataLogger class.
                sel += 1
                while True:
                    # Read the i-th line of the machine log.
                    input_line = input_file.read().split(", ")
                    input_step = input_line[0]
                    # Skip the first line, the heading one.
                    if input_step == "step":
                        print("Ignoring the head. Skipping to the next line")
                        continue
                    else:
                        # Open the merged_log.txt file.
                        with open(self.save_path + "\\merged_logs.txt", "a+") as output_file:
                            while True:
                                # Splitting the read line into the output file.
                                output_line = output_file.readline().split(", ")
                                output_step = output_line[0]
                                if input_step != output_step:
                                    continue
                                elif output_step == "1":
                                    for element in range(len(input_line)):
                                        if element == 0:
                                            continue
                                        else:
                                            output_file.write(input_line[element] + ", ")
                                break
                            output_file.close()
                        break
                input_file.close()
