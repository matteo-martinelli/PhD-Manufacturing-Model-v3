"""
machine_model.py -> Machine class:

Class describing a single machine behaviour.
Random breakdowns are embedded in the model.
Breakdown handling is also implemented during the input-output material handling.

The file have to be integrated with the env.

It takes as input an InputContainer and an OutputContainer object, to get and put raw materials from and in the
warehouses.

The log CSV files are encoded in the time steps in order to make every log unique within each time-step. So, time steps
are defined as "time_step.progressive_number". This was necessary in order to compute a join when merging the produced
log dataframes from the relative CSVs.

The log encoding is the following:
    -1: initial state
    -----------------------------------------------------------------
    x.1: input buffer empty, waiting one time step till is filled up
    x.2: input buffer filled up, continuing the process
    x.3: breakdown during input material handling
    x.4: repairing during input material handling
    x.5: finished the input material handling
    -----------------------------------------------------------------
    x.6: start to work on the part, required time to finish saved
    x.7: breakdown during the part processing
    x.8: repairing during the part processing
    x.9: finish to work on the part, required time to finish at zero
    -----------------------------------------------------------------
    x.10: output buffer full, waiting one time step till is emptied
    x.11: output buffer emptied, continuing with the process
    x.12: breakdown during output material handling
    x.13: repairing during output material handling
    x.14: finished the output material handling
"""

import random
import simpy
from monitoring import *
from global_variables import *


