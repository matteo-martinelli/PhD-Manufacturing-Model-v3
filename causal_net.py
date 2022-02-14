"""
causal_net.py: file where all the causal operations will be managed.

This file should become a class.
"""

# TO-do: transfer all on Colab. Eventually retry with The new CUDA env and paddlepaddle-gpu. -> Done
# To-do: test with GPU acceleration -> che pippa non va.
import time
import pandas

import tensorflow as tf
from tensorflow.python.client import device_lib

from causalnex.structure.notears import from_pandas
# from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE

import networkx

from IPython.display import Image


def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']


CSV_PATH = 'C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\Phd-Manufacturing-Model-v3\\logs\\' \
           'merged_logs.csv'


# print(tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None))
# print("List physical GPUs: ", tf.config.list_physical_devices('GPU'))


print("Available GPU: " + tf.test.gpu_device_name())
# print("Getting available GPUs: ", get_available_gpus())

data = pandas.read_csv(CSV_PATH, delimiter=',')

print(data.head(5))

print("Starting to infer the causal net from data.")

start_time = time.time()

structure_model = from_pandas(data)

print("--- %s minutes ---" % ((time.time() - start_time)/60))

print(networkx.draw(structure_model, with_labels=True))
# Image(visualize.draw(format('png')))

# networkx.drawing.nx_pydot.write_dot(structure_model, 'graph.dot')
