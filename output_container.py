"""
output_container.py Class:

This class extends the Container/Store Class of SimPy, integrating the level control.
The level control is needed in order to not run out of available space.

Is possible to exclude the level control service.
"""

import simpy
from global_variables import *
from monitoring import *


# TODO: Implement full-level-check logic and relative raising error. Sync the logic in the machine section.
class OutputContainer(simpy.Container):

    def __init__(self, env, max_capacity, init_capacity, output_control=True, critical_level_output_container=50,
                 dispatcher_lead_time=0, dispatcher_retrieved_check_time=8, dispatcher_std_check_time=1):
        super().__init__(env, max_capacity, init_capacity)
        # self.input_container = simpy.Container(env, capacity=max_capacity, init=init_capacity)
        # The following container has to be always full. The stock-out is to avoid.
        self.output_control_container = env.process(self.output_control_container(env))

        # Basic parameters
        self.output_control = output_control
        self.critical_level_output_container = critical_level_output_container
        self.dispatcher = dispatcher_lead_time
        self.dispatcher_lead_time = dispatcher_lead_time
        self.dispatcher_retrieved_check_time = dispatcher_retrieved_check_time
        self.dispatcher_std_check_time = dispatcher_std_check_time

        # TODO: implement container counter somehow.
        self.products_delivered = 0

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.data_logger = DataLogger(self.log_path, self.log_filename)
        self.data_logger.write_log("### DATA LOG FROM OUTPUT CONTAINER FILE ###\n")

    def output_control_container(self, env):
        yield env.timeout(0)

        # If the output container service has been activated in the object instantiation...
        while self.output_control:

            # Check container level. If under the critical level, start the emptying process.
            if self.level >= self.critical_level_output_container:

                # Print the event in the console and write in the log
                print('dispatch stock is {0}, calling store to pick guitars at day {1}, hour {2}'.format(
                    self.level, int(env.now / 8), env.now % 8))
                print('----------------------------------')
                self.data_logger.write_log(str(env.now) + ".1: stock finished C upper the critical level. " +
                                           str(self.level) + " pieces left. Calling the dispatcher\n")

                # Wait for the dispatcher lead time.
                yield env.timeout(self.dispatcher_lead_time)

                # Dispatcher arrived, writing in the console.
                print('store picking {0} guitars at day {1}, hour {2}'.format(self.level,
                                                                              int(env.now / 8), env.now % 8))
                print('----------------------------------')

                # The warehouse will be completely emptied. Counting the material amount.
                self.products_delivered += self.level
                yield self.get(self.level)

                # Writing to the log file
                self.data_logger.write_log(str(env.now) + ".2: dispatcher arrived. " + str(self.level)
                                           + " pieces took by the dispatcher.\n")

                # After the dispatch, check the level status after a given time (usually 8).
                yield env.timeout(self.dispatcher_retrieved_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield env.timeout(self.dispatcher_std_check_time)
