"""
Model.py file:

that's the class where the model is described and launched.
"""

# TODO: refactor the import statements adding the package reference in each imported file.
from logistic_model import *
from machine_model import *
from global_variables import *
from input_container import *
from output_container import *

# ENVIRONMENT DEFINITION -----------------------------------------------------------------------------------------------
env = simpy.Environment()

# LOGISTIC ENTITIES DEFINITION -----------------------------------------------------------------------------------------
input_A = InputContainer(env, max_capacity=GlobalVariables.CONTAINER_A_RAW_CAPACITY,
                         init_capacity=GlobalVariables.INITIAL_A_RAW, input_control=True,
                         critical_level_input_container=GlobalVariables.CRITICAL_STOCK_A_RAW,
                         supplier_lead_time=GlobalVariables.SUPPLIER_LEAD_TIME_A_RAW,
                         supplier_std_supply=GlobalVariables.SUPPLIER_STD_SUPPLY_A_RAW,
                         input_refilled_check_time=GlobalVariables.AFTER_REFILLING_CHECK_TIME_A_RAW,
                         input_std_check_time=GlobalVariables.STANDARD_A_CHECK_TIME)

output_A = OutputContainer(env, max_capacity=GlobalVariables.CONTAINER_A_FINISHED_CAPACITY,
                           init_capacity=GlobalVariables.INITIAL_A_FINISHED, output_control=False)


input_B = InputContainer(env, max_capacity=GlobalVariables.CONTAINER_B_RAW_CAPACITY,
                         init_capacity=GlobalVariables.INITIAL_B_RAW, input_control=True,
                         critical_level_input_container=GlobalVariables.CRITICAL_STOCK_B_RAW,
                         supplier_lead_time=GlobalVariables.SUPPLIER_LEAD_TIME_B_RAW,
                         supplier_std_supply=GlobalVariables.SUPPLIER_STD_SUPPLY_B_RAW,
                         input_refilled_check_time=GlobalVariables.AFTER_REFILLING_CHECK_TIME_B_RAW,
                         input_std_check_time=GlobalVariables.STANDARD_B_CHECK_TIME)

output_B = OutputContainer(env, max_capacity=GlobalVariables.CONTAINER_B_FINISHED_CAPACITY,
                           init_capacity=GlobalVariables.INITIAL_B_FINISHED, output_control=False)

input_C = InputContainer(env, max_capacity=GlobalVariables.CONTAINER_C_FINISHED_CAPACITY,
                         init_capacity=GlobalVariables.INITIAL_C_FINISHED, input_control=False)

output_C = OutputContainer(env, max_capacity=GlobalVariables.CONTAINER_C_FINISHED_CAPACITY,
                           init_capacity=GlobalVariables.INITIAL_C_FINISHED, output_control=True,
                           critical_level_output_container=GlobalVariables.CRITICAL_STOCK_C_FINISHED,
                           dispatcher_lead_time=GlobalVariables.DISPATCHER_LEAD_TIME_C_FINISHED,
                           dispatcher_retrieved_check_time=GlobalVariables.DISPATCHER_RETRIEVED_CHECK_TIME_C_FINISHED,
                           dispatcher_std_check_time=GlobalVariables.DISPATCHER_STD_CHECK_TIME_C_FINISHED)

# REPAIRMEN DEFINITION -------------------------------------------------------------------------------------------------
# TODO: after the process testing, switch from 3 to 1 repairman definition, changing its capacity.
# actual_repairman_A = simpy.PreemptiveResource(env, capacity=1)
# actual_repairman_B = simpy.PreemptiveResource(env, capacity=1)
# actual_repairman_C = simpy.PreemptiveResource(env, capacity=1)

# MACHINES DEFINITION --------------------------------------------------------------------------------------------------
machine_A = Machine(env, "Machine A", GlobalVariables.MEAN_PROCESS_TIME_A, GlobalVariables.SIGMA_PROCESS_TIME_A,
                    GlobalVariables.MTTF_A, GlobalVariables.REPAIR_TIME_A, input_A, output_A)
machine_B = Machine(env, "Machine B", GlobalVariables.MEAN_PROCESS_TIME_B, GlobalVariables.SIGMA_PROCESS_TIME_B,
                    GlobalVariables.MTTF_B, GlobalVariables.REPAIR_TIME_B, input_B, output_B)

# TODO: maybe **args and **kwargs could help here?
# Moving from output A&B to input C
output_A.get(1)
output_B.get(1)
input_C.put(1)

machine_C = Machine(env, "Machine C", GlobalVariables.MEAN_PROCESS_TIME_C, GlobalVariables.SIGMA_PROCESS_TIME_C,
                    GlobalVariables.MTTF_C, GlobalVariables.REPAIR_TIME_C, input_C, output_C)

# SIMULATION RUN! ------------------------------------------------------------------------------------------------------
print(f'STARTING SIMULATION')
print(f'----------------------------------')

env.run(until=int(GlobalVariables.SIM_TIME))

print('Node A raw container has {0} pieces ready to be processed'.format(input_A.level))
print('Node A finished container has {0} pieces ready to be processed'.
      format(output_A.level))

print('Node B raw container has {0} pieces ready to be processed'.format(input_B.level))
print('Node B finished container has {0} pieces ready to be processed'.format(output_B.level))

print(f'Dispatch C has %d pieces ready to go!' % output_C.level)
print(f'----------------------------------')
print('total pieces delivered: {0}'.format(output_C.products_delivered + output_C.level))
print('total pieces assembled: {0}'.format(machine_C.parts_made))
print(f'----------------------------------')
print(f'SIMULATION COMPLETED')
