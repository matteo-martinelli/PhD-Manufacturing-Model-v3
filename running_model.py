"""
Model.py file:

that's the class where the model is described and launched.
"""

# TODO: refactor the import statements adding the package reference in each imported file.
from logistic_model import *
from machine_model import *
from global_variables import *

# ENVIRONMENT DEFINITION -----------------------------------------------------------------------------------------------
env = simpy.Environment()

# LOGISTIC ENTITIES DEFINITION -----------------------------------------------------------------------------------------
input_A = LogisticWrapper(env, max_capacity=global_variables.CONTAINER_A_RAW_CAPACITY,
                          init_capacity=global_variables.INITIAL_A_RAW, bool_input_control_container=True,
                          critical_level_input_container=global_variables.CRITICAL_STOCK_A_RAW,
                          supplier_lead_time=global_variables.SUPPLIER_LEAD_TIME_A_RAW,
                          supplier_std_supply=global_variables.SUPPLIER_STD_SUPPLY_A_RAW,
                          input_refilled_check_time=global_variables.AFTER_REFILLING_CHECK_TIME_A_RAW,
                          input_std_check_time=global_variables.STANDARD_A_CHECK_TIME,
                          bool_output_control_container=False)

output_A = LogisticWrapper(env, max_capacity=global_variables.CONTAINER_A_FINISHED_CAPACITY,
                           init_capacity=global_variables.INITIAL_A_FINISHED, bool_input_control_container=False,
                           bool_output_control_container=False)

input_B = LogisticWrapper(env, max_capacity=global_variables.CONTAINER_B_RAW_CAPACITY,
                          init_capacity=global_variables.INITIAL_B_RAW, bool_input_control_container=True,
                          critical_level_input_container=global_variables.CRITICAL_STOCK_B_RAW,
                          supplier_lead_time=global_variables.SUPPLIER_LEAD_TIME_B_RAW,
                          supplier_std_supply=global_variables.SUPPLIER_STD_SUPPLY_B_RAW,
                          input_refilled_check_time=global_variables.AFTER_REFILLING_CHECK_TIME_B_RAW,
                          input_std_check_time=global_variables.STANDARD_B_CHECK_TIME,
                          bool_output_control_container=False)

output_B = LogisticWrapper(env, max_capacity=global_variables.CONTAINER_B_FINISHED_CAPACITY,
                           init_capacity=global_variables.INITIAL_B_FINISHED, bool_input_control_container=False,
                           bool_output_control_container=False)

input_C = LogisticWrapper(env, max_capacity=global_variables.CONTAINER_C_FINISHED_CAPACITY,
                          init_capacity=global_variables.INITIAL_C_FINISHED, bool_input_control_container=False,
                          bool_output_control_container=False)

output_C = LogisticWrapper(env, max_capacity=global_variables.CONTAINER_C_FINISHED_CAPACITY,
                           init_capacity=global_variables.INITIAL_C_FINISHED, bool_input_control_container=False,
                           bool_output_control_container=True,
                           critical_level_output_container=global_variables.CRITICAL_STOCK_C_FINISHED,
                           dispatcher_lead_time=global_variables.DISPATCHER_LEAD_TIME_C_FINISHED,
                           dispatcher_retrieved_check_time=global_variables.DISPATCHER_RETRIEVED_CHECK_TIME_C_FINISHED,
                           dispatcher_std_check_time=global_variables.DISPATCHER_STD_CHECK_TIME_C_FINISHED)

# REPAIRMEN DEFINITION -------------------------------------------------------------------------------------------------
# TODO: after the process testing, switch from 3 to 1 repairman definition, changing its capacity.
# actual_repairman_A = simpy.PreemptiveResource(env, capacity=1)
# actual_repairman_B = simpy.PreemptiveResource(env, capacity=1)
# actual_repairman_C = simpy.PreemptiveResource(env, capacity=1)

# MACHINES DEFINITION --------------------------------------------------------------------------------------------------
machine_A = Machine(env, "Machine A", global_variables.MEAN_PROCESS_TIME_A, global_variables.SIGMA_PROCESS_TIME_A,
                    global_variables.MTTF_A, global_variables.REPAIR_TIME_A, input_A, output_A)
machine_B = Machine(env, "Machine B", global_variables.MEAN_PROCESS_TIME_B, global_variables.SIGMA_PROCESS_TIME_B,
                    global_variables.MTTF_B, global_variables.REPAIR_TIME_B, input_B, output_B)

# TODO: maybe **args and **kwargs could help here?
# Moving from output A&B to input C
output_A.input_container.get(1)
output_B.input_container.get(1)
input_C.input_container.put(1)

machine_C = Machine(env, "Machine C", global_variables.MEAN_PROCESS_TIME_C, global_variables.SIGMA_PROCESS_TIME_C,
                    global_variables.MTTF_C, global_variables.REPAIR_TIME_C, input_C, output_C)

# SIMULATION RUN! ------------------------------------------------------------------------------------------------------
print(f'STARTING SIMULATION')
print(f'----------------------------------')

env.run(until=int(global_variables.SIM_TIME))

print('Node A raw container has {0} pieces ready to be processed'.format(input_A.input_container.level))
print('Node A finished container has {0} pieces ready to be processed'.
      format(output_A.output_container.level))

print('Node B raw container has {0} pieces ready to be processed'.format(input_B.input_container.level))
print('Node B finished container has {0} pieces ready to be processed'.format(output_B.output_container.level))

print(f'Dispatch C has %d pieces ready to go!' % output_C.output_container.level)
print(f'----------------------------------')
print('total pieces delivered: {0}'.format(output_C.products_delivered + output_C.output_container.level))
print('total pieces assembled: {0}'.format(machine_C.parts_made))
print(f'----------------------------------')
print(f'SIMULATION COMPLETED')