# TODO: think about turning private the appropriate attributes.
# TODO: test the class behaviour with the csv merged file:
#  - with longer simulations; -> DONE
#  - with breakdowns in the loop. -> Sync data appending with written logs to better debug the code.
#                                 -> Divide the working method into sub methods to better handle the code.
# MACHINE CLASS --------------------------------------------------------------------------------------------------------
class Machine(object):

    """
    A machine produces parts and gets broken every now and then.

    If it breaks, it requires a "repairman" and continues
    the production when is repaired. - DEACTIVATED IN MY IMPLEMENTATION.

    A machine has a "name" and a number of parts processed.
    """
    def __init__(self, env, name, mean_process_time, sigma_process_time, MTTF, repair_time, input_buffer,
                 output_buffer):
        self.env = env
        self.name = name    # Must be coded as "Machine" + identifying letter from A to Z

        # Process variables.
        self.parts_made = 0
        self.mean_process_time = mean_process_time
        self.sigma_process_time = sigma_process_time

        # Breakdowns variables.
        self.MTTF = MTTF
        self.break_mean = 1 / self.MTTF
        self.repair_time = repair_time
        self.broken = False

        self.input_buffer = input_buffer
        self.output_buffer = output_buffer

        # Simpy processes
        # Start "working" and "break_machine" processes for this machine.
        self.process = env.process(self.working())
        self.env.process(self._break_machine())
        self.logistic_breakdowns = True         # To exclude breakdowns during logistic operations, set to False.
        self.processing_breakdowns = True       # To exclude breakdowns during processing operations, set to False.
        # self.input_level_check = env.process(self._input_level_check())     # Process in parallel, WRONG
        # self.output_level_check = env.process(self._output_level_check())   # Process in parallel, WRONG

        # Logging objects - As a best practice, write before in the txt, console, then append data into the data list.
        self.log_path = GlobalVariables.LOG_PATH
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.csv_filename = self.name + " log.csv"
        self.data_logger = DataLogger(self.log_path, self.log_filename, self.csv_filename)
        self.data = list()

    # TODO: turn private
    # Function describing the machine process.
    def working(self):
        """
        Produces parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        When machine breaks, MTTR is computed from its statistics.
        """

        # TODO: should it be moved? It can be eliminated!
        # Creating the list containing the csv log files.
        # data = list()
        # Writing the -1 initial condition in the csv file.
        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
        self.data.append(['-1', self.input_buffer.level, '0', self.output_buffer.level, self.parts_made, self.broken,
                          self.MTTF, '0'])

        # TODO: check if there is a logging action everytime something happens.
        while True:
            # LOG THE INITIAL STATE ----------------------------------------------------------------------------------
            self._write_extended_log(self.env.now, '0', self.input_buffer.level, '0', self.output_buffer.level,
                                     self.parts_made, self.broken, self.MTTF, '0')

            # CHECK THE INPUT BUFFER LEVEL -----------------------------------------------------------------------------
            # Perform the output warehouse level checking: if empty, wait 1 time step.
            # If in the input buffer there is no raw material ...
            if self.input_buffer.level == 0:
                # ... and while the buffer is empty ...
                while self.input_buffer.level == 0:
                    # ... log the status ...
                    # Maybe this log is non necessary due to the initial state log... think about it
                    self._write_extended_log(self.env.now, '1', self.input_buffer.level, '0', self.output_buffer.level,
                                             self.parts_made, self.broken, self.MTTF, '0')
                    try:
                        # ... and wait one time step.
                        yield self.env.timeout(1)
                    except simpy.Interrupt:
                        pass
                # When the buffer is filled, log the status and continue.
                self._write_extended_log(self.env.now, '2', self.input_buffer.level, '0',
                                         self.output_buffer.level, self.parts_made, self.broken, self.MTTF, '0')

            # TODO: RICOMINCIA DA QUI. Aggiungi qui l'aggiornamento del buffer quando viene riempito. -> FATTO
            # TODO: Fai lo stesso per l'output buffer.

            # HANDLING INPUT MATERIAL ----------------------------------------------------------------------------------
            # Take the raw product from raw products warehouse. Wait the necessary step to retrieve the material.
            # The action is performed in a try-except block because the machine may break during the handling of the
            # material
            handled_in = 0
            start_handling = 0
            while handled_in:
                try:
                    # Handling the part
                    start_handling = self.env.now
                    # No handling logging - Maybe it should be added?
                    yield self.env.timeout(handled_in)
                    # handled_in set 0 to exit to the loop
                    handled_in = 0

                except simpy.Interrupt:
                    # If machine breakdowns are considered during logistic operations into the simulation...
                    if self.logistic_breakdowns:
                        # ... then simulate the process stop for the machine breakdown and relative time to repair
                        # wait...

                        # The machine broke.
                        self.broken = True
                        handled_in -= self.env.now - start_handling  # How much time left to handle the material?

                        self._write_extended_log(self.env.now, '3', self.input_buffer.level, '0',
                                                 self.output_buffer.level, self.parts_made, self.broken, '0',
                                                 self.repair_time)

                        yield self.env.timeout(self.repair_time)

                        # Machine repaired.
                        self.broken = False

                        self._write_extended_log(self.env.now, '4', self.input_buffer.level, '0',
                                                 self.output_buffer.level, self.parts_made, self.broken, self.MTTF, '0')
                    else:
                        # ... else, skip the time to repair wait and go ahead.
                        pass

            # TODO: move the logging of the finished operation into the try-block
            # Logging the event.
            self.input_buffer.get(1)  # Take the piece from the input buffer
            self.input_buffer.products_picked += 1  # Track the total products picked from the buffer

            self._write_extended_log(self.env.now, '5', self.input_buffer.level, '0', self.output_buffer.level,
                                     self.parts_made, self.broken, self.MTTF, '0')

            # PROCESSING THE MATERIAL ----------------------------------------------------------------------------------
            # Start making a new part
            time_per_part = self.mean_process_time
            done_in = time_per_part       # time_per_part() is the real stochastic function.
            start = 0
            while done_in:
                try:
                    # Working on the part
                    start = self.env.now

                    self._write_extended_log(self.env.now, '6', self.input_buffer.level, done_in,
                                             self.output_buffer.level, self.parts_made, self.broken, self.MTTF, '0')

                    yield self.env.timeout(done_in)
                    # Set 0 to exit to the loop
                    done_in = 0

                except simpy.Interrupt:
                    # If machine breakdowns are considered during machine operations into the simulation...
                    if self.processing_breakdowns:
                        # ... then simulate the process stop for the machine breakdown and relative time to repair
                        # wait..

                        # The machine broke.
                        self.broken = True
                        done_in -= self.env.now - start     # How much time left to finish the job?

                        self._write_extended_log(self.env.now, '7', self.input_buffer.level, done_in,
                                                 self.output_buffer.level, self.parts_made, self.broken, '0',
                                                 self.repair_time)

                        yield self.env.timeout(self.repair_time)

                        # Machine repaired.
                        self.broken = False

                        self._write_extended_log(self.env.now, '8', self.input_buffer.level, done_in,
                                                 self.output_buffer.level, self.parts_made, self.broken, self.MTTF, '0')
                    else:
                        # ... else, skip the time to repair wait and go ahead.
                        pass

            # Part is done
            prod_time = self.env.now
            self.parts_made += 1

            # TODO: should be added a log here. -> Complete the upgraded log method.

            self._write_extended_log(prod_time, '9', self.input_buffer.level, '0', self.output_buffer.level,
                                     self.parts_made, self.broken, self.MTTF, '0')

            # TODO: convert to work with _write_log potenziato
            """
            # Logging the event - prod
            # Print in the console
            print("{0}.y - mach: made 1 in {1}. Total pieces made: {2}.".format(
                str(prod_time), self.name, self.parts_made))
            # Print in the txt file
            self.data_logger.write_log_txt("{0}.y - mach: made 1 in {1}. Total pieces made: {2}.".format(
                str(prod_time), self.name, self.parts_made))
            """

            # CHECK THE OUTPUT BUFFER LEVEL ----------------------------------------------------------------------------
            # Perform the output warehouse level checking: if full, wait 1 time step.
            # self._output_level_check()

            # If in the output buffer there is full ...
            if self.output_buffer.level == self.output_buffer.capacity:
                # ... and while the buffer is still full ...
                while self.output_buffer.level == self.output_buffer.capacity:
                    # ... log the status ...
                    self._write_extended_log(self.env.now, '10', self.input_buffer.level, '0', self.output_buffer.level,
                                             self.parts_made, self.broken, self.MTTF, '0')

                    try:
                        # ... and wait one time step.
                        yield self.env.timeout(1)
                    except simpy.Interrupt:
                        pass
                # When the buffer is emptied, log the status and continue.
                self._write_extended_log(self.env.now, '11', self.input_buffer.level, '0',
                                         self.output_buffer.level, self.parts_made, self.broken, self.MTTF, '0')

            # HANDLING OUTPUT MATERIAL ---------------------------------------------------------------------------------
            handled_out = GlobalVariables.PUT_STD_DELAY
            start_handling = 0
            while handled_out:
                try:
                    # Handling the part
                    start_handling = self.env.now
                    # No handling logging - Maybe it should be added?
                    yield self.env.timeout(handled_out)
                    handled_out = 0  # Set 0 to exit to the loop

                except simpy.Interrupt:
                    # If machine breakdowns are considered during logistic operations into the simulation...
                    if self.logistic_breakdowns:
                        # ... then simulate the process stop for the machine breakdown and relative time to repair
                        # wait ...

                        # The machine broke.
                        self.broken = True
                        handled_out -= self.env.now - start_handling  # How much time left to handle the material?

                        self._write_extended_log(self.env.now, '12', self.input_buffer.level, '0',
                                                 self.output_buffer.level, self.parts_made, self.broken, '0',
                                                 self.repair_time)

                        yield self.env.timeout(self.repair_time)

                        # Machine repaired.
                        self.broken = False

                        self._write_extended_log(self.env.now, '13', self.input_buffer.level, '0',
                                                 self.output_buffer.level, self.parts_made, self.broken, self.MTTF, '0')
                    else:
                        # ... else, skip the time to repair wait and go ahead.
                        pass

            # Handling_out is done
            handled_out_time = self.env.now
            # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.output_buffer.put(1)                # Take the piece from the input buffer
            self.output_buffer.products_stored += 1  # Track the total products stored in the buffer

            self._write_extended_log(self.env.now, '14', self.input_buffer.level, '0', self.output_buffer.level,
                                     self.parts_made, self.broken, self.MTTF, '0')

            # Writing all the collected file into the csv.
            self.data_logger.write_log_csv(self.data)
            # Resetting the data collecting list.
            self.data = list()
            # Going at the next time-step
            try:
                yield self.env.timeout(1)
            except simpy.Interrupt:
                pass

    def _input_level_check(self):
        pass

    def _output_level_check(self):
        pass

    def _break_machine(self):
        """Break the machine every now and then."""
        random.seed(0)
        while True:
            time_to_failure = round(random.expovariate(self.break_mean))
            yield self.env.timeout(time_to_failure)
            if not self.broken:
                # Only breaks when machine is currently working and is not already broken.
                self.process.interrupt()

    # Signature = step, moment, input_level, done_in (time_process), output_level, parts_made (produced), broken, MTTF,
    # MTTR
    def _write_extended_log(self, step, moment, input_level, done_in, output_level, parts_made, broken, MTTF, MTTR):
        # TODO: Test in the _working method.
        # if statement ready-to-use but case never called in the working method.
        if moment == "0":
            text = "{0}.{1} - mach: state of {2} at step {0} moment {1}: input buffer {3}, output buffer {4}"
            # Print in the console
            print(text.format(step, moment, self.name, input_level, output_level))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, input_level, output_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        if moment == "1":
            text = "{0}.{1} - mach: the {2} input buffer level is {3}. Waiting 1 time step and re-check."
            # Print in the console
            print(text.format(step, moment, self.name, input_level))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, input_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        if moment == "2":
            text = "{0}.{1} - mach: the {2} input buffer has been filled up. The buffer level is {3}. Continuing with " \
                   "the process"
            # Print in the console
            print(text.format(step, moment, self.name, input_level))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, input_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "3":
            text = "\n{0}.{1} down - mach: {2} broke. Handling-in stopped. Machine will be repaired in {3}\n"
            # Print in the console
            print(text.format(step, moment, self.name, MTTR))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, MTTR))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "4":
            text = "\n{0}.{1} up - mach: {2} repaired. Handling-in restarted.\n"
            # Print in the console
            print(text.format(step, moment, self.name))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "5":
            text = "{0}.{1} - mach: input {2} level {3}; taken 1 from input {2}."
            # Print in the console
            print(text.format(step, moment, self.name, input_level))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, input_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "6":
            text = "{0}.{1} - mach: started 1 in {2}"
            # Print in the console
            print(text.format(step, moment, self.name))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "7":
            text = "\n{0}.{1} down - mach: {2} broke. {3} step for the job to be completed. Machine will be repaired " \
                   "in {4}\n"
            # Print in the console
            print(text.format(step, moment, self.name, done_in, MTTR))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, done_in, MTTR))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "8":
            text = "\n{0}.{1} up - mach: {2} repaired. Working restarted.\n"
            # Print in the console
            print(text.format(step, moment, self.name))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "9":
            text = "{0}.{1} - mach: made 1 in {2}. Total pieces made: {3}."
            # Print in the console
            print(text.format(step, moment, self.name, parts_made))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, parts_made))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        # TODO: Test in the _working method.
        # if statement ready-to-use but case never called in the working method.
        elif moment == "10":
            text = "{0}.{1} - out_full - mach: the {2} output buffer level is {3}. Waiting 1 time step and re-check."
            # Print in the console
            print(text.format(step, moment, self.name, output_level))
            # Print in the txt
            self.data_logger.write_log_txt(text.format(step, moment, self.name, output_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                             MTTF, MTTR])

        elif moment == "11":
            text = "{0}.{1} - mach: the {2} output buffer has been emptied. The buffer level is {3}. Continuing with " \
                   "the process"
            # Print in the console
            print(text.format(step, moment, self.name, input_level))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, input_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "12":
            text = "\n{0}.{1} down - mach: {2} broke. Handling-out stopped. Machine will be repaired in {3}\n"
            # Print in the console
            print(text.format(step, moment, self.name, MTTR))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, MTTR))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "13":
            text = "\n{0}.{1} up - mach: {2} repaired. Handling-out restarted.\n"
            # Print in the console
            print(text.format(step, moment, self.name))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

        elif moment == "14":
            text = "{0}.{1} - mach: output {2} level {3}; put 1 in output {2}."
            # Print in the console
            print(text.format(step, moment, self.name, output_level))
            # Print in the txt file
            self.data_logger.write_log_txt(text.format(step, moment, self.name, output_level))

            # csv_log = step + moment, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.data.append([str(step) + "." + str(moment), input_level, done_in, output_level, parts_made, broken,
                              MTTF, MTTR])

# MINOR FUNCTIONS ------------------------------------------------------------------------------------------------------
"""
def time_per_part():
    Return actual processing time for a concrete part.
    return random.normalvariate(PT_MEAN, PT_SIGMA)

def time_to_failure():
    Return time until next failure for a machine
    return random.expovariate(BREAK_MEAN)
"""
