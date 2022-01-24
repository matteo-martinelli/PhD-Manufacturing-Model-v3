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

The log encoding is thefollowing:
    -1: initial state
    x.1: breakdown during input material handling
    x.2: repairing during input material handling
    x.3: finished the input material handling
    x.4: start to work on the part, required time to finish saved
    x.5: breakdown during the part processing
    x.6: repairing during the part processing
    x.7: breakdown during output material handling
    x.8: repairing during output material handling
    x.9: finished the output material handling
"""

import random
import simpy
from monitoring import *
from global_variables import *


# TODO: think about turning private the appropriate attributes.
# TODO: test the class behaviour with the csv merged file:
#  - with longer simulations;
#  - with breakdowns in the loop.
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

        # Start "working" and "break_machine" processes for this machine.
        self.process = env.process(self.working())
        # self.env.process(self._break_machine())  # To exclude breakdowns, comment this line.

        # Logging objects - As a best practice, write before in the txt, console, then append data into the data list.
        self.log_path = GlobalVariables.LOG_PATH
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.csv_filename = self.name + " log.csv"
        self.data_logger = DataLogger(self.log_path, self.log_filename, self.csv_filename)

    # TODO: turn private
    # Function describing the machine process.
    def working(self):
        """
        Produces parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        When machine breaks, MTTR is computed from its statistics.
        """

        # TODO: should it be moved?
        # Creating the list containing the csv log files.
        data = list()
        # Writing the -1 initial condition in the csv file.
        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
        data.append(['-1', self.input_buffer.level, '0', self.output_buffer.level, self.parts_made, self.broken,
                     self.MTTF, '0'])

        # TODO: check if there is a logging action everytime something happens.
        while True:
            # CHECK THE INPUT BUFFER LEVEL -----------------------------------------------------------------------------
            # Perform the output warehouse level checking: if empty, wait 1 time step.
            self._input_level_check()

            # Warehouse tracking (made before the piece to be took/placed).
            # Logging the event - prod - del
            self._write_log("{0}.1 - mach: input {1} level {2}; get 1 from input {1}.", str(self.env.now), self.name,
                            str(self.input_buffer.level))

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
                    # The machine broke.
                    self.broken = True
                    handled_in -= self.env.now - start_handling  # How much time left to handle the material?

                    # Writing into the log file - prod
                    self._write_log("\n{0}.3 down - mach: {1} broke. Handling-in stopped. Machine will be repaired in "
                                    "{2}\n", str(self.env.now), self.name, str(self.repair_time))

                    # csv_log = step, input_level, time_process, output_level, produced, produced, failure, MTTF, MTTR
                    data.append([str(self.env.now) + ".1", self.input_buffer.level, '0', self.output_buffer.level,
                                 self.parts_made, self.broken, '0', self.repair_time])

                    yield self.env.timeout(self.repair_time)

                    # Machine repaired.
                    self.broken = False

                    # Logging the event. The machine is repaired.
                    self._write_log("\n{0}.3 up - mach: {1} repaired. Handling-in restarted.\n",
                                    str(self.env.now), self.name)

                    # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
                    data.append([str(self.env.now) + ".2", self.input_buffer.level, '0', self.output_buffer.level,
                                 self.parts_made, self.broken, self.MTTF, '0'])

            # TODO: move the logging of the finished operation into the try-block
            # Logging the event.
            self.input_buffer.get(1)                # Take the piece from the input buffer
            self.input_buffer.products_picked += 1  # Track the total products picked from the buffer

            self._write_log("{0}.2 - mach: input {1} level {2}; taken 1 from input {1}.", str(self.env.now), self.name,
                            str(self.input_buffer.level))

            # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            data.append([str(self.env.now) + ".3", self.input_buffer.level, '0', self.output_buffer.level,
                         self.parts_made, self.broken, self.MTTF, '0'])

            # PROCESSING THE MATERIAL ----------------------------------------------------------------------------------
            # Start making a new part
            time_per_part = self.mean_process_time
            done_in = time_per_part       # time_per_part() is the real stochastic function.
            start = 0
            while done_in:
                try:
                    # Working on the part
                    start = self.env.now

                    # Logging the event.
                    self._write_log("{0}.3 - mach: started 1 in {1}", str(start), self.name)

                    # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
                    data.append(
                        [str(self.env.now) + ".4", self.input_buffer.level, done_in, self.output_buffer.level,
                         self.parts_made, self.broken, self.MTTF, '0'])

                    yield self.env.timeout(done_in)
                    # Set 0 to exit to the loop
                    done_in = 0

                except simpy.Interrupt:
                    # The machine broke.
                    self.broken = True
                    done_in -= self.env.now - start     # How much time left to finish the job?

                    # Writing into the log file - prod
                    self._write_log("\n{0}.4 down - mach: {1} broke. {2} step for the job to be completed. "
                                    "Machine will be repaired in {3}\n", str(self.env.now), self.name, str(done_in),
                                    str(self.repair_time))

                    # csv_log = step, input_level, time_process, output_level, produced, produced, failure, MTTF, MTTR
                    data.append([str(self.env.now) + ".5", self.input_buffer.level, done_in, self.output_buffer.level,
                                 self.parts_made, self.broken, '0', self.repair_time])

                    yield self.env.timeout(self.repair_time)

                    # Machine repaired.
                    self.broken = False

                    # Logging the event. The machine is repaired.
                    self._write_log("\n{0}.3 up - mach: {1} repaired. Working restarted.\n",
                                    str(self.env.now), self.name)

                    # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
                    data.append([str(self.env.now) + ".6", self.input_buffer.level, done_in, self.output_buffer.level,
                                 self.parts_made, self.broken, self.MTTF, '0'])

            # Part is done
            prod_time = self.env.now
            self.parts_made += 1

            # Logging the event - prod
            self._write_log("{0}.4 - mach: made 1 in {1}. Total pieces made: {2}.", str(prod_time), self.name,
                            self.parts_made)

            # CHECK THE OUTPUT BUFFER LEVEL ----------------------------------------------------------------------------
            # Perform the output warehouse level checking: if full, wait 1 time step.
            self._output_level_check()

            # Logging the event - prod
            self._write_log("{0}.6 - mach: output {1} level {2}; put 1 in output {1}.", str(self.env.now), self.name,
                            str(self.output_buffer.level))

            # Writing into the log file - prod
            self.data_logger.write_log_txt("{0}.6 - mach: output {1} level {2}; put 1 in output {1}.\n"
                                           .format(str(self.env.now), self.name, str(self.output_buffer.level)))

            # HANDLING OUTPUT MATERIAL ---------------------------------------------------------------------------------
            handled_out = GlobalVariables.PUT_STD_DELAY
            start_handling = 0
            while handled_out:
                try:
                    # Handling the part
                    start_handling = self.env.now
                    # No handling logging - Maybe it should be added?
                    yield self.env.timeout(handled_out)
                    # TODO: verify that the piece is effectively put.
                    # self.output_buffer.put(1)
                    handled_out = 0  # Set 0 to exit to the loop

                except simpy.Interrupt:
                    # The machine broke.
                    self.broken = True
                    handled_out -= self.env.now - start_handling  # How much time left to handle the material?

                    # Writing into the log file - prod
                    self._write_log("\n{0}.3 down - mach: {1} broke. Handling-out stopped. Machine will be repaired in "
                                    "{2}\n", str(self.env.now), self.name, str(self.repair_time))

                    # csv_log = step, input_level, time_process, output_level, produced, produced, failure, MTTF, MTTR
                    data.append([str(self.env.now) + ".7", self.input_buffer.level, '0', self.output_buffer.level,
                                 self.parts_made, self.broken, '0', self.repair_time])

                    yield self.env.timeout(self.repair_time)

                    # Machine repaired.
                    self.broken = False

                    # Logging the event. The machine is repaired.
                    self._write_log("\n{0}.3 up - mach: {1} repaired. Handling-out restarted.\n",
                                    str(self.env.now), self.name)

                    # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
                    data.append([str(self.env.now) + ".8", self.input_buffer.level, '0', self.output_buffer.level,
                                 self.parts_made, self.broken, self.MTTF, '0'])

            # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            self.output_buffer.put(1)                # Take the piece from the input buffer
            self.output_buffer.products_stored += 1  # Track the total products stored in the buffer

            data.append([str(self.env.now) + ".9", self.input_buffer.level, done_in, self.output_buffer.level,
                         self.parts_made, self.broken, self.MTTF, '0'])

            # TODO: move the logging of the finished operation into the try-block - NOPE the log has to be out instead.
            # Logging into the file - prod
            self._write_log("{0}.7 - mach: output {1} level {2}; put 1 in output {1}.", str(self.env.now), self.name,
                            str(self.output_buffer.level))

            # Writing all the collected file into the csv.
            self.data_logger.write_log_csv(data)
            # Resetting the data collecting list.
            data = list()

    def _break_machine(self):
        """Break the machine every now and then."""
        while True:
            time_to_failure = round(random.expovariate(self.break_mean))
            yield self.env.timeout(time_to_failure)
            if not self.broken:
                # Only breaks when machine is currently working and is not already broken.
                self.process.interrupt()

    def _input_level_check(self):
        # If in the input buffer there is no raw material ...
        while self.input_buffer.level == 0:
            self._write_log("{0}.in_empty - mach: the {1} input buffer level is {2}. Waiting 1 time step and re-check.",
                            str(self.env.now), self.name, str(self.input_buffer.level))

            yield self.env.timeout(1)

    def _output_level_check(self):
        # If in the output buffer there is not enough space to place 1 piece ...
        while self.output_buffer.level == self.output_buffer.capacity:
            self._write_log("{0}.out_full - mach: the {1} output buffer level is {2}. Waiting 1 time step and re-check.",
                            str(self.env.now), self.name, str(self.output_buffer.level))

            yield self.env.timeout(1)

    def _write_log(self, text, *data):
        # Writing into console
        print(str(text).format(*data))
        # Writing into the txt
        self.data_logger.write_log_txt(str(text + "\n").format(*data))


# MINOR FUNCTIONS ------------------------------------------------------------------------------------------------------
"""
def time_per_part():
    Return actual processing time for a concrete part.
    return random.normalvariate(PT_MEAN, PT_SIGMA)

def time_to_failure():
    Return time until next failure for a machine
    return random.expovariate(BREAK_MEAN)
"""
