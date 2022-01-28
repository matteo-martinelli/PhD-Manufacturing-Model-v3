"""
input_container.py Class:

This class extends the Container/Store Class of SimPy, integrating the level control.
The level control is needed in order to have always some material available.

Is possible to exclude the level control service.
"""

import simpy
from monitoring import DataLogger
from global_variables import GlobalVariables


# TODO: think about turning private the appropriate attributes.
class InputContainer(simpy.Container):

    def __init__(self, env, name, max_capacity, init_capacity, input_control=True, critical_level_input_container=50,
                 supplier_lead_time=0, supplier_std_supply=50, input_refilled_check_time=8, input_std_check_time=1):
        super().__init__(env, max_capacity, init_capacity)
        # self.input_container = simpy.Container(env, capacity=max_capacity, init=init_capacity)
        self.name = name
        self._env = env
        # The following container has to be always full. The stock-out is to avoid.
        self._env.process(self._input_control_container())

        # Basic parameters
        self.input_control = input_control
        self.critical_level = critical_level_input_container
        self.supplier_lead_time = supplier_lead_time
        self.supplier_std_supply = supplier_std_supply
        self.after_refilling_check_time = input_refilled_check_time
        self.std_check_time = input_std_check_time

        self.products_picked = 0

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.data_logger = DataLogger(self.log_path, self.log_filename)
        self.data_logger.write_log_txt("### DATA LOG FROM INPUT CONTAINER FILE ###\n")

    def _input_control_container(self):
        yield self._env.timeout(0)

        # If the input container service has been activated in the object instantiation...
        while self.input_control:

            # Check container level. If under the critical level, start the emptying process.
            # if self.input_container.level <= self.critical_level_input_container:
            if self.level <= self.critical_level:

                # Logging the event.
                print('{0}.1 in_log: container {1} stock under the critical level {2}, {3} pieces left.'
                      .format(self._env.now, self.name, self.critical_level, self.level))
                print('calling the component supplier')
                print('----------------------------------')
                # Writing into the log file - logistic
                self.data_logger.write_log_txt('{0}.1 in_log: container {1} stock under the critical level {2}, {3} '
                                               'pieces left.'.format(self._env.now, self.name, self.critical_level,
                                                                     self.level))
                self.data_logger.write_log_txt('Calling the components supplier. \n')

                # Wait for the supplier lead time.
                yield self._env.timeout(self.supplier_lead_time)

                # Supplier arrived, logging the event.
                print('{0}.2 in_log: component supplier {1} arrived'.format(self._env.now, self.name))
                # Writing into the log file - logistic
                self.data_logger.write_log_txt('{0}.2 in_log: component supplier {1} arrived\n'.format(self._env.now, self.name))

                # The warehouse will be refilled with a standard quantity.
                yield self.put(50)

                # Logging the event.
                print('{0}.3 in_log: container {1} new A component stock is {2}'.format(self._env.now, self.name, self.level))
                print('----------------------------------')
                # Writing into the log file - logistic
                self.data_logger.write_log_txt('{0}.3 in_log: container {1} new A component stock is {2}\n'
                                               .format(self._env.now, self.name, self.level))

                # After the refill, check the level status after a given time (usually 8).
                yield self._env.timeout(self.after_refilling_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield self._env.timeout(self.std_check_time)
