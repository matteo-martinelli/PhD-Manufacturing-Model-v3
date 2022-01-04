"""
input_container.py Class:

This class extends the Container/Store Class of SimPy, integrating the level control.
The level control is needed in order to have always with some material available;
"""

# from Makers import *
import simpy
from global_variables import *
from monitoring import *


# TODO: Implement full-level-check logic and relative raising error. Sync the logic in the machine section.
class InputContainer(simpy.Container):

    def __init__(self, env, max_capacity, init_capacity, critical_level_input_container=50, supplier_lead_time=0,
                 supplier_std_supply=50, input_refilled_check_time=8, input_std_check_time=1):
        super().__init__(env, max_capacity, init_capacity)
        # self.input_container = simpy.Container(env, capacity=max_capacity, init=init_capacity)
        # The following container has to be always full. The stock-out is to avoid.
        self.input_control_container = env.process(self.input_control_container(env))

        # Basic parameters - to be confirmed
        self.critical_level_input_container = critical_level_input_container
        self.supplier_lead_time = supplier_lead_time
        self.supplier_std_supply = supplier_std_supply
        self.input_refilled_check_time = input_refilled_check_time
        self.input_std_check_time = input_std_check_time

        self.products_delivered = 0

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH_generic_version
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.data_logger = DataLogger(self.log_path, self.log_filename)
        self.data_logger.write_log("### DATA LOG FROM PROCESS MACHINE FILE ###\n")

    def input_control_container(self, env):
        yield env.timeout(0)

        # Check container level. If under the critical level, start the emptying process.
        # if self.input_container.level <= self.critical_level_input_container:
        if self.level <= self.critical_level_input_container:

            # Writing to the log file
            print('A component stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                self.level, int(env.now / 8), env.now % 8))
            print('calling A component supplier')
            print('----------------------------------')
            self.data_logger.write_log(str(env.now) + ".1: stock raw A under the critical level. " +
                                       str(self.level) + " pieces left. Calling the supplier\n")

            # Wait for the refiller lead time.
            yield env.timeout(self.supplier_lead_time)

            # Refiller arrived, writing in the console.
            print('A component supplier arrives at day {0}, hour {1}'.format(int(env.now / 8), env.now % 8))

            # The warehouse will be refilled with a standard quantity.
            yield self.put(50)

            # Writing to the console and the log.
            print('new A component stock is {0}'.format(self.level))
            print('----------------------------------')
            self.data_logger.write_log(str(env.now) + ".2: supplier arrived. " + str(50) +
                                       " pieces supplied to raw B. New level " + str(self.level) +
                                       ".\n")

            # After the refill, check the level status after a given time (usually 8).
            yield env.timeout(self.input_refilled_check_time)
        else:
            # If no dispatch, check the level status after at the next step.
            yield env.timeout(self.input_std_check_time)
