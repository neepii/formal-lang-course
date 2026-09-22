from typing import Set, Tuple
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex
import pyformlang as pfl
import networkx as nx


def regex_to_dfa(regex: str) -> DeterministicFiniteAutomaton:
    regex = Regex(regex)
    nfa: NondeterministicFiniteAutomaton = regex.to_epsilon_nfa()
    dfa: DeterministicFiniteAutomaton = nfa.to_deterministic().minimize()
    return dfa


def graph_to_nfa(
    graph: nx.MultiDiGraph, start_states: Set[int], final_states: Set[int]
) -> NondeterministicFiniteAutomaton:

    nfa = NondeterministicFiniteAutomaton()
    if start_states is None and final_states is None:
        for state in graph:
            number = int(state)
            nfa.add_start_state(number)
            nfa.add_final_state(number)
    else:
        if start_states is not None:
            for start_state in start_states:
                nfa.add_start_state(start_state)
        if final_states is not None:
            for final_state in final_states:
                nfa.add_final_state(final_state)

    delta: List[Tuple[int, str, int]] = []
    for u, v, data in graph.edges(data=True):
        label: str = data.get("label")
        if label is not None:
            delta.append((State(int(u)), Symbol(str(label)), State(int(v))))

    nfa.add_transitions(delta)
    return nfa
