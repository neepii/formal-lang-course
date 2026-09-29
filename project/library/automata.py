from typing import Set, Tuple, List, Iterable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex
import networkx as nx
import scipy.sparse as sp


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


class AdjacencyMatrixFA:
    """Boolean adjacency-matrix representation of a finite automaton."""

    def __init__(self, automaton):
        self.states = sorted(automaton.states, key=lambda s: repr(s.value))
        self.state_to_index = {s: i for i, s in enumerate(self.states)}
        self.start_indices = {
            self.state_to_index[s] for s in automaton.start_states
        }
        self.final_indices = {
            self.state_to_index[s] for s in automaton.final_states
        }
        self.n = len(self.states)

        self.bool_matrices: dict = {}
        for sym in automaton.symbols:
            self.bool_matrices[sym.value] = sp.lil_matrix(
                (self.n, self.n), dtype=bool
            )

        for src, transitions in automaton.to_dict().items():
            i = self.state_to_index[src]
            for sym, target in transitions.items():
                j_indices = {target} if isinstance(target, State) else target
                for dst in j_indices:
                    j = self.state_to_index[dst]
                    self.bool_matrices[sym.value][i, j] = True

        for sym in automaton.symbols:
            self.bool_matrices[sym.value] = self.bool_matrices[
                sym.value
            ].tocsr()

    def accepts(self, word: Iterable[Symbol]) -> bool:
        word = [str(getattr(item, "value", item)) for item in word]

        rows = [0] * len(self.start_indices)
        cols = list(self.start_indices)
        data = [True] * len(self.start_indices)
        n = self.n
        vec = sp.csr_matrix((data, (rows, cols)), shape=(1, n), dtype=bool)

        for s in word:
            if s not in self.bool_matrices:
                return False
            vec = vec @ self.bool_matrices[s]
            vec.eliminate_zeros()

        return not self.final_indices.isdisjoint(set(vec.indices))

    def _transitive_closure(self) -> sp.csr_matrix:
        m_any = sp.csr_matrix((self.n, self.n), dtype=bool)
        for matrix in self.bool_matrices.values():
            m_any = m_any + matrix
        m_any = m_any.astype(bool)
        m_any.eliminate_zeros()

        closure = (
            sp.identity(self.n, dtype=bool, format="csr") + m_any
        ).astype(bool)
        closure.eliminate_zeros()

        for _ in range(self.n.bit_length() + 1):
            closure = (closure @ closure).astype(bool)
            closure.eliminate_zeros()

        return closure

    def is_empty(self) -> bool:
        closure = self._transitive_closure()
        return all(
            not closure[i, j]
            for i in self.start_indices
            for j in self.final_indices
        )

    @classmethod
    def _from_components(
        cls, n, start_indices, final_indices, bool_matrices
    ) -> "AdjacencyMatrixFA":
        obj = cls.__new__(cls)
        obj.n = n
        obj.start_indices = set(start_indices)
        obj.final_indices = set(final_indices)
        obj.bool_matrices = bool_matrices
        obj.states = None
        obj.state_to_index = None
        return obj


def intersect_automata(
    automaton1: AdjacencyMatrixFA, automaton2: AdjacencyMatrixFA
) -> AdjacencyMatrixFA:
    n1, n2 = automaton1.n, automaton2.n
    symbols = set(automaton1.bool_matrices) | set(automaton2.bool_matrices)

    bool_matrices = {}
    for s in symbols:
        m1 = automaton1.bool_matrices.get(
            s, sp.csr_matrix((n1, n1), dtype=bool)
        )
        m2 = automaton2.bool_matrices.get(
            s, sp.csr_matrix((n2, n2), dtype=bool)
        )
        bool_matrices[s] = sp.kron(m1, m2).astype(bool).tocsr()

    start_indices = {
        i1 * n2 + i2
        for i1 in automaton1.start_indices
        for i2 in automaton2.start_indices
    }
    final_indices = {
        i1 * n2 + i2
        for i1 in automaton1.final_indices
        for i2 in automaton2.final_indices
    }

    return AdjacencyMatrixFA._from_components(
        n1 * n2, start_indices, final_indices, bool_matrices
    )


def tensor_based_rpq(
    regex: str,
    graph: nx.MultiDiGraph,
    start_nodes: set[int],
    final_nodes: set[int],
) -> set[tuple[int, int]]:
    dfa = regex_to_dfa(regex)
    nfa = graph_to_nfa(graph, start_nodes, final_nodes)

    fa_dfa = AdjacencyMatrixFA(dfa)
    fa_nfa = AdjacencyMatrixFA(nfa)

    intersection = intersect_automata(fa_dfa, fa_nfa)
    closure = intersection._transitive_closure()

    node_to_index = {
        int(s.value): idx for s, idx in fa_nfa.state_to_index.items()
    }
    n2 = fa_nfa.n
    dfa_start = next(iter(fa_dfa.start_indices))

    result = set()
    for i in start_nodes:
        src = dfa_start * n2 + node_to_index[i]
        for j in final_nodes:
            dst_base = node_to_index[j]
            for f in fa_dfa.final_indices:
                dst = f * n2 + dst_base
                if closure[src, dst]:
                    result.add((i, j))
                    break

    return result
