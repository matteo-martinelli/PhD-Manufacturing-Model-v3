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

    def __init__(self, env, name, max_capacity, init_capacity, output_control=True, critical_level_output_container=50,
                 dispatcher_lead_time=0, dispatcher_retrieved_check_time=8, dispatcher_std_check_time=1):
        super().__init__(env, max_capacity, init_capacity)
        # self.input_container = simpy.Container(env, capacity=max_capacity, init=init_capacity)
        self.name = name
        self.env = env
        # The following container has to be always full. The stock-out is to avoid.
        self.output_control_container = env.process(self.output_control_container(self.env))

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
        self.excel_filename = GlobalVariables.EXCEL_FILENAME
        self.data_logger = DataLogger(self.log_path, self.log_filename, self.excel_filename)
        self.data_logger.write_log("### DATA LOG FROM OUTPUT CONTAINER FILE ###\n")

    def output_control_container(self, env):
        yield env.timeout(0)

        # If the output container service has been activated in the object instantiation...
        while self.output_control:

            # Check container level. If under the critical level, start the emptying process.
            if self.level >= self.critical_level_output_container:

                # Logging the event.
                print('{0}.1: container {1} dispatch stock upper the critical level{2}, {3} pieces left.'
                      .format(env.now, self.name, self.critical_level_output_container, self.level))
                print('Calling the dispatcher.')
                print('----------------------------------')
                # Writing into the log file - logistic
                self.data_logger.write_log('{0}.1: container {1} dispatch stock upper the critical level {2}, {3} '
                                           'pieces left.'.format(env.now, self.name,
                                                                 self.critical_level_output_container, self.level))
                self.data_logger.write_log('Calling the dispatcher.\n')

                # Wait for the dispatcher lead time.
                yield env.timeout(self.dispatcher_lead_time)

                # Dispatcher arrived, writing in the console.
                print('{0}.2: component dispatcher {1} arrived'.format(env.now, self.name))
                # Writing into the log file - logistic
                self.data_logger.write_log('{0}.2: component dispatcher {1} arrived\n'.format(env.now, self.name))

                # The warehouse will be completely emptied. Counting the material amount.
                self.products_delivered += self.level

                # Logging the event.
                print("{0}.3: dispatcher arrived. {1} pieces took by the dispatcher.\n"
                      .format(str(env.now), str(self.level)))
                print('----------------------------------')
                # Writing to the log file
                self.data_logger.write_log("{0}.3: dispatcher arrived. {1} pieces took by the dispatcher.\n"
                                           .format(str(env.now), str(self.level)))
                # Dispatcher get made after the log; otherwise the level logged would be zero.
                yield self.get(self.level)

                # After the dispatch, check the level status after a given time (usually 8).
                yield env.timeout(self.dispatcher_retrieved_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield env.timeout(self.dispatcher_std_check_time)
