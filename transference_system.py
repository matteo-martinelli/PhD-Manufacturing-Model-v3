"""
transference_system.py class:

Class that has the responsibility to move material from the raw container A and B to the container C.
Written in the most generic way, still a class taylor made to solve a singular problem.
"""


# TRANSFERENCE SYSTEM CLASS --------------------------------------------------------------------------------------------
class TransferenceSystem(object):
    """
    Takes as input one (more in the future) input containers and one output container.
    """
    def __init__(self, env, process_name, input_containers, output_container):
        self.env = env
        self._process_name = process_name
        self._input_containers = input_containers    # This is passed as a list
        self._output_container = output_container

        # self.process = env.process(self.material_transfer())
        # self.env.process(self.material_transfer(env))
        self._material_transfer = env.process(self._material_transfer(self.env))

    #  Function describing the machine process.
    def _material_transfer(self, env):
        yield env.timeout(0)

        while True:
            # Assuming that the input buffers are not empty and the output are not full.
            not_empty = True
            not_full = True
            
            # Looping all the input elements...
            for element in range(len(self._input_containers)):
                # ...if the input element is empty, change the flag in False.
                if self._input_containers[element].level is 0:
                    not_empty = False

            # ...if the output container is full, change the flag in False.
            if self._output_container.level is self._output_container.capacity:
                not_full = False

            # If the input buffers are not full ...
            if not_empty is True and not_full is True:
                # ... get all the material in the input container ...
                for element in range(len(self._input_containers)):
                    self._input_containers[element].get(1)
                # ... and put the material into the output container
                self._output_container.put(1)
            # Then wait one time-step and re-do the buffer checking.
            yield env.timeout(1)
