import pytest  # noqa: F401
import project  # on import will print something from __init__ file # noqa: F401
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex
import project.library.automata as automata
import project.library.graphs as graphs
import pyformlang as pfl
import networkx as nx
import cfpq_data
from typing import List, Set


def setup_module(module):
    pass


def teardown_module(module):
    pass


def _invariant_regex_to_dfa(regex_to_test: str, xs: List[str]):
    dfa = automata.regex_to_dfa(regex_to_test)
    regex = Regex(regex_to_test)

    for x in xs:
        assert regex.accepts(x) == dfa.accepts(x)


def _invariant_graph_to_nfa(
    graph: nx.MultiDiGraph, start_states: Set[int], final_states: Set[int]
):
    nfa = automata.graph_to_nfa(graph, start_states, final_states)
    for u, transitions in nfa.to_dict().items():
        for symbol, target_states in transitions.items():
            for v in target_states:
                assert any(
                    str(edge_data.get("label")) == str(symbol)
                    for edge_data in graph.get_edge_data(u, v).values()
                )


def test_regex_to_dfa_binary_alphabet():
    xs = [
        "a",
        "aa",
        "ab",
        "abb",
        "abbbbbbbb",
        "aaaaaa",
        "bbbbb",
        "aabaababaaab",
        "b",
        "",
    ]
    _invariant_regex_to_dfa("ab*", xs)
    _invariant_regex_to_dfa("ab|ba", xs)
    _invariant_regex_to_dfa("ab|(ab)*", xs)
    _invariant_regex_to_dfa("a*", xs)
    _invariant_regex_to_dfa("aa*", xs)
    _invariant_regex_to_dfa("ab(a*bbb)*", xs)


def test_regex_to_dfa_ternary_alphabet():
    xs = [
        "abc",
        "aabcbaccc",
        "aaaaaaaaa",
        "ababcbcbcbcababbbbbbbbb",
        "aaaaabbbbbbcccccc",
        "aaabbbbbbabbbbbcccccc",
        "",
    ]
    _invariant_regex_to_dfa("a*b*c*", xs)
    _invariant_regex_to_dfa("(a(b|c)|b(a|c)|c(a|b))* (a|b|c|$)", xs)
    _invariant_regex_to_dfa("(b|c|ab)*", xs)
    _invariant_regex_to_dfa("(a|b)* (c|b)*", xs)
    _invariant_regex_to_dfa(
        "((b|c)* a (a* b a)* a* (bb|c))* ((b|c)* | (b|c)* a (a* b a)* a* ($|b))", xs
    )


def test_graph_to_nfa_basic():
    graph = nx.MultiDiGraph()

    graph.add_nodes_from(range(2))
    graph.add_edge(0, 1, label="a")

    _invariant_graph_to_nfa(graph, {0}, {1})


def test_graph_to_nfa_two_cycles():
    graph = graphs.labeled_two_cycles_graph_to_dot(10, 10)
    _invariant_graph_to_nfa(graph, {2, 3, 14, 15}, {0})


def test_graph_to_nfa_with_nones():
    graph = nx.MultiDiGraph()
    num_of_nodes = 10
    graph.add_nodes_from(range(num_of_nodes))
    for i in range(num_of_nodes - 1):
        graph.add_edge(i, i + 1, label="a")

    nfa = automata.graph_to_nfa(graph, None, None)
    for state in nfa.states:
        assert state in nfa.start_states
        assert state in nfa.final_states


def test_graph_to_nfa_with_only_start_states():
    graph = nx.MultiDiGraph()
    num_of_nodes = 10
    graph.add_nodes_from(range(num_of_nodes))
    for i in range(num_of_nodes - 1):
        graph.add_edge(i, i + 1, label="a")

    nfa = automata.graph_to_nfa(graph, {0}, None)
    for state in nfa.states:
        assert state not in nfa.final_states


def test_graph_to_nfa_with_only_start_states():
    graph = nx.MultiDiGraph()
    num_of_nodes = 10
    graph.add_nodes_from(range(num_of_nodes))
    for i in range(num_of_nodes - 1):
        graph.add_edge(i, i + 1, label="a")

    nfa = automata.graph_to_nfa(graph, None, {9})
    for state in nfa.states:
        assert state not in nfa.start_states


def test_graph_to_nfa_for_building_language():
    graph = nx.MultiDiGraph()

    graph.add_nodes_from(range(2))
    graph.add_edge(0, 1, label="a")
    graph.add_edge(1, 1, label="b")
    nfa = automata.graph_to_nfa(graph, {0}, {1})
    regex = Regex("a b*")
    xs = [
        "a",
        "aa",
        "ab",
        "abb",
        "abbbbbbbb",
        "aaaaaa",
        "bbbbb",
        "aabaababaaab",
        "b",
        "",
    ]

    for x in xs:
        assert regex.accepts(x) == nfa.accepts(x)


# You need internet access for this test
def test_graph_to_nfa_using_names():
    path = cfpq_data.download("wc")
    graph: nx.MultiDiGraph = cfpq_data.graph_from_csv(path)
    _invariant_graph_to_nfa(graph, {2, 3, 14, 15}, {0})
