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
        self.name = name

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
        # self.env.process(self.break_machine())  # To exclude breakdowns, comment this line.

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.excel_filename = GlobalVariables.EXCEL_FILENAME
        self.data_logger = DataLogger(self.log_path, self.log_filename, self.excel_filename)
        self.data_logger.write_log("### DATA LOG FROM PROCESS MACHINE FILE ###\n")

    #  Function describing the machine process.
    def working(self):
        """Produces parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        When machine breaks, MTTR is computed from its statistics.
        """
        while True:
            # Perform the output warehouse level checking: if empty, wait 1 time step.
            while self.input_buffer.level == 0:
                print(str(self.env.now) + ": the " + self.name + " input buffer level is " +
                      str(self.input_buffer.level) + ". Waiting 1 time step and re-check.")
                self.data_logger.write_log(str(self.env.now) + ": the " + self.name + " input buffer level is " +
                                           str(self.input_buffer.level) + ". Waiting 1 time step and re-check.\n")
                yield self.env.timeout(1)

            # Warehouse tracking (made before the piece to be took/placed).
            # Logging the event.
            print("{0}.1a: input {1} level {2}; get 1 from input {1}."
                  .format(str(self.env.now), self.name, str(self.input_buffer.level)))
            # Writing into the log file - prod - del
            self.data_logger.write_log("{0}.1a: input {1} level {2}; get 1 from input {1}.\n"
                                       .format(str(self.env.now), self.name, str(self.input_buffer.level)))

            # Take the raw product from raw products warehouse
            self.input_buffer.get(1)

            # Logging the event.
            print("{0}.1b: input {1} level {2}; taken 1 from input {1}. "
                  .format(str(self.env.now), self.name, str(self.input_buffer.level)))
            # Writing into the log file - prod
            self.data_logger.write_log("{0}.1b: input {1} level {2}; taken 1 from input {1}.\n"
                                       .format(str(self.env.now), self.name, str(self.input_buffer.level)))

            # Start making a new part
            time_per_part = self.mean_process_time
            done_in = time_per_part       # time_per_part() is the real stochastic function.
            while done_in:
                try:
                    # Working on the part
                    start = self.env.now
                    # Logging the event.
                    print(str(start) + ".2b: started 1 in " + self.name + ". ")
                    # Writing into the log file - prod
                    self.data_logger.write_log(str(start) + ".2b: started 1 in " + self.name + ".\n")

                    yield self.env.timeout(done_in)
                    done_in = 0     # Set 0 to exit to the loop

                except simpy.Interrupt:
                    # The machine broke.
                    self.broken = True
                    done_in -= self.env.now - start     # How much time left to finish the job?

                    # Logging the event.
                    print("\n{0}: {1} broke. {2} step for the job to be completed. Machine will be repaired in {0}\n"
                          .format(str(self.env.now), self.name, str(done_in),
                                  str(self.repair_time)))
                    # Writing into the log file - prod
                    self.data_logger.write_log("{0}: {1} broke. {2} step for the job to be completed. "
                                               .format(str(self.env.now), self.name, str(done_in)))
                    self.data_logger.write_log("Machine will be repaired in {0}\n".format(str(self.repair_time)))

                    yield self.env.timeout(self.repair_time)

                    # Machine repaired.
                    self.broken = False

                    # Logging the event. The machine is repaired.
                    print("{0}: {1} repaired. Working restarted.".format(str(self.env.now), self.name))
                    # Writing into the log file - prod
                    self.data_logger.write_log("{0}: {1} repaired. Working restarted.\n"
                                               .format(str(self.env.now), self.name))

            # Part is done
            prod_time = self.env.now
            self.parts_made += 1

            # Logging the event - prod
            print("{0}.2b: made 1 in {1}. Total pieces made: {2}.".format(str(prod_time), self.name, self.parts_made))
            # Writing into the log file - prod
            self.data_logger.write_log("{0}.2b: made 1 in {1}. Total pieces made: {2}.\n"
                                       .format(str(prod_time), self.name, self.parts_made))

            # Perform the output warehouse level checking: if full, wait 1 time step. NOT WORKING
            while self.output_buffer.level == self.output_buffer.capacity:
                print(str(self.env.now) + ": the " + self.name + " output buffer level is " +
                      str(self.output_buffer.level) + ". Waiting 1 time step and re-check.")
                self.data_logger.write_log(str(self.env.now) + ": the " + self.name + " output buffer level is " +
                                           str(self.output_buffer.level) + ". Waiting 1 time step and re-check.\n")
                yield self.env.timeout(1)

            # Logging the event - prod
            print("{0}.3a: output {1} level {2}; put 1 in output {1}.".format(str(self.env.now), self.name,
                                                                              str(self.output_buffer.level)))
            # Writing into the log file - prod
            self.data_logger.write_log("{0}.3a: output {1} level {2}; put 1 in output {1}.\n"
                                       .format(str(self.env.now), self.name, str(self.output_buffer.level)))

            # Put the finished product into the finished warehouse
            self.output_buffer.put(1)

            # Logging into the file - prod
            print("{0}.3b: output {1} level {2}; put 1 in output {1}.".format(str(self.env.now), self.name,
                                                                                str(self.output_buffer.level)))
            # Writing into the log file - prod
            self.data_logger.write_log("{0}.3b: output {1} level {2}; put 1 in output {1}.\n"
                                       .format(str(self.env.now), self.name, str(self.output_buffer.level)))

        # yield self.env.timeout(0)

    def break_machine(self):
        """Break the machine every now and then."""
        while True:
            time_to_failure = round(random.expovariate(self.break_mean))
            yield self.env.timeout(time_to_failure)
            if not self.broken:
                # Only breaks when machine is currently working.
                self.process.interrupt()


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
