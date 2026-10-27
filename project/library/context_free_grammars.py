from typing import Set
from collections import deque
import networkx as nx
import pyformlang.cfg
from pyformlang.cfg import CFG, Production, Terminal, Variable
import scipy.sparse as sp


def cfg_to_weak_normal_form(cfg: pyformlang.cfg.CFG) -> pyformlang.cfg.CFG:
    sym_counter = 0
    prefix_new_nonterminals = "new_nonterminal_"

    cfg = cfg.eliminate_unit_productions()
    cfg = cfg.remove_useless_symbols()

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


def matrix_based_cfpq(
    cfg: pyformlang.cfg.CFG,
    graph: nx.DiGraph,
    start_nodes: Set[int] = None,
    final_nodes: Set[int] = None,
) -> set[tuple[int, int]]:
    wcnf = cfg_to_weak_normal_form(cfg)

    nodes = sorted(graph.nodes(), key=repr)
    node_to_index = {node: index for index, node in enumerate(nodes)}
    n = len(nodes)

    variables = set(wcnf.variables) | {wcnf.start_symbol}
    decomposition = {var: sp.csr_matrix((n, n), dtype=bool) for var in variables}

    terminal_heads = {}
    unit_index = {}
    left_index = {}
    right_index = {}

    for production in wcnf.productions:
        head, body = production.head, production.body
        if len(body) == 0:
            decomposition[head] = sp.identity(n, dtype=bool, format="csr")
        elif len(body) == 1 and isinstance(body[0], Terminal):
            terminal_heads.setdefault(str(body[0].value), []).append(head)
        elif len(body) == 1:
            unit_index.setdefault(body[0], []).append(head)
        else:
            left, right = body[0], body[1]
            left_index.setdefault(left, []).append((head, right))
            right_index.setdefault(right, []).append((head, left))

    edge_triples = {}
    for u, v, data in graph.edges(data=True):
        label = data.get("label")
        if label is None:
            continue
        heads = terminal_heads.get(str(label))
        if not heads:
            continue
        i, j = node_to_index[u], node_to_index[v]
        for head in heads:
            rows, cols = edge_triples.setdefault(head, ([], []))
            rows.append(i)
            cols.append(j)

    for head, (rows, cols) in edge_triples.items():
        data = [True] * len(rows)
        edges = sp.csr_matrix((data, (rows, cols)), shape=(n, n), dtype=bool)
        decomposition[head] = (decomposition[head] + edges).astype(bool)

    queue = deque(var for var, matrix in decomposition.items() if matrix.nnz)
    in_queue = set(queue)

    while queue:
        var = queue.popleft()
        in_queue.discard(var)

        additions = {}
        for head in unit_index.get(var, ()):
            additions[head] = decomposition[var]

        for head, other in left_index.get(var, ()):
            additions[head] = (
                additions.get(head, sp.csr_matrix((n, n), dtype=bool))
                + decomposition[var] @ decomposition[other]
            )

        for head, other in right_index.get(var, ()):
            additions[head] = (
                additions.get(head, sp.csr_matrix((n, n), dtype=bool))
                + decomposition[other] @ decomposition[var]
            )

        for head, addition in additions.items():
            merged = (decomposition[head] + addition).astype(bool)
            merged.eliminate_zeros()
            if merged.nnz != decomposition[head].nnz:
                decomposition[head] = merged
                if head not in in_queue:
                    in_queue.add(head)
                    queue.append(head)

    all_nodes = set(nodes)
    if start_nodes is None:
        start_nodes = all_nodes
    if final_nodes is None:
        final_nodes = all_nodes

    reachability = decomposition[wcnf.start_symbol]
    return {
        (u, v)
        for u in start_nodes
        for v in final_nodes
        if u in node_to_index
        and v in node_to_index
        and reachability[node_to_index[u], node_to_index[v]]
    }
