"""
running_model.py file:

that's the class where the model is described and launched.

NOTE: all the numbers extracted in the step generation are floats because the functions involved are stochastic.
Moreover, also process parameters are floats. To prevent "raw" steps generation, each time-step has been truncated at
the comma level.
"""

# TODO: de-clutter unused libs with pip. Check here how to do that:
#  https://stackoverflow.com/questions/25376213/delete-unused-packages-from-requirements-file
# TODO: pack all the sim files into a single package.
# TODO: manage this file as a class with a main section as program entry point.
# TODO: add sim-parameters.txt file automatic saving at the end of each sim run.
# TODO: implement log saving based on the moment the sim is run. It should be indicated as a single string in the
#  running file, passed to each object logging something, and used from each class to refer to the same lof folder for
#  that particular run

import time
import simpy
import os
import shutil
from machine_model import Machine
from input_container import InputContainer
from output_container import OutputContainer
from transference_system import TransferenceSystem
from global_variables import GlobalVariables


if __name__ == '__main__':
    # SIM INITIALIZATION -----------------------------------------------------------------------------------------------
    # Getting simulation start time
    start_time = time.time()
    start_time_string = time.strftime('%Y.%m.%d-%H.%M')

    # TODO: create here the log folder. Is it the best place where to do it? I think yes, cause is related to the sim
    # Creating the new log directory name
    log_dir = 'logs\\' + start_time_string + '-log'
    # Creating the relative new log directory
    os.mkdir(log_dir)
    # Copying the running variables to the new directory
    shutil.copy(src='global_variables.py', dst=log_dir)
    # Renaming the running variables filename in txt format
    # pre, ext = os.path.splitext(log_dir + '\\global_variables.py')
    os.rename(log_dir + '\\global_variables.py', log_dir + '\\sim-variables' + '.txt')

    # ENVIRONMENT DEFINITION -------------------------------------------------------------------------------------------
    env = simpy.Environment()

    # LOGISTIC ENTITIES DEFINITION -------------------------------------------------------------------------------------
    input_A = InputContainer(env, name="input A", log_path=log_dir,
                             max_capacity=GlobalVariables.CONTAINER_A_RAW_CAPACITY,
                             init_capacity=GlobalVariables.INITIAL_A_RAW, input_control=True,
                             critical_level_input_container=GlobalVariables.CRITICAL_STOCK_A_RAW,
                             supplier_lead_time=GlobalVariables.SUPPLIER_LEAD_TIME_A_RAW,
                             supplier_std_supply=GlobalVariables.SUPPLIER_STD_SUPPLY_A_RAW,
                             input_refilled_check_time=GlobalVariables.AFTER_REFILLING_CHECK_TIME_A_RAW,
                             input_std_check_time=GlobalVariables.STANDARD_A_CHECK_TIME)

    output_A = OutputContainer(env, name="output A", log_path=log_dir,
                               max_capacity=GlobalVariables.CONTAINER_A_FINISHED_CAPACITY,
                               init_capacity=GlobalVariables.INITIAL_A_FINISHED, output_control=False)

    input_B = InputContainer(env, name="input B", log_path=log_dir,
                             max_capacity=GlobalVariables.CONTAINER_B_RAW_CAPACITY,
                             init_capacity=GlobalVariables.INITIAL_B_RAW, input_control=True,
                             critical_level_input_container=GlobalVariables.CRITICAL_STOCK_B_RAW,
                             supplier_lead_time=GlobalVariables.SUPPLIER_LEAD_TIME_B_RAW,
                             supplier_std_supply=GlobalVariables.SUPPLIER_STD_SUPPLY_B_RAW,
                             input_refilled_check_time=GlobalVariables.AFTER_REFILLING_CHECK_TIME_B_RAW,
                             input_std_check_time=GlobalVariables.STANDARD_B_CHECK_TIME)

    output_B = OutputContainer(env, name="output B", log_path=log_dir,
                               max_capacity=GlobalVariables.CONTAINER_B_FINISHED_CAPACITY,
                               init_capacity=GlobalVariables.INITIAL_B_FINISHED, output_control=False)

    input_C = InputContainer(env, name="input C", log_path=log_dir,
                             max_capacity=GlobalVariables.CONTAINER_C_FINISHED_CAPACITY,
                             init_capacity=GlobalVariables.INITIAL_C_FINISHED, input_control=False)

    output_C = OutputContainer(env, name="output C", log_path=log_dir,
                               max_capacity=GlobalVariables.CONTAINER_C_FINISHED_CAPACITY,
                               init_capacity=GlobalVariables.INITIAL_C_FINISHED, output_control=True,
                               critical_level_output_container=GlobalVariables.CRITICAL_STOCK_C_FINISHED,
                               dispatcher_lead_time=GlobalVariables.DISPATCHER_LEAD_TIME_C_FINISHED,
                               dispatcher_retrieved_check_time=GlobalVariables
                               .DISPATCHER_RETRIEVED_CHECK_TIME_C_FINISHED,
                               dispatcher_std_check_time=GlobalVariables.DISPATCHER_STD_CHECK_TIME_C_FINISHED)

    # MACHINES DEFINITION ----------------------------------------------------------------------------------------------
    machine_A = Machine(env, "Machine A", log_dir, GlobalVariables.MEAN_PROCESS_TIME_A,
                        GlobalVariables.SIGMA_PROCESS_TIME_A, GlobalVariables.MTTF_A, GlobalVariables.MTTR_A, input_A,
                        output_A)
    machine_B = Machine(env, "Machine B", log_dir, GlobalVariables.MEAN_PROCESS_TIME_B,
                        GlobalVariables.SIGMA_PROCESS_TIME_B, GlobalVariables.MTTF_B, GlobalVariables.MTTR_B, input_B,
                        output_B)

    # Maybe **args and **kwargs could help here? -> Implement in the next version of the sw.
    # Moving from output A&B to input C
    output_containers = list()
    output_containers.append(output_A)
    output_containers.append(output_B)

    transference_from_A_B_to_C = TransferenceSystem(env, "from A and B to C", output_containers, input_C)

    machine_C = Machine(env, "Machine C", log_dir, GlobalVariables.MEAN_PROCESS_TIME_C,
                        GlobalVariables.SIGMA_PROCESS_TIME_C, GlobalVariables.MTTF_C, GlobalVariables.MTTR_C, input_C,
                        output_C)

    # SIMULATION RUN! --------------------------------------------------------------------------------------------------
    print(f'STARTING SIMULATION')
    print(f'----------------------------------')

    env.run(until=int(GlobalVariables.SIM_TIME))

    print(f'----------------------------------')
    print('Node A raw container has {0} pieces ready to be processed'.format(input_A.level))
    print('Node A raw pieces picked: {0}\n'.format(input_A.products_picked))

    print('Node A finished container has {0} pieces processed'.format(output_A.level))
    print('Node A finished container pieces stored: {0}\n'.format(output_A.products_stored))

    print('Node B raw container has {0} pieces ready to be processed'.format(input_B.level))
    print('Node B raw pieces picked: {0}\n'.format(input_B.products_picked))

    print('Node B finished container has {0} pieces processed'.format(output_B.level))
    print('Node B finished container pieces stored: {0}\n'.format(output_B.products_stored))

    print('Node C raw container has {0} pieces ready to be processed'.format(input_C.level))
    print('Node C raw pieces picked: {0}\n'.format(input_C.products_picked))

    print('Node C finished container has {0} pieces processed'.format(output_C.level))
    print('Node C finished container pieces stored: {0}\n'.format(output_C.products_stored))

    print(f'Dispatch C has %d pieces ready to go!' % output_C.level)
    print(f'----------------------------------')
    print('total pieces delivered: {0}'.format(output_C.products_delivered + output_C.level))
    print('total pieces assembled: {0}'.format(machine_C.parts_made))
    print(f'----------------------------------')
    print(f'SIMULATION COMPLETED')

    finish_time = time.time()
    sim_time = finish_time - start_time
    print("Total sim time: {} seconds".format(round(sim_time, 2)))
