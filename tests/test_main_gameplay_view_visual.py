import pytest
import os
from PySide6.QtWidgets import QApplication

from views.main_gameplay_view import MainGameplayView
from game_logic.engine import GameEngine # To instantiate the game engine for the view
import constants

# Ensure the output directory exists, as defined in CONTRIBUTING.md
VISUAL_TESTS_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "test-visuals", "views")
if not os.path.exists(VISUAL_TESTS_OUTPUT_DIR):
    os.makedirs(VISUAL_TESTS_OUTPUT_DIR, exist_ok=True)

# pytest-qt provides the qtbot fixture automatically
def capture_widget_screenshot(qtbot, widget_to_test, filename_base, sub_directory=""):
    """
    Helper function to show a widget, capture, and save a screenshot.
    """
    qtbot.addWidget(widget_to_test)
    widget_to_test.show()
    qtbot.waitExposed(widget_to_test)

    # Ensure all pending events are processed, allowing the widget to fully render
    QApplication.processEvents()

    output_dir_path = os.path.join(VISUAL_TESTS_OUTPUT_DIR, sub_directory)
    if not os.path.exists(output_dir_path) and sub_directory:
        os.makedirs(output_dir_path, exist_ok=True)

    output_path = os.path.join(output_dir_path, f"{filename_base}.png")
    pixmap = widget_to_test.grab()
    pixmap.save(output_path)
    print(f"Screenshot saved: {output_path}")
    assert os.path.exists(output_path)
    return output_path

def setup_game_engine():
    """Helper to create a GameEngine instance with mock data."""
    # Mock data for GameEngine initialization
    mock_player_setup_data = [
        {"name": "Player 1", "home_terrain": "Highland", "armies": {"home": {"name": "P1 Home", "points": 10}, "campaign": {"name": "P1 Campaign", "points": 10}, "horde": {"name": "P1 Horde", "points": 4}}},
        {"name": "Player 2", "home_terrain": "Coastland", "armies": {"home": {"name": "P2 Home", "points": 12}, "campaign": {"name": "P2 Campaign", "points": 8}, "horde": {"name": "P2 Horde", "points": 4}}}
    ]
    mock_first_player_name = "Player 1"
    mock_frontier_terrain = "Flatland"
    mock_distance_rolls = [("Player 1", 3), ("Player 2", 5)]

    game_engine = GameEngine(
        player_setup_data=mock_player_setup_data,
        first_player_name=mock_first_player_name,
        frontier_terrain=mock_frontier_terrain,
        distance_rolls=mock_distance_rolls
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
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index(constants.PHASE_EIGHTH_FACE)
    game_engine.turn_manager.current_phase = constants.PHASE_EIGHTH_FACE
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry() # Ensure engine processes this phase entry
    
    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    # main_gameplay_view.update_ui() # update_ui is called on init and by signals
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_EighthFacePhase")

def test_main_gameplay_view_dragon_attack_phase(qtbot):
    game_engine = setup_game_engine()
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index(constants.PHASE_DRAGON_ATTACK)
    game_engine.turn_manager.current_phase = constants.PHASE_DRAGON_ATTACK
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_DragonAttackPhase")

def test_main_gameplay_view_awaiting_maneuver_input(qtbot):
    game_engine = setup_game_engine()
    # Initial state is FIRST_MARCH - DECIDE_MANEUVER
    game_engine.decide_maneuver(True) # Player decides to maneuver

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    # game_engine.game_state_updated signal should trigger update_ui
    QApplication.processEvents() # Ensure signals are processed
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_AwaitingManeuverInput")

def test_main_gameplay_view_select_action_after_maneuver_no(qtbot):
    game_engine = setup_game_engine()
    game_engine.decide_maneuver(False) # Player decides NOT to maneuver

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
    game_engine.decide_maneuver(False) # Or submit_maneuver_input
    game_engine.select_action(constants.ACTION_MELEE)

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_AttackerMeleeRoll")

def test_main_gameplay_view_defender_saves_roll(qtbot):
    game_engine = setup_game_engine()
    # Navigate to AWAITING_ATTACKER_MELEE_ROLL state
    game_engine.decide_maneuver(False)
    game_engine.select_action(constants.ACTION_MELEE)
    # Submit attacker results to move to defender saves
    game_engine.submit_attacker_melee_results("5 hits")

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
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index(constants.PHASE_EXPIRE_EFFECTS)
    game_engine.turn_manager.current_phase = constants.PHASE_EXPIRE_EFFECTS
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    
    # _handle_phase_entry for EXPIRE_EFFECTS will call advance_phase,
    # which in turn calls _handle_phase_entry for the *next* phase (EIGHTH_FACE).
    game_engine._handle_phase_entry() 

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents() # Allow signals to propagate
    # The UI should now reflect the EIGHTH_FACE phase
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_AfterExpireEffects")

# TODO: Add tests for other phases like SPECIES_ABILITIES, RESERVES
# TODO: Add tests for MISSILE and MAGIC action steps once implemented
