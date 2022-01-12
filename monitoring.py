"""
Monitoring.py class:

Class containing the global variables for the model.
"""

import os
import xlwt
# from xlwt import Workbook
from openpyxl import Workbook


class DataLogger(object):
    def __init__(self, path, filename_txt, filename_xlsx):
        self.path = path

        self.filename_txt = filename_txt
        self.complete_filename_txt = self.path + "\\" + self.filename_txt

        self.filename_xlsx = filename_xlsx
        self.complete_filename_xlsx = self.path + "\\" + self.filename_xlsx

        self.initialize_log_file()
        self.initialize_excel_file()

    def write_log(self, text):
        with open(self.complete_filename_txt, "a") as f:
            f.write(text)
            f.close()

    def initialize_log_file(self):
        try:
            os.remove(self.complete_filename_txt)
        except FileNotFoundError:
            print("The log file has not been found in the directory, creating a new one.")
            os.makedirs(self.path)
            with open(self.complete_filename_txt, "w") as f:
                f.close()

    def initialize_excel_file(self):
        # Create the workbook
        wb = Workbook()
        # add_sheet is used to create sheet.
        sheet1 = wb.active
        sheet1.title = "Sheet 1"
        # Writing the heading
        sheet1['A1'] = "Timestep [step]"

        sheet1['B1'] = "input A [level]"
        sheet1['C1'] = "timeprocess A [step]"
        sheet1['D1'] = "output A [level]"
        sheet1['E1'] = "failure A [bool]"
        sheet1['F1'] = "MTTF A [step]"
        sheet1['G1'] = "MTTR A [step]"

        sheet1['H1'] = "input B [level]"
        sheet1['J1'] = "timeprocess B [step]"
        sheet1['K1'] = "output B [level]"
        sheet1['L1'] = "failure B [bool]"
        sheet1['M1'] = "MTTF B [step]"
        sheet1['N1'] = "MTTR B [step]"

        sheet1['O1'] = "input C [level]"
        sheet1['P1'] = "timeprocess C [step]"
        sheet1['Q1'] = "output C [level]"
        sheet1['R1'] = "failure C [bool]"
        sheet1['S1'] = "MTTF C [step]"
        sheet1['T1'] = "MTTR C [step]"

        wb.save(self.complete_filename_xlsx)
