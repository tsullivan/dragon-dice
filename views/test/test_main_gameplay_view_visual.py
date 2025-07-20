import pytest
from PySide6.QtWidgets import QApplication

import constants
from game_logic.game_orchestrator import GameOrchestrator as GameEngine  # To instantiate the game engine for the view
from models.game_phase_model import get_turn_phases
from models.test.mock import create_army_dict, create_player_setup_dict
from test.utils.visual_test_helpers import capture_widget_screenshot
from views.main_gameplay_view import MainGameplayView


def setup_game_engine():
    """Helper to create a GameEngine instance with type-safe mock data."""
    # Create Player 1 with complete mock data
    player1_data = create_player_setup_dict(name="Player 1", home_terrain="Highland", force_size=24)
    player1_data["armies"] = {
        "home": create_army_dict(
            name="P1 Home", location="Player 1 Highland", allocated_points=10, unique_id="player_1_home", unit_count=1
        ),
        "campaign": create_army_dict(
            name="P1 Campaign", location="Flatland", allocated_points=10, unique_id="player_1_campaign", unit_count=1
        ),
        "horde": create_army_dict(
            name="P1 Horde", location="Player 2 Coastland", allocated_points=4, unique_id="player_1_horde", unit_count=1
        ),
    }

    # Create Player 2 with complete mock data
    player2_data = create_player_setup_dict(name="Player 2", home_terrain="Coastland", force_size=24)
    player2_data["armies"] = {
        "home": create_army_dict(
            name="P2 Home", location="Player 2 Coastland", allocated_points=12, unique_id="player_2_home", unit_count=1
        ),
        "campaign": create_army_dict(
            name="P2 Campaign", location="Flatland", allocated_points=8, unique_id="player_2_campaign", unit_count=1
        ),
        "horde": create_army_dict(
            name="P2 Horde", location="Player 1 Highland", allocated_points=4, unique_id="player_2_horde", unit_count=1
        ),
    }

    mock_player_setup_data = [player1_data, player2_data]
    mock_first_player_name = "Player 1"
    mock_frontier_terrain = "Flatland"
    mock_distance_rolls = [("Player 1", 3), ("Player 2", 5)]

    game_engine = GameEngine(
        player_setup_data=mock_player_setup_data,
        first_player_name=mock_first_player_name,
        frontier_terrain=mock_frontier_terrain,
        distance_rolls=mock_distance_rolls,
    )
    return game_engine


def test_main_gameplay_view_initial_state(qtbot):
    """Captures a PNG of the MainGameplayView in its initial state (First March - Decide Maneuver)."""
    game_engine = setup_game_engine()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_initial")
    # The test implicitly passes if no exceptions occur and the assertion in capture_widget_screenshot passes.


def test_main_gameplay_view_eighth_face_phase(qtbot):
    game_engine = setup_game_engine()
    # Manually set the game engine to the EIGHTH_FACE phase
    game_engine.turn_manager.current_phase_idx = get_turn_phases().index("EIGHTH_FACE")
    game_engine.turn_manager.current_phase = "EIGHTH_FACE"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()  # Ensure engine processes this phase entry

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    # main_gameplay_view.update_ui() # update_ui is called on init and by signals
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_EighthFacePhase")


def test_main_gameplay_view_dragon_attack_phase(qtbot):
    game_engine = setup_game_engine()
    game_engine.turn_manager.current_phase_idx = get_turn_phases().index("DRAGON_ATTACK")
    game_engine.turn_manager.current_phase = "DRAGON_ATTACK"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_DragonAttackPhase")


def test_main_gameplay_view_awaiting_maneuver_input(qtbot):
    game_engine = setup_game_engine()
    # Initial state is FIRST_MARCH - DECIDE_MANEUVER
    game_engine.decide_maneuver(True)  # Player decides to maneuver

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    # game_engine.game_state_updated signal should trigger update_ui
    QApplication.processEvents()  # Ensure signals are processed
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_AwaitingManeuverInput")


