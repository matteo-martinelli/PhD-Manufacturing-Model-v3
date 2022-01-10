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
        self.process_name = process_name
        self.input_containers = input_containers    # This is passed as a list
        self.output_container = output_container

        # self.process = env.process(self.material_transfer())
        # self.env.process(self.material_transfer(env))
        self.material_transfer = env.process(self.material_transfer(self.env))

    #  Function describing the machine process.
    def material_transfer(self, env):
        yield env.timeout(0)

        while True:
            # Get all the material in the input container
            for element in range(len(self.input_containers)):
                self.input_containers[element].get(1)

            # Once all the material has been taken, put one element in the output container
            self.output_container.put(1)
            # print('here')
            yield env.timeout(1)
