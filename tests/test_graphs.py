import pytest  # noqa: F401
import project  # on import will print something from __init__ file # noqa: F401
import project.library.graphs as graphs
import networkx as nx


def setup_module(module):
    pass


def teardown_module(module):
    pass


def test_labeled_two_cycles_graph_test_1(tmp_path):
    tmp_path = tmp_path / "two_cycles.dot"
    g1 = graphs.labeled_two_cycles_graph_to_dot(3, 4, filename=tmp_path)

    assert isinstance(g1, nx.MultiDiGraph)
    assert g1.number_of_nodes() == 8
    assert g1.number_of_edges() == 9
    assert tmp_path.exists()

    g2 = nx.nx_pydot.read_dot(tmp_path)

    assert g2.number_of_nodes() == 8
    assert g2.number_of_edges() == 9
    assert graphs.get_unique_labels(g2) == {"a", "b"}


def test_labeled_two_cycles_graph_test_2(tmp_path):
    tmp_path = tmp_path / "two_cycles.dot"
    g = graphs.labeled_two_cycles_graph_to_dot(5, 15, filename=tmp_path)

    assert isinstance(g, nx.MultiDiGraph)
    assert g.number_of_nodes() == 21
    assert g.number_of_edges() == 22
    assert tmp_path.exists()

    g2 = nx.nx_pydot.read_dot(tmp_path)

    assert g2.number_of_nodes() == 21
    assert g2.number_of_edges() == 22
    assert graphs.get_unique_labels(g2) == {"a", "b"}


# You need internet access to run these tests


def test_info_wc():
    expected_v = 332
    expected_e = 269
    expected_labels = {"a", "d"}
    v, e, labels = graphs.graph_info_from_name("wc")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_generations():
    expected_v = 129
    expected_e = 273
    expected_labels = {
        "inverseOf",
        "equivalentClass",
        "hasChild",
        "hasSex",
        "sameAs",
        "oneOf",
        "hasSibling",
        "type",
        "hasValue",
        "onProperty",
        "versionInfo",
        "rest",
        "intersectionOf",
        "range",
        "someValuesFrom",
        "hasParent",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("generations")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_travel():
    expected_v = 131
    expected_e = 277
    expected_labels = {
        "equivalentClass",
        "disjointWith",
        "hasAccommodation",
        "subClassOf",
        "rest",
        "minCardinality",
        "complementOf",
        "unionOf",
        "type",
        "oneOf",
        "comment",
        "hasPart",
        "inverseOf",
        "hasValue",
        "onProperty",
        "versionInfo",
        "domain",
        "differentFrom",
        "intersectionOf",
        "range",
        "someValuesFrom",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("travel")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_univ():
    expected_v = 179
    expected_e = 293
    expected_labels = {
        "inverseOf",
        "comment",
        "subPropertyOf",
        "rest",
        "type",
        "onProperty",
        "subClassOf",
        "label",
        "versionInfo",
        "domain",
        "intersectionOf",
        "range",
        "someValuesFrom",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("univ")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_atom():
    expected_v = 291
    expected_e = 425
    expected_labels = {
        "language",
        "date",
        "publisher",
        "creator",
        "subPropertyOf",
        "seeAlso",
        "imports",
        "type",
        "versionInfo",
        "subClassOf",
        "label",
        "comment",
        "domain",
        "format",
        "range",
        "description",
        "title",
    }
    v, e, labels = graphs.graph_info_from_name("atom")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_biomedical():
    expected_v = 341
    expected_e = 459
    expected_labels = {
        "language",
        "publisher",
        "creator",
        "type",
        "versionInfo",
        "subClassOf",
        "label",
        "comment",
        "description",
        "title",
    }
    v, e, labels = graphs.graph_info_from_name("biomedical")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels
