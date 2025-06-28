import pytest
from PySide6.QtWidgets import QApplication

from views.main_gameplay_view import MainGameplayView
from game_logic.engine import GameEngine  # To instantiate the game engine for the view
from test.utils.visual_test_helpers import capture_widget_screenshot
import utils.constants as constants


def setup_game_engine():
    """Helper to create a GameEngine instance with mock data."""
    # Mock data for GameEngine initialization
    mock_player_setup_data = [
        {
            "name": "Player 1",
            "home_terrain": "Highland",
            "armies": {
                "home": {"name": "P1 Home", "points": 10},
                "campaign": {"name": "P1 Campaign", "points": 10},
                "horde": {"name": "P1 Horde", "points": 4},
            },
        },
        {
            "name": "Player 2",
            "home_terrain": "Coastland",
            "armies": {
                "home": {"name": "P2 Home", "points": 12},
                "campaign": {"name": "P2 Campaign", "points": 8},
                "horde": {"name": "P2 Horde", "points": 4},
            },
        },
    ]
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
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index(
        "EIGHTH_FACE"
    )
    game_engine.turn_manager.current_phase = "EIGHTH_FACE"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()  # Ensure engine processes this phase entry

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    # main_gameplay_view.update_ui() # update_ui is called on init and by signals
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_EighthFacePhase"
    )


def test_main_gameplay_view_dragon_attack_phase(qtbot):
    game_engine = setup_game_engine()
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index(
        "DRAGON_ATTACK"
    )
    game_engine.turn_manager.current_phase = "DRAGON_ATTACK"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_DragonAttackPhase"
    )


def test_main_gameplay_view_awaiting_maneuver_input(qtbot):
    game_engine = setup_game_engine()
    # Initial state is FIRST_MARCH - DECIDE_MANEUVER
    game_engine.decide_maneuver(True)  # Player decides to maneuver

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    # game_engine.game_state_updated signal should trigger update_ui
    QApplication.processEvents()  # Ensure signals are processed
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_AwaitingManeuverInput"
    )


def test_main_gameplay_view_select_action_after_maneuver_no(qtbot):
    game_engine = setup_game_engine()
    game_engine.decide_maneuver(False)  # Player decides NOT to maneuver

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_SelectAction_NoManeuver"
    )


def test_main_gameplay_view_select_action_after_maneuver_submit(qtbot):
    game_engine = setup_game_engine()
    game_engine.decide_maneuver(True)
    game_engine.submit_maneuver_input("Flying units advance.")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_SelectAction_AfterManeuver"
    )


def test_main_gameplay_view_attacker_melee_roll(qtbot):
    game_engine = setup_game_engine()
    # Navigate to SELECT_ACTION state first
    game_engine.decide_maneuver(False)  # Or submit_maneuver_input
    game_engine.select_action("MELEE")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_AttackerMeleeRoll"
    )


def test_main_gameplay_view_defender_saves_roll(qtbot):
    game_engine = setup_game_engine()
    # Navigate to AWAITING_ATTACKER_MELEE_ROLL state
    game_engine.decide_maneuver(False)
    game_engine.select_action("MELEE")
    # Submit attacker results to move to defender saves
    game_engine.submit_attacker_melee_results("5 hits")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_DefenderSavesRoll"
    )


def test_main_gameplay_view_expire_effects_phase_auto_advances(qtbot):
    """
    Tests that EXPIRE_EFFECTS phase is entered and then auto-advances.
    The screenshot will likely be of the phase *after* EXPIRE_EFFECTS (i.e., EIGHTH_FACE).
    """
    game_engine = setup_game_engine()
    # Manually set to EXPIRE_EFFECTS. _handle_phase_entry for EXPIRE_EFFECTS calls advance_phase()
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index(
        "EXPIRE_EFFECTS"
    )
    game_engine.turn_manager.current_phase = "EXPIRE_EFFECTS"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""

    # _handle_phase_entry for EXPIRE_EFFECTS will call advance_phase,
    # which in turn calls _handle_phase_entry for the *next* phase (EIGHTH_FACE).
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()  # Allow signals to propagate
    # The UI should now reflect the EIGHTH_FACE phase
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_AfterExpireEffects"
    )


def test_main_gameplay_view_species_abilities_phase(qtbot):
    """Tests the SPECIES_ABILITIES phase display."""
    game_engine = setup_game_engine()
    # Set to SPECIES_ABILITIES phase
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index(
        "SPECIES_ABILITIES"
    )
    game_engine.turn_manager.current_phase = "SPECIES_ABILITIES"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_SpeciesAbilitiesPhase"
    )


def test_main_gameplay_view_reserves_phase(qtbot):
    """Tests the RESERVES phase display."""
    game_engine = setup_game_engine()
    # Set to RESERVES phase
    game_engine.turn_manager.current_phase_idx = constants.TURN_PHASES.index("RESERVES")
    game_engine.turn_manager.current_phase = "RESERVES"
    game_engine.turn_manager.current_march_step = ""
    game_engine.turn_manager.current_action_step = ""
    game_engine._handle_phase_entry()

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_ReservesPhase"
    )


def test_main_gameplay_view_attacker_missile_roll(qtbot):
    """Tests the MISSILE action step display."""
    game_engine = setup_game_engine()
    # Navigate to SELECT_ACTION state first, then select MISSILE
    game_engine.decide_maneuver(False)
    game_engine.select_action("MISSILE")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(
        qtbot, main_gameplay_view, "MainGameplayView_AttackerMissileRoll"
    )


def test_main_gameplay_view_magic_roll(qtbot):
    """Tests the MAGIC action step display."""
    game_engine = setup_game_engine()
    # Navigate to SELECT_ACTION state first, then select MAGIC
    game_engine.decide_maneuver(False)
    game_engine.select_action("MAGIC")

    main_gameplay_view = MainGameplayView(game_engine=game_engine)
    QApplication.processEvents()
    capture_widget_screenshot(qtbot, main_gameplay_view, "MainGameplayView_MagicRoll")
