"""
Machine_A.py class:

Class describing a single machine behaviour.
Random breakdowns are embedded in the model.
The file have to be integrated with the env.

It takes as input also the LogisticModel, to get and put raw materials from warehouses.
"""
import random
import simpy
from global_variables import *
import monitoring


# TODO: Add the breakdown logging and console printing. Test the breakdown system.
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
        self.env.process(self.break_machine())  # To exclude breakdowns, comment this line.

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH_generic_version
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.data_logger = Monitoring.DataLogger(self.log_path, self.log_filename)
        self.data_logger.write_log("### DATA LOG FROM PROCESS MACHINE FILE ###\n")

    #  Function describing the machine process.
    def working(self):
        """Produces parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairman when this happens.
        """
        while True:
            # Perform the output warehouse level checking: if empty, wait 1 time step. NOT WORKING.
            input_node_level = self.input_buffer.input_container.level
            """
            while input_node_level == 0:
                print(str(self.env.now) + ": the " + self.name + " input buffer level is " + str(input_node_level) +
                      ". Waiting 1 time step and re-check.")
                self.data_logger.write_log(str(self.env.now) + ": the " + self.name + " input buffer level is "
                                           + str(input_node_level) + ". Waiting 1 time step and re-check.\n")
                yield self.env.timeout(1)
            """
            # Warehouse tracking made before the piece to be took/placed.
            input_time = self.env.now

            # Take the raw product from raw products warehouse
            self.input_buffer.input_container.get(1)

            # Start making a new part
            time_per_part = self.mean_process_time
            done_in = time_per_part       # time_per_part() is the real stochastic function.
            while done_in:
                try:
                    # Working on the part
                    start = self.env.now
                    yield self.env.timeout(done_in)
                    done_in = 0     # Set 0 to exit to the loop

                except simpy.Interrupt:
                    # The machine broke.
                    self.broken = True
                    done_in -= self.env.now - start     # How much time left to finish the job?

                    # Logging the event.
                    print("\n" + str(self.env.now) + ": " + self.name + " broke." + str(done_in) +
                          " step for the job to be completed. Machine will be repaired in " +
                          str(self.repair_time) + "\n")
                    self.data_logger.write_log(str(self.env.now) + ": " + self.name + " broke. " + str(done_in) +
                                               " step for the job to be completed.")
                    self.data_logger.write_log("Machine will be repaired in " + str(self.repair_time) + "\n")

                    yield self.env.timeout(self.repair_time)

                    # Machine repaired.
                    self.broken = False

                    # Logging the event. The machine is repaired.
                    print(str(self.env.now) + ": " + self.name + " repaired. Working restarted.")
                    self.data_logger.write_log(str(self.env.now) + ": " + self.name +
                                               " repaired. Working restarted.\n")

            # Part is done
            prod_time = self.env.now
            self.parts_made += 1
            print(str(prod_time) + ": Node " + self.name + " assembled {0} pieces.".format(self.parts_made))

            # Perform the output warehouse level checking: if full, wait 1 time step. NOT WORKING
            output_node_level = self.output_buffer.output_container.level
            """
            while output_node_level == self.output_buffer.output_container.capacity:
                print(str(self.env.now) + ": the " + self.name + " output buffer level is " + str(output_node_level) +
                      ". Waiting 1 time step and re-check.")
                self.data_logger.write_log(str(self.env.now) + ": the " + self.name + " output buffer level is " +
                                           str(output_node_level) + ". Waiting 1 time step and re-check.\n")
                yield self.env.timeout(1)
            """
            # Put the finished product into the finished warehouse
            self.output_buffer.output_container.put(1)
            output_time = self.env.now

            # Writing to the log file
            self.data_logger.write_log(str(input_time) + ".1: input " + self.name + " level " + str(input_node_level)
                                       + "; get 1 from input " + self.name + ".\n")
            self.data_logger.write_log(str(prod_time) + ".2: made 1 in " + self.name + ".\n")
            self.data_logger.write_log(str(output_time) + ".3: output " + self.name + " level " + str(output_node_level)
                                       + "; put 1 in output " + self.name + ".\n")
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
