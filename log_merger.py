"""
LogMerger.py class:

the class responsibility is to take all the log output of the simulator and merge it into one unique csv file.
The merged file has to be consistent with time order.
"""

import os


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
                    print("there1")
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


