"""
output_container.py Class:

This class extends the Container/Store Class of SimPy, integrating the level control.
The level control is needed in order to not run out of available space.

Is possible to exclude the level control service.
"""

import simpy
from monitoring import *
from global_variables import *


class OutputContainer(simpy.Container):
    def __init__(self, env, name, max_capacity, init_capacity, output_control=True, critical_level_output_container=50,
                 dispatcher_lead_time=0, dispatcher_retrieved_check_time=8, dispatcher_std_check_time=1):
        super().__init__(env, max_capacity, init_capacity)
        # self.input_container = simpy.Container(env, capacity=max_capacity, init=init_capacity)
        self.name = name
        self.env = env
        # The following container has to be always full. The stock-out is to avoid.
        self.env.process(self._output_control_container())

        # Basic parameters
        self.output_control = output_control
        self.critical_level_output_container = critical_level_output_container
        self.dispatcher = dispatcher_lead_time
        self.dispatcher_lead_time = dispatcher_lead_time
        self.dispatcher_retrieved_check_time = dispatcher_retrieved_check_time
        self.dispatcher_std_check_time = dispatcher_std_check_time

        self.products_stored = 0
        self.products_delivered = 0

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.data_logger = DataLogger(self.log_path, self.log_filename)
        self.data_logger.write_log_txt("### DATA LOG FROM OUTPUT CONTAINER FILE ###\n")

    def _output_control_container(self):
        yield self.env.timeout(0)

        # If the output container service has been activated in the object instantiation...
        while self.output_control:

            # Check container level. If under the critical level, start the emptying process.
            if self.level >= self.critical_level_output_container:

                # Logging the event.
                print('{0}.1 - out_log: container {1} dispatch stock upper the critical level{2}, {3} pieces left.'
                      .format(self.env.now, self.name, self.critical_level_output_container, self.level))
                print('Calling the dispatcher.')
                print('----------------------------------')
                # Writing into the log file - logistic
                self.data_logger.write_log_txt('{0}.1 - out_log: container {1} dispatch stock upper the critical level '
                                               '{2}, {3} pieces left.'.format(self.env.now, self.name,
                                                                              self.critical_level_output_container,
                                                                              self.level))
                self.data_logger.write_log_txt('Calling the dispatcher.\n')

                # Wait for the dispatcher lead time.
                yield self.env.timeout(self.dispatcher_lead_time)

                # Dispatcher arrived, writing in the console.
                print('{0}.2 - out_log: component dispatcher {1} arrived'.format(self.env.now, self.name))
                # Writing into the log file - logistic
                self.data_logger.write_log_txt('{0}.2 - out_log: component dispatcher {1} arrived\n'.format(self.env.now, self.name))

                # The warehouse will be completely emptied. Counting the material amount.
                self.products_delivered += self.level

                # Logging the event.
                print("{0}.3 - out_log: dispatcher arrived. {1} pieces took by the dispatcher.\n"
                      .format(str(self.env.now), str(self.level)))
                print('----------------------------------')
                # Writing to the log file
                self.data_logger.write_log_txt("{0}.3 - out_log: dispatcher arrived. {1} pieces took by the "
                                               "dispatcher.\n".format(str(self.env.now), str(self.level)))
                # Dispatcher get made after the log; otherwise the level logged would be zero.
                yield self.get(self.level)

                # After the dispatch, check the level status after a given time (usually 8).
                yield self.env.timeout(self.dispatcher_retrieved_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield self.env.timeout(self.dispatcher_std_check_time)
