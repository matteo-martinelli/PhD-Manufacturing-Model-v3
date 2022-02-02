"""
causal_net.py: file where all the causal operations will be managed.

This file should become a class.
"""

import pandas
from causalnex.structure.notears import from_pandas
from causalnex.plots import plot_structure, NODE_STYLE, EDGE_STYLE
from IPython.display import Image


CSV_PATH = 'C:\\Users\\wmatt\\Desktop\\Workspace\\Projects\\Phd-Projects\\Phd-Manufacturing-Model-v3\\logs\\' \
           'merged_logs.csv'

data = pandas.read_csv(CSV_PATH, delimiter=',')
print(data.head(5))

structure_model = from_pandas(data)

visualize = plot_structure(
    structure_model,
    graph_attributes={'scale': '0.5'},
    all_node_attributes=NODE_STYLE.WEAK,
    all_edge_attributes=EDGE_STYLE.WEAK,
    prog='fdp')

Image(visualize.draw(format('png')))
