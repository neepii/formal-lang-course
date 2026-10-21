from typing import Set, Tuple, List, Iterable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton
from pyformlang.finite_automaton import State
from pyformlang.finite_automaton import Symbol
from pyformlang.regular_expression import Regex
import networkx as nx
import scipy.sparse as sp
import pyformlang.cfg
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
    pass
