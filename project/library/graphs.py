import cfpq_data
from pathlib import Path
from typing import Any, Iterable, Tuple, Union, Set
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


def labeled_two_cycles_graph_to_dot(
    n: Union[int, Iterable[Any]],
    m: Union[int, Iterable[Any]],
    common_node: Any = 0,
    labels: Tuple[str, str] = ("a", "b"),
    filename: Union[str, Path, None] = None,
) -> nx.MultiDiGraph:
    graph = cfpq_data.labeled_two_cycles_graph(
        n,
        m,
        common_node=common_node,
        labels=labels,
    )

    if filename is not None:
        pydot_graph = nx.nx_pydot.to_pydot(graph)
        pydot_graph.write_raw(str(filename))

    return graph
