from typing import Set, Tuple, List
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex
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

    all_states: Set[int] = {int(state) for state in graph.nodes()}

    if start_states is None and final_states is None:
        start_states = all_states
        final_states = all_states
    else:
        if start_states is None:
            start_states = set()
        elif len(start_states) == 0:
            start_states = all_states

        if final_states is None:
            final_states = set()
        elif len(final_states) == 0:
            final_states = all_states

    for start_state in start_states:
        nfa.add_start_state(start_state)
    for final_state in final_states:
        nfa.add_final_state(final_state)

    delta: List[Tuple[int, str, int]] = []
    for u, v, data in graph.edges(data=True):
        label: str = data.get("label")
        if label is not None:
            delta.append((State(int(u)), Symbol(str(label)), State(int(v))))

    nfa.add_transitions(delta)
    return nfa
