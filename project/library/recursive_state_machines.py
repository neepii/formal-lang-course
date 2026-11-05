import networkx as nx
import scipy.sparse as sp
from pyformlang.cfg import CFG
from pyformlang.finite_automaton import (
    NondeterministicFiniteAutomaton,
    State,
    Symbol,
)
from pyformlang.rsa import RecursiveAutomaton

from .automata import AdjacencyMatrixFA


def cfg_to_rsm(cfg: CFG) -> RecursiveAutomaton:
    start_symbol = Symbol(str(cfg.start_symbol.value))
    return RecursiveAutomaton.from_text(cfg.to_text(), start_symbol=start_symbol)


def ebnf_to_rsm(ebnf: str) -> RecursiveAutomaton:
    return RecursiveAutomaton.from_text(ebnf)


def _rsm_to_adjacency_fa(rsm: RecursiveAutomaton):
    merged = NondeterministicFiniteAutomaton()
    start_states = {}
    final_states = {}
    for label, box in rsm.boxes.items():
        label_str = str(label.value)
        start_states[label_str] = {
            State((label_str, repr(state.value))) for state in box.start_state
        }
        final_states[label_str] = {
            State((label_str, repr(state.value))) for state in box.final_states
        }
        for state in start_states[label_str]:
            merged.add_start_state(state)
        for state in final_states[label_str]:
            merged.add_final_state(state)
        for src, transitions in box.dfa.to_dict().items():
            src_state = State((label_str, repr(src.value)))
            for sym, targets in transitions.items():
                if isinstance(targets, State):
                    targets = {targets}
                for dst in targets:
                    merged.add_transition(
                        src_state, sym, State((label_str, repr(dst.value)))
                    )
    return AdjacencyMatrixFA(merged), start_states, final_states


class FourRussians:
    def __init__(self, n: int):
        self.n = n
        self.k = max(1, min(8, n.bit_length()))
        self.chunk_mask = (1 << self.k) - 1
        self.full_mask = (1 << n) - 1
        self._table = {
            (a, b): a & b for a in range(1 << self.k) for b in range(1 << self.k)
        }

    def hadamard_and(self, a: int, b: int) -> int:
        result = 0
        for shift in range(0, self.n, self.k):
            chunk_a = (a >> shift) & self.chunk_mask
            chunk_b = (b >> shift) & self.chunk_mask
            result |= self._table[(chunk_a, chunk_b)] << shift
        return result

    def hadamard_and_not(self, a: int, b: int) -> int:
        return self.hadamard_and(a, b ^ self.full_mask)


class _BitMatrixTransitiveClosure:
    def __init__(self, n: int):
        self.n = n
        self.four_russians = FourRussians(n)
        self.rows = [(1 << u) for u in range(n)]
        self.cols = [(1 << u) for u in range(n)]

    def add_edge(self, i: int, j: int, new_entries: list):
        if (self.rows[i] >> j) & 1:
            return
        candidates = self.four_russians.hadamard_and_not(self.cols[i], self.cols[j])
        self.rows[i] |= 1 << j
        self.cols[j] |= 1 << i
        new_entries.append((i, j))
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            u = bit.bit_length() - 1
            new_successors = self.four_russians.hadamard_and_not(
                self.rows[j], self.rows[u]
            )
            while new_successors:
                v_bit = new_successors & -new_successors
                new_successors ^= v_bit
                v = v_bit.bit_length() - 1
                self.rows[u] |= v_bit
                self.cols[v] |= 1 << u
                new_entries.append((u, v))


def tensor_based_cfpq(
    rsm: RecursiveAutomaton,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    rsm_fa, start_states, final_states = _rsm_to_adjacency_fa(rsm)
    m1 = rsm_fa.bool_matrices
    dim = rsm_fa.n

    nodes = sorted(graph.nodes(), key=repr)
    node_to_index = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    nonterminals = {str(label.value) for label in rsm.boxes.keys()}
    m2 = {label: sp.lil_matrix((n, n), dtype=bool) for label in nonterminals}
    a2 = {label: sp.lil_matrix((n, n), dtype=bool) for label in nonterminals}

    for u, v, data in graph.edges(data=True):
        edge_label = data.get("label")
        if edge_label is None:
            continue
        edge_label = str(edge_label)
        if edge_label not in m2:
            m2[edge_label] = sp.lil_matrix((n, n), dtype=bool)
            a2[edge_label] = sp.lil_matrix((n, n), dtype=bool)
        m2[edge_label][node_to_index[u], node_to_index[v]] = True
        a2[edge_label][node_to_index[u], node_to_index[v]] = True

    identity = sp.identity(n, dtype=bool, format="csr")
    for label_str in nonterminals:
        if start_states[label_str] & final_states[label_str]:
            m2[label_str] = m2[label_str] + identity
            a2[label_str] = a2[label_str] + identity

    start_nonterminals = {}
    final_nonterminals = {}
    for label_str, states in start_states.items():
        for state in states:
            start_nonterminals.setdefault(rsm_fa.state_to_index[state], set()).add(
                label_str
            )
    for label_str, states in final_states.items():
        for state in states:
            final_nonterminals.setdefault(rsm_fa.state_to_index[state], set()).add(
                label_str
            )

    def nonterminals_between(s: int, f: int) -> set[str]:
        return start_nonterminals.get(s, set()) & final_nonterminals.get(f, set())

    total = dim * n
    m3 = sp.csr_matrix((total, total), dtype=bool)
    closure = _BitMatrixTransitiveClosure(total)

    fixpoint_not_reached = True
    while fixpoint_not_reached:
        fixpoint_not_reached = False
        m3_prime = sp.csr_matrix((total, total), dtype=bool)
        for label, added in a2.items():
            if added.nnz == 0 or label not in m1:
                continue
            m3_prime = m3_prime + sp.kron(m1[label], added.tocsr(), format="csr")
        m3_prime = m3_prime.astype(bool)
        m3_prime.eliminate_zeros()

        if m3_prime.nnz == 0:
            break

        m3 = (m3 + m3_prime).astype(bool)
        m3.eliminate_zeros()

        for label in a2:
            a2[label] = sp.lil_matrix((n, n), dtype=bool)

        new_entries = []
        m3_prime = m3_prime.tocoo()
        for i, j in zip(m3_prime.row, m3_prime.col):
            closure.add_edge(int(i), int(j), new_entries)

        for i, j in new_entries:
            s, x = divmod(i, n)
            f, y = divmod(j, n)
            for label_str in nonterminals_between(s, f):
                m2[label_str][x, y] = True
                a2[label_str][x, y] = True
                fixpoint_not_reached = True

    start_label = str(rsm.initial_label.value)
    reachability = m2.get(start_label)
    if reachability is None:
        return set()

    all_nodes = set(nodes)
    if start_nodes is None:
        start_nodes = all_nodes
    if final_nodes is None:
        final_nodes = all_nodes

    return {
        (u, v)
        for u in start_nodes
        for v in final_nodes
        if u in node_to_index
        and v in node_to_index
        and reachability[node_to_index[u], node_to_index[v]]
    }
