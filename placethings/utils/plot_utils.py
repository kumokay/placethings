from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import networkx as nx
from matplotlib import pyplot as plt


def show_plot(graph, with_edge=True, which_edge_label=None):
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(
        graph,
        pos=pos,
        nodelist=None,
        node_size=300,
        node_color='r',
        node_shape='o',
    )
    nx.draw_networkx_labels(
        graph,
        pos=pos,
        labels=None,
        font_size=12,
        font_color='k',
        font_family='sans-serif',
        font_weight='normal',
    )
    if with_edge:
        nx.draw_networkx_edges(
            graph,
            pos=pos,
            edgelist=None,
            width=1.0,
            edge_color='k',
            style='solid',
        )
        if not which_edge_label:
            edge_labels = {}
        else:
            edge_labels = {
                (src, dst): attr[which_edge_label]
                for src, dst, attr in graph.edges(data=True)
            }
        nx.draw_networkx_edge_labels(
            graph,
            pos=pos,
            edge_labels=edge_labels,
            label_pos=0.5,
            font_size=10,
            font_color='k',
            font_family='sans-serif',
            font_weight='normal',
        )
    plt.show(graph)
