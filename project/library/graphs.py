import cfpq_data
from pathlib import Path
from typing import Union, Set, Tuple
import networkx as nx


def graph_info_from_name(name: str) -> Tuple[int, int, Set[str]]:
    path = cfpq_data.download(name)
    return graph_info_from_path(path)


def graph_info_from_path(path: Union[str, Path]) -> Tuple[int, int, Set[str]]:
    graph: nx.MultiDiGraph = cfpq_data.graph_from_csv(path)

    num_vertices: int = graph.number_of_nodes()
    num_edges: int = graph.number_of_edges()

    unique_labels: Set[str] = set()
    for _u, _v, data in graph.edges(data=True):
        label = data.get("label")
        if label is not None:
            unique_labels.add(label)

    return num_vertices, num_edges, unique_labels
