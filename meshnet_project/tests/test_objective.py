from meshnet.objective import HELP_TEXT, FULL_OBJECTIVE, show_help
from meshnet.mesh import MeshNetwork


def test_complete_objective_present():
    assert "COMPLETE PROJECT OBJECTIVE" in FULL_OBJECTIVE
    assert "Blockchain of messages" in FULL_OBJECTIVE
    assert "Sensei Network Map" in FULL_OBJECTIVE
    assert "Runtime -> Run all" in FULL_OBJECTIVE or "Runtime" in FULL_OBJECTIVE
    assert "No fixed ports" in FULL_OBJECTIVE


def test_help_contains_objective_and_commands():
    help_text = show_help()
    assert "COMPLETE PROJECT OBJECTIVE" in help_text
    assert "Blockchain of messages" in help_text
    assert "Sensei Network Map" in help_text
    assert "/peers" in HELP_TEXT
    assert "/routes" in HELP_TEXT
    assert "/ping" in HELP_TEXT


def test_network_show_help_matches_shared_help():
    net = MeshNetwork()
    assert net.show_help() == HELP_TEXT
