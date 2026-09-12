import pytest  # noqa: F401
import project  # on import will print something from __init__ file # noqa: F401
import project.library.graphs as graphs


def setup_module(module):
    pass


def teardown_module(module):
    pass


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


def test_info_bzip():
    expected_v = 632
    expected_e = 556
    expected_labels = {"d", "a"}
    v, e, labels = graphs.graph_info_from_name("bzip")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_foaf():
    expected_v = 256
    expected_e = 631
    expected_labels = {
        "isDefinedBy",
        "inverseOf",
        "equivalentClass",
        "disjointWith",
        "term_status",
        "equivalentProperty",
        "subPropertyOf",
        "type",
        "subClassOf",
        "label",
        "comment",
        "domain",
        "range",
        "description",
        "title",
    }
    v, e, labels = graphs.graph_info_from_name("foaf")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_people():
    expected_v = 337
    expected_e = 640
    expected_labels = {
        "equivalentClass",
        "drives",
        "service_number",
        "disjointWith",
        "subClassOf",
        "rest",
        "is_pet_of",
        "minCardinality",
        "complementOf",
        "unionOf",
        "type",
        "subPropertyOf",
        "allValuesFrom",
        "has_pet",
        "label",
        "comment",
        "inverseOf",
        "maxCardinality",
        "reads",
        "onProperty",
        "domain",
        "intersectionOf",
        "range",
        "someValuesFrom",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("people")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_pr():
    expected_v = 815
    expected_e = 692
    expected_labels = {"d", "a"}
    v, e, labels = graphs.graph_info_from_name("pr")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_funding():
    expected_v = 778
    expected_e = 1086
    expected_labels = {
        "contributor",
        "subClassOf",
        "rest",
        "unionOf",
        "type",
        "subPropertyOf",
        "rights",
        "creator",
        "imports",
        "seeAlso",
        "label",
        "comment",
        "title",
        "inverseOf",
        "date",
        "versionInfo",
        "domain",
        "range",
        "description",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("funding")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_ls():
    expected_v = 1687
    expected_e = 1453
    expected_labels = {"d", "a"}
    v, e, labels = graphs.graph_info_from_name("ls")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_wine():
    expected_v = 733
    expected_e = 1839
    expected_labels = {
        "locatedIn",
        "madeFromGrape",
        "hasBody",
        "disjointWith",
        "subClassOf",
        "rest",
        "yearValue",
        "distinctMembers",
        "priorVersion",
        "minCardinality",
        "hasColor",
        "unionOf",
        "type",
        "subPropertyOf",
        "cardinality",
        "hasMaker",
        "hasVintageYear",
        "allValuesFrom",
        "oneOf",
        "imports",
        "hasFlavor",
        "label",
        "comment",
        "hasSugar",
        "adjacentRegion",
        "inverseOf",
        "maxCardinality",
        "hasValue",
        "onProperty",
        "domain",
        "differentFrom",
        "intersectionOf",
        "range",
        "someValuesFrom",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("wine")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_pizza():
    expected_v = 671
    expected_e = 1980
    expected_labels = {
        "equivalentClass",
        "disjointWith",
        "subClassOf",
        "rest",
        "distinctMembers",
        "minCardinality",
        "complementOf",
        "unionOf",
        "type",
        "subPropertyOf",
        "allValuesFrom",
        "oneOf",
        "label",
        "comment",
        "inverseOf",
        "hasValue",
        "onProperty",
        "versionInfo",
        "domain",
        "intersectionOf",
        "range",
        "someValuesFrom",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("pizza")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_gzip():
    expected_v = 2687
    expected_e = 2293
    expected_labels = {"d", "a"}
    v, e, labels = graphs.graph_info_from_name("gzip")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_core():
    expected_v = 1323
    expected_e = 2752
    expected_labels = {
        "equivalentClass",
        "disjointWith",
        "subClassOf",
        "rest",
        "distinctMembers",
        "minCardinality",
        "isDefinedBy",
        "deprecated",
        "unionOf",
        "type",
        "subPropertyOf",
        "cardinality",
        "allValuesFrom",
        "oneOf",
        "maxQualifiedCardinality",
        "seeAlso",
        "onDataRange",
        "label",
        "comment",
        "inverseOf",
        "maxCardinality",
        "qualifiedCardinality",
        "hasValue",
        "versionInfo",
        "onProperty",
        "domain",
        "intersectionOf",
        "range",
        "someValuesFrom",
        "onClass",
        "first",
    }
    v, e, labels = graphs.graph_info_from_name("core")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_pathways():
    expected_v = 6238
    expected_e = 12363
    expected_labels = {"imports", "type", "subClassOf", "label", "narrower"}
    v, e, labels = graphs.graph_info_from_name("pathways")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_enzyme():
    expected_v = 48815
    expected_e = 86543
    expected_labels = {
        "narrowerTransitive",
        "replacedBy",
        "obsolete",
        "replaces",
        "broaderTransitive",
        "cofactorLabel",
        "prefLabel",
        "type",
        "activity",
        "imports",
        "subClassOf",
        "label",
        "comment",
        "altLabel",
    }
    v, e, labels = graphs.graph_info_from_name("enzyme")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_eclass():
    expected_v = 239111
    expected_e = 360248
    expected_labels = {
        "hierarchyCode",
        "creator",
        "imports",
        "type",
        "subClassOf",
        "label",
        "comment",
        "subPropertyOf",
        "range",
        "domain",
    }
    v, e, labels = graphs.graph_info_from_name("eclass")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels


def test_info_go_hierarchy():
    expected_v = 45007
    expected_e = 490109
    expected_labels = {"subClassOf"}
    v, e, labels = graphs.graph_info_from_name("go_hierarchy")
    assert v == expected_v
    assert e == expected_e
    assert labels == expected_labels