def test_main_gameplay_view_select_action_after_maneuver_no(qtbot):
    game_engine = setup_game_engine()
    game_engine.decide_maneuver(False)  # Player decides NOT to maneuver

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_SelectAction_NoManeuver")


def test_main_gameplay_view_select_action_after_maneuver_submit(qtbot):
    game_engine = setup_game_engine()
    game_engine.decide_maneuver(True)
    game_engine.submit_maneuver_input("Flying units advance.")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_SelectAction_AfterManeuver")


def test_main_gameplay_view_attacker_melee_roll(qtbot):
    game_engine = setup_game_engine()
    # Navigate to SELECT_ACTION state first
    game_engine.decide_maneuver(False)  # Or submit_maneuver_input
    game_engine.select_action("MELEE")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_AttackerMeleeRoll")


def test_main_gameplay_view_defender_saves_roll(qtbot):
    game_engine = setup_game_engine()
    # Navigate to AWAITING_ATTACKER_MELEE_ROLL state
    # First choose an acting army (required before maneuver decision)
    mock_army = {
        "name": "Player 1 Home Army",
        "army_type": "home",
        "location": "Player 1 Highland",
        "unique_id": "Player 1_home",
    }
    game_engine.choose_acting_army(mock_army)
    game_engine.decide_maneuver(False)
    game_engine.select_action("MELEE")
    # Submit attacker results to move to defender saves
    game_engine.submit_attacker_melee_results("5 melee")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_DefenderSavesRoll")


def test_main_gameplay_view_expire_effects_phase_auto_advances(qtbot):
    """
    Tests that EXPIRE_EFFECTS phase is entered and then auto-advances.
    The screenshot will likely be of the phase *after* EXPIRE_EFFECTS (i.e., EIGHTH_FACE).
    """
    game_engine = setup_game_engine()
    # Manually set to EXPIRE_EFFECTS. _handle_phase_entry for EXPIRE_EFFECTS calls advance_phase()
    game_engine.turn_manager.current_phase_idx = get_turn_phases().index("EXPIRE_EFFECTS")
    game_engine.turn_manager.current_phase = "EXPIRE_EFFECTS"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""

    # _handle_phase_entry for EXPIRE_EFFECTS will call advance_phase,
    # which in turn calls _handle_phase_entry for the *next* phase (EIGHTH_FACE).
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()  # Allow signals to propagate
    # The UI should now reflect the EIGHTH_FACE phase
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_AfterExpireEffects")


def test_main_gameplay_view_species_abilities_phase(qtbot):
    """Tests the SPECIES_ABILITIES phase display."""
    game_engine = setup_game_engine()
    # Set to SPECIES_ABILITIES phase
    game_engine.turn_manager.current_phase_idx = get_turn_phases().index("SPECIES_ABILITIES")
    game_engine.turn_manager.current_phase = "SPECIES_ABILITIES"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_SpeciesAbilitiesPhase")


def test_main_gameplay_view_reserves_phase(qtbot):
    """Tests the RESERVES phase display."""
    game_engine = setup_game_engine()
    # Set to RESERVES phase
    game_engine.turn_manager.current_phase_idx = get_turn_phases().index("RESERVES")
    game_engine.turn_manager.current_phase = "RESERVES"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_ReservesPhase")


def test_main_gameplay_view_attacker_missile_roll(qtbot):
    """Tests the MISSILE action step display."""
    game_engine = setup_game_engine()
    # Navigate to SELECT_ACTION state first, then select MISSILE
    game_engine.decide_maneuver(False)
    game_engine.select_action("MISSILE")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_AttackerMissileRoll")


def test_main_gameplay_view_magic_roll(qtbot):
    """Tests the MAGIC action step display."""
    game_engine = setup_game_engine()
    # Navigate to SELECT_ACTION state first, then select MAGIC
    game_engine.decide_maneuver(False)
    game_engine.select_action("MAGIC")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_MagicRoll")
