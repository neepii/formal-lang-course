import pytest  # noqa: F401
import project  # on import will print something from __init__ file # noqa: F401
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex
import project.library.automata as automata
import pyformlang as pfl
import networkx as nx
from typing import List


def setup_module(module):
    pass


def teardown_module(module):
    pass


def _invariant_regex_to_dfa(regex_to_test: str, xs: List[str]):
    dfa = automata.regex_to_dfa(regex_to_test)
    regex = Regex(regex_to_test)

    for x in xs:
        assert regex.accepts(x) == dfa.accepts(x)


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


# def test_graph_to_nfa():
