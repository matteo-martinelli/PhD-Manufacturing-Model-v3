"""
SingleGlobalVariables.py class:

Class containing the global variables for the model.
"""


class GlobalVariables(object):
    # LOGISTIC PARAMETERS ----------------------------------------------------------------------------------------------

    # NOTE: Containers critical levels
    # Critical stock should be 1 business day greater than supplier take to come
    # wood_critical_stock = (((8/mean_A) * num_A + (8/mean_B) * num_B) * 3)  # 2 days to deliver + 1 marging
    # electronic_critical_stock = (8/mean_assembly) * num_assembly * 2  # 1 day to deliver + 1 marging

    # 1.Node A Raw Container
    CONTAINER_A_RAW_CAPACITY = 500
    INITIAL_A_RAW = 200
    CRITICAL_STOCK_A_RAW = 50
    SUPPLIER_LEAD_TIME_A_RAW = 0
    SUPPLIER_STD_SUPPLY_A_RAW = 50
    AFTER_REFILLING_CHECK_TIME_A_RAW = 8
    STANDARD_A_CHECK_TIME = 1

    # 2.Node A Finished Container
    CONTAINER_A_FINISHED_CAPACITY = 500
    INITIAL_A_FINISHED = 0
    # Put at one more than the container total capacity to disable.
    CRITICAL_STOCK_A_FINISHED = CONTAINER_A_FINISHED_CAPACITY + 1
    DISPATCHER_LEAD_TIME_A_FINISHED = 0
    DISPATCHER_STD_RETRIEVE_A_FINISHED = 0
    DISPATCHER_RETRIEVED_CHECK_TIME_A_FINISHED = 0
    DISPATCHER_STD_CHECK_TIME_A_FINISHED = 0

    # 3.Node B Raw Container
    CONTAINER_B_RAW_CAPACITY = 500
    INITIAL_B_RAW = 200
    CRITICAL_STOCK_B_RAW = 50
    SUPPLIER_LEAD_TIME_B_RAW = 0
    SUPPLIER_STD_SUPPLY_B_RAW = 50
    AFTER_REFILLING_CHECK_TIME_B_RAW = 8
    STANDARD_B_CHECK_TIME = 1

    # 3.Node B Finished Container
    CONTAINER_B_FINISHED_CAPACITY = 500
    INITIAL_B_FINISHED = 0
    # Put at one more than the container total capacity to disable.
    CRITICAL_STOCK_B_FINISHED = CONTAINER_B_FINISHED_CAPACITY + 1
    DISPATCHER_LEAD_TIME_B_FINISHED = 0
    DISPATCHER_STD_RETRIEVE_B_FINISHED = 0
    DISPATCHER_RETRIEVED_CHECK_TIME_B_FINISHED = 0
    DISPATCHER_STD_CHECK_TIME_B_FINISHED = 0

    # 3.Node C Finished Container
    CONTAINER_C_FINISHED_CAPACITY = 500
    INITIAL_C_FINISHED = 0
    CRITICAL_STOCK_C_FINISHED = 50
    DISPATCHER_LEAD_TIME_C_FINISHED = 0
    DISPATCHER_STD_RETRIEVE_C_FINISHED = 0
    DISPATCHER_RETRIEVED_CHECK_TIME_C_FINISHED = 8
    DISPATCHER_STD_CHECK_TIME_C_FINISHED = 1
    # Total delivered pieces.
    DELIVERED_PIECES = 0

    # Warehouse get and put standard delay
    GET_STD_DELAY = 1
    PUT_STD_DELAY = 1

    # PROCESS PARAMETERS ----------------------------------------------------------------------------------------------
    RANDOM_SEED = 42

    # 1.Node A
    NUM_MACHINES_A = 1          # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_A = 230   # Avg. processing time in seconds - std 3,5 min = 210 sec
    SIGMA_PROCESS_TIME_A = 15   # Sigma processing time.
    MTTF_A = 72000              # Mean time to failure in seconds - Standard value: 300 hours = 18000 min = 1080000 sec
    BREAK_MEAN_A = 1 / MTTF_A   # Param. for expovariate distribution
    MTTR_A = 14400               # Time it takes to repair a machine, in seconds - Standard value: 15 min = 900 sec
    REPAIR_MEAN_A = 1 / MTTR_A  # Param. for expovariate distribution

    # 2.Node B
    NUM_MACHINES_B = 1          # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_B = 240   # Avg. processing time in seconds - Standard value: 4,5 min = 270 sec
    SIGMA_PROCESS_TIME_B = 13   # Sigma processing time.
    MTTF_B = 86400              # Mean time to failure in minutes - Standard value: 600 hours = 36000 min = 2160000 sec
    BREAK_MEAN_B = 1 / MTTF_B   # Param. for expovariate distributions
    # TODO: try with 9000 min of MTTR and check if more 1 flags are printed in the log.
    MTTR_B = 12000              # Time it takes to repair a machine, in seconds - Standard value: 15 min = 900 sec
    REPAIR_MEAN_B = 1 / MTTR_B  # Param. for expovariate distribution

    # 3.Node C
    NUM_MACHINES_C = 1          # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_C = 250   # Avg. processing time in seconds - Standard value: 4 min = 240 sec
    SIGMA_PROCESS_TIME_C = 10   # Sigma processing time.
    MTTF_C = 100800             # Mean time to failure in minutes - Standard value: 450 hours = 27000 min = 1620000 sec
    BREAK_MEAN_C = 1 / MTTF_C   # Param. for expovariate distribution
    MTTR_C = 9600               # Time it takes to repair a machine, in seconds - Standard value: 15 min = 900 sec
    REPAIR_MEAN_C = 1 / MTTR_C  # Param. for expovariate distribution

    # SIM PARAMETERS ---------------------------------------------------------------------------------------------------
    WORKING_SECONDS = 60            # Working seconds for a minute in a day
    WORKING_MINUTES = 60            # Working minutes for an hour in a day
    WORKING_HOURS = 8               # Working hours in a day - for test purposes keep 1 day - 8hours/day
    SHIFTS_IN_A_WORKING_DAY = 1     # Number of shifts in a day - for test purposes keep 1 shift/day - 8hours/day
    BUSINESS_DAYS = 5               # Business days in a week - for test purposes keep 1 day - 8hours/day
    WORKING_WEEKS = 12              # Business weeks in a month - for test purposes keep 1 day - 8hours/day

    # Total simulation time in minutes (added "60 *" at the head) - for test purposes keep 1 day - 8hours/day
    SIM_TIME = WORKING_SECONDS * WORKING_MINUTES * WORKING_HOURS * SHIFTS_IN_A_WORKING_DAY * BUSINESS_DAYS * \
               WORKING_WEEKS

    # LOG PARAMETERS ---------------------------------------------------------------------------------------------------
    # Log path for generic model version
    LOG_PATH = "C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\Phd-Manufacturing-Model-v3\\logs"
    # Log filename
    LOG_FILENAME = "Log.txt"

    # OTHER PARAMETERS -------------------------------------------------------------------------------------------------

    # CLASS METHODS ----------------------------------------------------------------------------------------------------
