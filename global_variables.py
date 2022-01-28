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

    # 1.Node A - Note: the aleatory process time has not been used.
    NUM_MACHINES_A = 1              # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_A = 1         # Avg. processing time in hours.
    SIGMA_PROCESS_TIME_A = 0.15     # Sigma processing time.
    MTTF_A = 300                    # Mean time to failure in minutes Initial value: 300
    BREAK_MEAN_A = 1 / MTTF_A       # Param. for expovariate distribution
    MTTR_A = 4                      # Time it takes to repair a machine, in minutes. Initial value: 30.
    REPAIR_MEAN_A = 1 / MTTR_A      # Param. for expovariate distribution

    # 2.Node B - Note: the aleatory process time has not been used.
    NUM_MACHINES_B = 1              # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_B = 1         # Avg. processing time in hours.
    SIGMA_PROCESS_TIME_B = 0.1      # Sigma processing time.
    MTTF_B = 600                    # Mean time to failure in minutes
    BREAK_MEAN_B = 1 / MTTF_B       # Param. for expovariate distribution
    MTTR_B = 4                      # Time it takes to repair a machine, in minutes. Initial value: 30.
    REPAIR_MEAN_B = 1 / MTTR_B      # Param. for expovariate distribution

    # 3.Node C - Note: the aleatory process time has not been used.
    NUM_MACHINES_C = 1              # Number of machines in the work-shop.
    MEAN_PROCESS_TIME_C = 1         # Avg. processing time in hours.
    SIGMA_PROCESS_TIME_C = 0.08     # Sigma processing time.
    MTTF_C = 400                    # Mean time to failure in minutes
    BREAK_MEAN_C = 1 / MTTF_C       # Param. for expovariate distribution
    MTTR_C = 4                      # Time it takes to repair a machine, in minutes. Initial value: 30.
    REPAIR_MEAN_C = 1 / MTTR_C      # Param. for expovariate distribution

    # SIM PARAMETERS ---------------------------------------------------------------------------------------------------
    # Working hours in a day - for test purposes keep 1 day - 8hours/day
    WORKING_HOURS = 8
    # Number of shifts in a day - for test purposes keep 1 shift/day - 8hours/day
    SHIFTS_IN_A_WORKING_DAY = 1
    # Business days in a week - for test purposes keep 1 day - 8hours/day
    BUSINESS_DAYS = 5
    # Business weeks in a month - for test purposes keep 1 day - 8hours/day
    WORKING_WEEKS = 52
    # Total simulation time in minutes (added "60 *" at the head) - for test purposes keep 1 day - 8hours/day
    SIM_TIME = WORKING_HOURS * SHIFTS_IN_A_WORKING_DAY * BUSINESS_DAYS * WORKING_WEEKS

    # LOG PARAMETERS ---------------------------------------------------------------------------------------------------
    # Log path for generic model version
    LOG_PATH = "C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\Phd-Manufacturing-Model-v3\\logs"
    # Log filename
    LOG_FILENAME = "Log.txt"

    # OTHER PARAMETERS -------------------------------------------------------------------------------------------------

    # CLASS METHODS ----------------------------------------------------------------------------------------------------
