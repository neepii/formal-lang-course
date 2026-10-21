from typing import Set, Tuple, List, Iterable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex
from collections import deque
import networkx as nx
import scipy.sparse as sp
import pyformlang.cfg
from project.library.automata import graph_to_nfa
from pyformlang.cfg import CFG, Production, Terminal, Variable


def cfg_to_weak_normal_form(cfg: pyformlang.cfg.CFG) -> pyformlang.cfg.CFG:
    sym_counter = 0
    prefix_new_nonterminals = "new_nonterminal_"

    cfg = cfg.eliminate_unit_productions()

    existing_variables = set(cfg.variables)

    def fresh_variable() -> Variable:
        nonlocal sym_counter
        while True:
            sym_counter += 1
            var = Variable(prefix_new_nonterminals + str(sym_counter))
            if var not in existing_variables:
                return var

    productions = set()
    terminal_to_var = {}

    for production in cfg.productions:
        body = production.body

        if len(body) <= 1:
            productions.add(production)
            continue

        new_body = []
        for symbol in body:
            if isinstance(symbol, Terminal):
                if symbol not in terminal_to_var:
                    terminal_to_var[symbol] = fresh_variable()
                new_body.append(terminal_to_var[symbol])
            else:
                new_body.append(symbol)

        if len(new_body) == 2:
            productions.add(Production(production.head, new_body))
            continue

        head = production.head
        for i in range(len(new_body) - 2):
            var = fresh_variable()
            productions.add(Production(head, [new_body[i], var]))
            head = var
        productions.add(Production(head, [new_body[-2], new_body[-1]]))

    for terminal, var in terminal_to_var.items():
        productions.add(Production(var, [terminal]))

    return CFG(start_symbol=cfg.start_symbol, productions=productions)


def hellings_based_cfpq(
    cfg: pyformlang.cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: set[int] = None,
    final_nodes: set[int] = None,
) -> set[tuple[int, int]]:
    """
    Hellings, 2014
    """
    wcnf = cfg_to_weak_normal_form(cfg)

    nodes = set(graph.nodes())
    if start_nodes is None:
        start_nodes = nodes
    if final_nodes is None:
        final_nodes = nodes

    epsilon_heads = []
    terminal_heads = {}
    left_index = {}
    right_index = {}

    for prod in wcnf.productions:
        head, body = prod.head, prod.body
        if len(body) == 0:
            epsilon_heads.append(head)
        elif len(body) == 1:
            terminal_heads.setdefault(body[0], []).append(head)
        else:
            left, right = body[0], body[1]
            left_index.setdefault(left, set()).add((head, right))
            right_index.setdefault(right, set()).add((head, left))

    reachable = set()
    by_start = {}
    by_end = {}
    worklist = deque()

    def add(u, N, v):
        if (u, N, v) not in reachable:
            reachable.add((u, N, v))
            by_start.setdefault((u, N), set()).add(v)
            by_end.setdefault((v, N), set()).add(u)
            worklist.append((u, N, v))

    for u, v, data in graph.edges(data=True):
        label = data.get("label")
        if label is None:
            continue
        for head in terminal_heads.get(Terminal(label), ()):
            add(u, head, v)

    for head in epsilon_heads:
        for u in nodes:
            add(u, head, u)

    while worklist:
        u, N, v = worklist.popleft()

        for head, R in left_index.get(N, set()):
            for w in list(by_start.get((v, R), ())):
                add(u, head, w)

        for head, L in right_index.get(N, set()):
            for w in list(by_end.get((u, L), ())):
                add(w, head, v)

    start_symbol = wcnf.start_symbol
    result = set()
    for u in start_nodes:
        for v in final_nodes:
            if (u, start_symbol, v) in reachable:
                result.add((u, v))

    return result
