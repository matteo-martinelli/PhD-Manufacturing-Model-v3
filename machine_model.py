"""
Machine_A.py class:

Class describing a single machine behaviour.
Random breakdowns are embedded in the model.
The file have to be integrated with the env.

It takes as input also the LogisticModel, to get and put raw materials from warehouses.
"""

import random
import simpy
from monitoring import *


# TODO: Add a -1 time logging mapping the overall initial state of the system.
# MACHINE CLASS --------------------------------------------------------------------------------------------------------
class Machine(object):
    """A machine produces parts and gets broken every now and then.

    If it breaks, it requires a "repairman" and continues
    the production when is repaired.

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
        self.env.process(self.break_machine())  # To exclude breakdowns, comment this line.

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.csv_filename = self.name + "_log.txt"
        self.data_logger = DataLogger(self.log_path, self.log_filename, self.csv_filename)
        self.data_logger.write_log_txt("### DATA LOG FROM PROCESS MACHINE FILE ###\n")

    # TODO: turn private
    #  Function describing the machine process.
    def working(self):
        """Produces parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        When machine breaks, MTTR is computed from its statistics.
        """

        # TODO: should it be moved?
        # Writing the -1 situation in the csv file.
        data = list()
        # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
        data.append(['-1', self.input_buffer.level, '0', self.output_buffer.level, self.parts_made, self.broken,
                     self.MTTF, '0'])

        while True:
            # Perform the output warehouse level checking: if empty, wait 1 time step.
            self.input_level_check()

            # Warehouse tracking (made before the piece to be took/placed).
            # Logging the event.
            print("{0}.1 - mach: input {1} level {2}; get 1 from input {1}."
                  .format(str(self.env.now), self.name, str(self.input_buffer.level)))
            # Writing into the log file - prod - del
            self.data_logger.write_log_txt("{0}.1 - mach: input {1} level {2}; get 1 from input {1}.\n"
                                           .format(str(self.env.now), self.name, str(self.input_buffer.level)))

            # Take the raw product from raw products warehouse
            self.input_buffer.get(1)

            # Logging the event.
            print("{0}.2 - mach: input {1} level {2}; taken 1 from input {1}. "
                  .format(str(self.env.now), self.name, str(self.input_buffer.level)))
            # Writing into the log file - prod
            self.data_logger.write_log_txt("{0}.2 - mach: input {1} level {2}; taken 1 from input {1}.\n"
                                           .format(str(self.env.now), self.name, str(self.input_buffer.level)))

            # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            data.append([self.env.now, self.input_buffer.level, '0', self.output_buffer.level, self.parts_made,
                         self.broken, self.MTTF, '0'])

            # Start making a new part
            time_per_part = self.mean_process_time
            done_in = time_per_part       # time_per_part() is the real stochastic function.

            # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            data.append([self.env.now, self.input_buffer.level, done_in, self.output_buffer.level, self.parts_made,
                         self.broken, self.MTTF, '0'])

            while done_in:
                try:
                    # Working on the part
                    start = self.env.now
                    # Logging the event.
                    print("{0}.3 - mach: started 1 in {1}\n".format(str(start), self.name))
                    # Writing into the log file - prod
                    self.data_logger.write_log_txt("{0}.3 - mach: started 1 in {1}\n".format(str(start), self.name))

                    yield self.env.timeout(done_in)
                    done_in = 0     # Set 0 to exit to the loop

                except simpy.Interrupt:
                    # The machine broke.
                    self.broken = True
                    done_in -= self.env.now - start     # How much time left to finish the job?

                    # Logging the event.
                    print("{0}.3 down - mach: {1} broke. {2} step for the job to be completed. "
                          "Machine will be repaired in {0}\n".format(str(self.env.now), self.name, str(done_in),
                                                                     str(self.repair_time)))
                    # Writing into the log file - prod
                    self.data_logger.write_log_txt("{0}.3 down - mach: {1} broke. {2} step for the job to be completed."
                                                   .format(str(self.env.now), self.name, str(done_in)))
                    self.data_logger.write_log_txt(" Machine will be repaired in {0}\n".format(str(self.repair_time)))

                    # csv_log = step, input_level, time_process, output_level, produced, produced, failure, MTTF, MTTR
                    data.append([self.env.now, self.input_buffer.level, done_in, self.output_buffer.level,
                                 self.parts_made, self.broken, self.MTTF, self.repair_time])

                    yield self.env.timeout(self.repair_time)

                    # Machine repaired.
                    self.broken = False

                    # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
                    data.append([self.env.now, self.input_buffer.level, done_in, self.output_buffer.level,
                                 self.parts_made, self.broken, self.MTTF, '0'])

                    # Logging the event. The machine is repaired.
                    print("{0}.3 up - mach: {1} repaired. Working restarted.".format(str(self.env.now), self.name))
                    # Writing into the log file - prod
                    self.data_logger.write_log_txt("{0}.3 up - mach: {1} repaired. Working restarted.\n"
                                                   .format(str(self.env.now), self.name))

            # Part is done
            prod_time = self.env.now
            self.parts_made += 1

            # Logging the event - prod
            print("{0}.4 - mach: made 1 in {1}. Total pieces made: {2}.".format(str(prod_time), self.name, self.parts_made))
            # Writing into the log file - prod
            self.data_logger.write_log_txt("{0}.4 - mach: made 1 in {1}. Total pieces made: {2}.\n"
                                           .format(str(prod_time), self.name, self.parts_made))

            # Perform the output warehouse level checking: if full, wait 1 time step.
            self.output_level_check()

            # Logging the event - prod
            print("{0}.6 - mach: output {1} level {2}; put 1 in output {1}.".format(str(self.env.now), self.name,
                                                                                    str(self.output_buffer.level)))
            # Writing into the log file - prod
            self.data_logger.write_log_txt("{0}.6 - mach: output {1} level {2}; put 1 in output {1}.\n"
                                           .format(str(self.env.now), self.name, str(self.output_buffer.level)))

            # Put the finished product into the finished warehouse
            self.output_buffer.put(1)

            # csv_log = step, input_level, time_process, output_level, produced, failure, MTTF, MTTR
            data.append([self.env.now, self.input_buffer.level, done_in, self.output_buffer.level,
                         self.parts_made, self.broken, self.MTTF, '0'])

            # Logging into the file - prod
            print("{0}.7 - mach: output {1} level {2}; put 1 in output {1}.".format(str(self.env.now), self.name,
                                                                                    str(self.output_buffer.level)))
            # Writing into the log file - prod
            self.data_logger.write_log_txt("{0}.7 - mach: output {1} level {2}; put 1 in output {1}.\n"
                                           .format(str(self.env.now), self.name, str(self.output_buffer.level)))

            # Writing all the collected file into the csv.
            self.data_logger.write_log_csv(data)
            # Resetting the data collecting list.
            data = list()

    # TODO: turn private
    def break_machine(self):
        """Break the machine every now and then."""
        while True:
            time_to_failure = round(random.expovariate(self.break_mean))
            yield self.env.timeout(time_to_failure)
            if not self.broken:
                # Only breaks when machine is currently working.
                self.process.interrupt()

    # TODO: turn private
    def input_level_check(self):
        while self.input_buffer.level == 0:
            print("{0}.in_empty - mach: the {1} input buffer level is {2}. Waiting 1 time step and re-check."
                  .format(str(self.env.now), self.name, str(self.input_buffer.level)))
            self.data_logger.write_log_txt("{0}.in_empty - mach: the {1} input buffer level is {2}. Waiting 1 time "
                                           "step and re-check.\n".format(str(self.env.now), self.name,
                                                                         str(self.input_buffer.level)))
            yield self.env.timeout(1)

    # TODO: turn private
    def output_level_check(self):
        while self.output_buffer.level == self.output_buffer.capacity:
            print("{0}.out_full - mach: the {1} output buffer level is {2}. Waiting 1 time step and re-check."
                  .format(str(self.env.now), self.name, str(self.output_buffer.level)))
            self.data_logger.write_log_txt("{0}.out_full - mach: the {1} output buffer level is {2}. Waiting 1 time"
                                           " step and re-check.\n"
                                           .format(str(self.env.now), self.name, str(self.output_buffer.level)))
            yield self.env.timeout(1)


"""
# REPAIRMAN FUNCTION ---------------------------------------------------------------------------------------------------
def other_jobs(env, repairman, other_jobs_time):
    # Those are repairman's other not important jobs.
    while True:
        # Start a new job
        done_in = other_jobs_time
        while done_in:
            # Retry the job until is done
            # Its priority is lower than that of machine repairs
            with repairman.request(priority=2) as req:
                yield req
                try:
                    start = env.now
                    yield env.timeout(done_in)
                    done_in = 0
                except simpy.Interrupt:
                    done_in -= env.now - start
"""

# MINOR FUNCTIONS ------------------------------------------------------------------------------------------------------
"""
def time_per_part():
    Return actual processing time for a concrete part.
    return random.normalvariate(PT_MEAN, PT_SIGMA)

def time_to_failure():
    Return time until next failure for a machine
    return random.expovariate(BREAK_MEAN)
"""
