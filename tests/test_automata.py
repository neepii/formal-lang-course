import pytest  # noqa: F401
import project  # on import will print something from __init__ file # noqa: F401
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import Symbol
import project.library.automata as automata
import project.library.graphs as graphs
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


def test_graph_to_nfa_with_only_final_states():
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


def test_adjacency_matrix_fa_accepts_dfa():
    fa = automata.AdjacencyMatrixFA(automata.regex_to_dfa("a b*"))
    accepted = [["a"], ["a", "b"], ["a", "b", "b", "b"]]
    rejected = [[], ["b"], ["a", "a"], ["c"], ["a", "b", "c"]]

    for word in accepted:
        assert fa.accepts([Symbol(x) for x in word]) is True
        assert fa.accepts(word) is True
    for word in rejected:
        assert fa.accepts([Symbol(x) for x in word]) is False
        assert fa.accepts(word) is False


def test_adjacency_matrix_fa_accepts_nfa_graph():
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(range(2))
    graph.add_edge(0, 1, label="a")
    graph.add_edge(1, 1, label="b")

    fa = automata.AdjacencyMatrixFA(automata.graph_to_nfa(graph, {0}, {1}))
    regex = Regex("a b*")
    words = [
        "",
        "a",
        "aa",
        "ab",
        "abb",
        "b",
        "abbbbbbbb",
        "aaaaaa",
        "bbbbb",
        "aabaababaaab",
    ]

    for word in words:
        assert fa.accepts(list(word)) == regex.accepts(word)
        assert fa.accepts([Symbol(c) for c in word]) == regex.accepts(word)


def test_adjacency_matrix_fa_accepts_empty_word():
    fa = automata.AdjacencyMatrixFA(automata.regex_to_dfa("a*"))
    assert fa.accepts([]) is True
    assert fa.accepts("") is True
    assert fa.accepts(["a", "a", "a"]) is True
    assert fa.accepts(["b"]) is False


def test_adjacency_matrix_fa_is_empty_empty_intersection():
    fa = automata.intersect_automata(
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("a")),
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("b")),
    )
    assert fa.is_empty() is True


def test_adjacency_matrix_fa_is_empty_nonempty():
    fa = automata.AdjacencyMatrixFA(automata.regex_to_dfa("a b*"))
    assert fa.is_empty() is False


def test_adjacency_matrix_fa_is_empty_empty_word_and_disconnected_graph():
    fa = automata.AdjacencyMatrixFA(automata.regex_to_dfa("a*"))
    assert fa.is_empty() is False

    graph = nx.MultiDiGraph()
    graph.add_nodes_from([0, 1])
    graph.add_edge(0, 0, label="a")
    nfa_fa = automata.AdjacencyMatrixFA(automata.graph_to_nfa(graph, {0}, {1}))
    assert nfa_fa.is_empty() is True


def test_intersect_automata_matches_regex_intersection():
    fa = automata.intersect_automata(
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("a* b")),
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("a b*")),
    )
    r1 = Regex("a* b")
    r2 = Regex("a b*")
    words = ["", "a", "b", "ab", "aab", "abb", "aabb", "ba", "aabbb"]

    for word in words:
        assert fa.accepts(list(word)) == (r1.accepts(word) and r2.accepts(word))


def test_intersect_automata_matches_regex_intersection_star():
    fa = automata.intersect_automata(
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("a*")),
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("(a|b)*")),
    )
    r1 = Regex("a*")
    r2 = Regex("(a|b)*")
    words = ["", "a", "aa", "b", "ab", "ba"]

    for word in words:
        assert fa.accepts(list(word)) == (r1.accepts(word) and r2.accepts(word))


def test_intersect_automata_empty_intersection():
    fa = automata.intersect_automata(
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("a")),
        automata.AdjacencyMatrixFA(automata.regex_to_dfa("b")),
    )
    assert fa.is_empty() is True
    assert fa.accepts(["a"]) is False
    assert fa.accepts(["b"]) is False


def test_tensor_based_rpq_single_edge():
    graph = nx.MultiDiGraph()
    graph.add_nodes_from([0, 1])
    graph.add_edge(0, 1, label="a")

    assert automata.tensor_based_rpq("a", graph, {0}, {1}) == {(0, 1)}
    assert automata.tensor_based_rpq("a", graph, {0, 1}, {0, 1}) == {(0, 1)}


def test_tensor_based_rpq_path():
    graph = nx.MultiDiGraph()
    graph.add_nodes_from([0, 1, 2])
    graph.add_edge(0, 1, label="a")
    graph.add_edge(1, 2, label="b")

    assert automata.tensor_based_rpq("a b", graph, {0, 1, 2}, {0, 1, 2}) == {(0, 2)}
    assert automata.tensor_based_rpq("a", graph, {0, 1, 2}, {0, 1, 2}) == {(0, 1)}


def test_tensor_based_rpq_star():
    graph = nx.MultiDiGraph()
    graph.add_nodes_from([0, 1, 2])
    graph.add_edge(0, 1, label="a")
    graph.add_edge(1, 2, label="a")
    graph.add_edge(1, 1, label="b")

    expected = {(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)}
    assert automata.tensor_based_rpq("a*", graph, {0, 1, 2}, {0, 1, 2}) == expected
    assert automata.tensor_based_rpq("(a|b)*", graph, {0, 1, 2}, {0, 1, 2}) == expected
