"""
log_analyzer.py file: LogAnalyzer Class

Class whose responsibility is to analyse the result log of the simulation. Its purpose it to compute the following
metrics:
    - fault_Machine x = 1 AND flag_Machine_x = 1 AND flag_Machine_C = 1
    - fault_Machine x = 1 AND flag_Machine_x = 1 AND flag_Machine_C = 0

This metrics will be used to understand the impact and expectancy on the Causal Network.
"""
