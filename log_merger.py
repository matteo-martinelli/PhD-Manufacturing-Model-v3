"""
LogMerger.py class:

the class responsibility is to take all the log output of the simulator and merge it into one unique csv file.
The merged file has to be consistent with time order.
"""


class LogMerger(object):

    def __init__(self, save_path):
        self.save_path = save_path

    def merge_logs(self, file_name_1, file_name_2, file_name3):
        try:
            with open(file_name_1, "r") as f:
                line = f.readline()
                head_1 = line
                f.close()

            with open(file_name_2, "r") as f:
                line = f.readline()
                head_2 = line
                f.close()

            with open(file_name3, "r") as f:
                line = f.readline()
                head_3 = line
                f.close()

            with open(self.save_path + "\\merged_logs.txt", "w") as f:
                f.write(head_1 + "," + head_2 + "," + head_3)
                f.close()

        except FileExistsError:
            print('The log file does not exists!')