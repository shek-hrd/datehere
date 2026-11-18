import pytest
from meshnet.routing import MeshTopology


def test_multihop_route():
    t = MeshTopology()
    t.add_link("a", "b")
    t.add_link("b", "c")
    assert t.route("a", "c") == ["a", "b", "c"]


def test_failure_reroutes():
    t = MeshTopology()
    t.add_link("a", "b")
    t.add_link("b", "c")
    t.add_link("a", "d")
    t.add_link("d", "c")
    assert t.route("a", "c") == ["a", "b", "c"]
    t.remove_node("b")
    assert t.route("a", "c") == ["a", "d", "c"]


def test_no_route_raises():
    t = MeshTopology()
    t.add_node("a")
    t.add_node("z")
    with pytest.raises(ValueError):
        t.route("a", "z")
