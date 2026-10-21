import pytest  # noqa: F401
import project  # noqa: F401
import project.library.context_free_grammars as cfgs
from pyformlang.cfg import CFG, Terminal, Variable


def setup_module(module):
    pass


def teardown_module(module):
    pass


def _is_wcnf(cfg: CFG) -> bool:
    """Every production is N -> ε, N -> t, or N -> A B."""
    for prod in cfg.productions:
        body = prod.body
        if len(body) == 0:
            continue
        if len(body) == 1 and isinstance(body[0], Terminal):
            continue
        if len(body) == 2 and all(isinstance(sym, Variable) for sym in body):
            continue
        return False
    return True


def _has_unit_productions(cfg: CFG) -> bool:
    return any(
        len(prod.body) == 1 and isinstance(prod.body[0], Variable)
        for prod in cfg.productions
    )


def _words(cfg: CFG, max_length: int) -> set:
    """Language of the grammar restricted to words up to max_length."""
    return {
        "".join(str(sym.value) for sym in word) for word in cfg.get_words(max_length)
    }


def test_wcnf_productions_have_weak_normal_form():
    grammars = [
        "S -> a S b S | epsilon",
        "S -> S S | a",
        "S -> a b c",
        "S -> A\nA -> a A | a",
        "S -> a A b | B\nA -> a\nB -> b",
    ]
    for text in grammars:
        wcnf = cfgs.cfg_to_weak_normal_form(CFG.from_text(text))
        assert _is_wcnf(wcnf), text


def test_wcnf_preserves_language():
    grammars = [
        "S -> a S b S | epsilon",
        "S -> S S | a | epsilon",
        "S -> a b c",
        "S -> A | b\nA -> a",
        "S -> a A\nA -> b",
    ]
    for text in grammars:
        cfg = CFG.from_text(text)
        wcnf = cfgs.cfg_to_weak_normal_form(cfg)
        assert _words(cfg, 6) == _words(wcnf, 6), text


def test_wcnf_eliminates_unit_productions():
    cfg = CFG.from_text("S -> A | b\nA -> a")
    wcnf = cfgs.cfg_to_weak_normal_form(cfg)
    assert not _has_unit_productions(wcnf)


def test_wcnf_keeps_epsilon_productions():
    cfg = CFG.from_text("S -> a | epsilon")
    wcnf = cfgs.cfg_to_weak_normal_form(cfg)
    assert any(len(prod.body) == 0 for prod in wcnf.productions)
    assert "" in _words(wcnf, 3)


def test_wcnf_preserves_start_symbol():
    cfg = CFG.from_text("S -> a")
    wcnf = cfgs.cfg_to_weak_normal_form(cfg)
    assert wcnf.start_symbol == cfg.start_symbol


def test_wcnf_splits_long_production():
    cfg = CFG.from_text("S -> a b c")
    wcnf = cfgs.cfg_to_weak_normal_form(cfg)
    assert _is_wcnf(wcnf)
    assert _words(wcnf, 4) == {"abc"}
