"""
LogisticModel_Generic.py Class: LogisticWrapper

This class wraps the Container Class of SimPy, integrating the level control.

It can be differentiated in 3 types:
    1. an input warehouse, which needs a level control because it needs to have always with some material available;
    2. a middle warehouse, which needs no control, because is "leveled" between input e output production nodes;
    3. an output warehouse, which needs a level control because it needs to have always space for output finished
    product.

The warehouse type is discriminated with the passed parameters (signature?) of the constructor. The default warehouse
type is the second one, middle warehouse.
"""

# from Makers import *
import simpy
import monitoring
from global_variables import *


# TODO: split this class into two different classes - one for the input container and one for the output. Apply
#  subclasses with respect to the simpy.Container class.
class LogisticWrapper:
    def input_control_container(self, env):
        yield env.timeout(0)

        # If the input container service has been activated in the object instantiation...
        while self.bool_input_control_container:

            # Check container level. If under the critical level, start the emptying process.
            if self.input_container.level <= self.critical_level_input_container:

                # Writing to the log file
                print('A component stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.input_container.level, int(env.now / 8), env.now % 8))
                print('calling A component supplier')
                print('----------------------------------')
                self.data_logger.write_log(str(env.now) + ".1: stock raw A under the critical level. " +
                                           str(self.input_container.level) + " pieces left. Calling the supplier\n")

                # Wait for the refiller lead time.
                yield env.timeout(self.supplier_lead_time)

                # Refiller arrived, writing in the console.
                print('A component supplier arrives at day {0}, hour {1}'.format(int(env.now / 8), env.now % 8))

                # The warehouse will be refilled with a standard quantity.
                yield self.input_container.put(50)

                # Writing to the console and the log.
                print('new A component stock is {0}'.format(self.input_container.level))
                print('----------------------------------')
                self.data_logger.write_log(str(env.now) + ".2: supplier arrived. " + str(50) +
                                           " pieces supplied to raw B. New level " + str(self.input_container.level) +
                                           ".\n")

                # After the refill, check the level status after a given time (usually 8).
                yield env.timeout(self.input_refilled_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield env.timeout(self.input_std_check_time)

    def output_control_container(self, env):
        yield env.timeout(0)

        # If the output container service has been activated in the object instantiation...
        while self.bool_output_control_container:

            # Check container level. If under the critical level, start the emptying process.
            if self.output_container.level >= self.critical_level_output_container:

                # Print the event in the console and write in the log
                print('dispatch stock is {0}, calling store to pick guitars at day {1}, hour {2}'.format(
                    self.output_control_container.level, int(env.now/8), env.now % 8))
                print('----------------------------------')
                self.data_logger.write_log(str(env.now) + ".1: stock finished C upper the critical level. " +
                                           str(self.output_container.level) + " pieces left. Calling the dispatcher\n")

                # Wait for the dispatcher lead time.
                yield env.timeout(self.dispatcher_lead_time)

                # Dispatcher arrived, writing in the console.
                print('store picking {0} guitars at day {1}, hour {2}'.format(self.output_control_container.level,
                                                                              int(env.now / 8), env.now % 8))
                print('----------------------------------')

                # The warehouse will be completely emptied. Counting the material amount.
                self.products_delivered += self.output_control_container.level
                yield self.output_control_container.get(self.output_control_container.level)

                # Writing to the log file
                self.data_logger.write_log(str(env.now) + ".2: dispatcher arrived. " + str(self.output_container.level)
                                           + " pieces took by the dispatcher.\n")

                # After the dispatch, check the level status after a given time (usually 8).
                yield env.timeout(self.dispatcher_retrieved_check_time)
            else:
                # If no dispatch, check the level status after at the next step.
                yield env.timeout(self.dispatcher_std_check_time)

    def __init__(self, env, max_capacity, init_capacity, bool_input_control_container=False,
                 critical_level_input_container=50, supplier_lead_time=0, supplier_std_supply=50,
                 input_refilled_check_time=8, input_std_check_time=1, bool_output_control_container=False,
                 critical_level_output_container=50, dispatcher_lead_time=0, dispatcher_retrieved_check_time=8,
                 dispatcher_std_check_time=1):

        self.input_container = simpy.Container(env, capacity=max_capacity, init=init_capacity)
        self.output_container = simpy.Container(env, capacity=max_capacity, init=init_capacity)
        # The following container has to be always full. The stock-out is to avoid.
        self.input_control_container = env.process(self.input_control_container(env))
        # The following container has to be emptied when runs full.
        self.output_control_container = env.process(self.output_control_container(env))

        # Basic parameters - to be confirmed
        self.bool_input_control_container = bool_input_control_container
        self.critical_level_input_container = critical_level_input_container
        self.supplier_lead_time = supplier_lead_time
        self.supplier_std_supply = supplier_std_supply
        self.input_refilled_check_time = input_refilled_check_time
        self.input_std_check_time = input_std_check_time

        self.bool_output_control_container = bool_output_control_container
        self.products_delivered = 0
        self.critical_level_output_container = critical_level_output_container
        self.dispatcher_lead_time = dispatcher_lead_time

        self.dispatcher_retrieved_check_time = dispatcher_retrieved_check_time
        self.dispatcher_std_check_time = dispatcher_std_check_time

        # Logging objects
        self.log_path = GlobalVariables.LOG_PATH_generic_version
        self.log_filename = GlobalVariables.LOG_FILENAME
        self.data_logger = Monitoring.DataLogger(self.log_path, self.log_filename)
        self.data_logger.write_log("### DATA LOG FROM PROCESS MACHINE FILE ###\n")
