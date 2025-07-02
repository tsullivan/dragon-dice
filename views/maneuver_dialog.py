from typing import Any, Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)


class TerrainDirectionDialog(QDialog):
    """Dialog for choosing terrain direction when maneuver succeeds."""

    direction_chosen = Signal(str)  # "UP" or "DOWN"

    def __init__(self, location: str, current_face: int, parent=None):
        super().__init__(parent)
        self.location = location
        self.current_face = current_face

        self.setWindowTitle("Choose Terrain Direction")
        self.setModal(True)
        self.resize(400, 250)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the terrain direction choice UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Maneuver Successful!")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Current terrain info
        terrain_info = QLabel(
            f"Location: {self.location}\nCurrent Face: {self.current_face}\n\nChoose the direction to turn the terrain:"
        )
        terrain_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        terrain_info.setWordWrap(True)
        layout.addWidget(terrain_info)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Direction buttons
        button_layout = QHBoxLayout()

        # UP button
        up_face = min(self.current_face + 1, 8)  # Dragon Dice faces 1-8
        self.up_button = QPushButton(f"Turn UP\n(Face {self.current_face} → {up_face})")
        self.up_button.setStyleSheet(
            "QPushButton { background-color: #339af0; color: white; font-weight: bold; padding: 10px; }"
        )
        self.up_button.clicked.connect(lambda: self._choose_direction("UP"))

        # DOWN button
        down_face = max(self.current_face - 1, 1)  # Dragon Dice faces 1-8
        self.down_button = QPushButton(f"Turn DOWN\n(Face {self.current_face} → {down_face})")
        self.down_button.setStyleSheet(
            "QPushButton { background-color: #ff8787; color: white; font-weight: bold; padding: 10px; }"
        )
        self.down_button.clicked.connect(lambda: self._choose_direction("DOWN"))

        # Disable buttons if at extremes
        if self.current_face >= 8:
            self.up_button.setEnabled(False)
            self.up_button.setText("Turn UP\n(Already at Max)")
        if self.current_face <= 1:
            self.down_button.setEnabled(False)
            self.down_button.setText("Turn DOWN\n(Already at Min)")

        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        layout.addLayout(button_layout)

    def _choose_direction(self, direction: str):
        """Emit the chosen direction and close dialog."""
        self.direction_chosen.emit(direction)
        self.accept()


class CounterManeuverDecisionDialog(QDialog):
    """Dialog for asking opposing players about counter-maneuvering."""

    decision_made = Signal(str, bool)  # player_name, will_counter

    def __init__(self, player_name: str, location: str, maneuvering_player: str, parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self.location = location
        self.maneuvering_player = maneuvering_player

        self.setWindowTitle(f"Counter-Maneuver Decision - {player_name}")
        self.setModal(True)
        self.resize(400, 250)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the counter-maneuver decision UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Counter-Maneuver Opportunity")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Explanation
        explanation = QLabel(
            f"Player {self.maneuvering_player} wants to maneuver at {self.location}.\n\n"
            f"You have an army at this location. According to Dragon Dice rules,\n"
            f"you may choose to oppose this maneuver (counter-maneuver).\n\n"
            f"If you counter-maneuver, both armies will roll dice simultaneously.\n"
            f"If you don't oppose, the maneuver automatically succeeds."
        )
        explanation.setWordWrap(True)
        explanation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(explanation)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons
        button_layout = QHBoxLayout()

        self.counter_button = QPushButton("Counter-Maneuver")
        self.counter_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; }")
        self.counter_button.clicked.connect(lambda: self._make_decision(True))

        self.allow_button = QPushButton("Allow Maneuver")
        self.allow_button.setStyleSheet("QPushButton { background-color: #51cf66; color: white; font-weight: bold; }")
        self.allow_button.clicked.connect(lambda: self._make_decision(False))

        button_layout.addWidget(self.counter_button)
        button_layout.addWidget(self.allow_button)
        layout.addLayout(button_layout)

    def _make_decision(self, will_counter: bool):
        """Emit the decision and close dialog."""
        print(f"CounterManeuverDecisionDialog: {self.player_name} making decision: {will_counter}")
        self.decision_made.emit(self.player_name, will_counter)
        self.accept()


class SimultaneousManeuverRollDialog(QDialog):
    """Dialog for handling simultaneous maneuver rolls."""

    rolls_completed = Signal(int, int)  # maneuvering_results, counter_results

    def __init__(
        self,
        maneuvering_player: str,
        maneuvering_army: dict,
        counter_players: list,
        location: str,
        parent=None,
    ):
        super().__init__(parent)
        self.maneuvering_player = maneuvering_player
        self.maneuvering_army = maneuvering_army
        self.counter_players = counter_players
        self.location = location

        self.maneuvering_results = 0
        self.counter_results = 0
        self.results_submitted = {"maneuvering": False, "counter": False}

        self.setWindowTitle(f"Simultaneous Maneuver Rolls - {location}")
        self.setModal(True)
        self.resize(600, 400)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the simultaneous rolling UI."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Simultaneous Maneuver Rolls")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            f"Both armies must roll dice simultaneously at {self.location}.\n"
            f"Count maneuver results only. Maneuvering succeeds if results ≥ counter-maneuver results."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)

        # Rolling sections
        roll_layout = QHBoxLayout()

        # Maneuvering player section
        maneuvering_group = QGroupBox(f"Maneuvering Army - {self.maneuvering_player}")
        maneuvering_layout = QVBoxLayout(maneuvering_group)

        maneuvering_info = QLabel(
            f"Army: {self.maneuvering_army.get('name', 'Unknown')}\n"
            f"Units: {len(self.maneuvering_army.get('units', []))}"
        )
        maneuvering_layout.addWidget(maneuvering_info)

        maneuver_result_layout = QHBoxLayout()
        maneuver_result_layout.addWidget(QLabel("Maneuver Results:"))
        self.maneuvering_spin = QSpinBox()
        self.maneuvering_spin.setMinimum(0)
        self.maneuvering_spin.setMaximum(50)  # Reasonable max
        maneuver_result_layout.addWidget(self.maneuvering_spin)
        maneuvering_layout.addLayout(maneuver_result_layout)

        self.submit_maneuvering_btn = QPushButton("Submit Maneuvering Results")
        self.submit_maneuvering_btn.clicked.connect(self._submit_maneuvering_results)
        maneuvering_layout.addWidget(self.submit_maneuvering_btn)

        roll_layout.addWidget(maneuvering_group)

        # Counter-maneuvering player section
        counter_group = QGroupBox("Counter-Maneuvering Army")
        counter_layout = QVBoxLayout(counter_group)

        counter_players_text = ", ".join(self.counter_players)
        counter_info = QLabel(f"Players: {counter_players_text}")
        counter_layout.addWidget(counter_info)

        counter_result_layout = QHBoxLayout()
        counter_result_layout.addWidget(QLabel("Maneuver Results:"))
        self.counter_spin = QSpinBox()
        self.counter_spin.setMinimum(0)
        self.counter_spin.setMaximum(50)  # Reasonable max
        counter_result_layout.addWidget(self.counter_spin)
        counter_layout.addLayout(counter_result_layout)

        self.submit_counter_btn = QPushButton("Submit Counter-Maneuver Results")
        self.submit_counter_btn.clicked.connect(self._submit_counter_results)
        counter_layout.addWidget(self.submit_counter_btn)

        roll_layout.addWidget(counter_group)
        layout.addLayout(roll_layout)

        # Results display
        self.results_display = QTextEdit()
        self.results_display.setMaximumHeight(100)
        self.results_display.setPlainText("Waiting for both armies to submit their maneuver results...")
        layout.addWidget(self.results_display)

        # Complete button (initially disabled)
        self.complete_btn = QPushButton("Complete Maneuver")
        self.complete_btn.setEnabled(False)
        self.complete_btn.clicked.connect(self._complete_maneuver)
        layout.addWidget(self.complete_btn)

    def _submit_maneuvering_results(self):
        """Submit maneuvering army results."""
        self.maneuvering_results = self.maneuvering_spin.value()
        self.results_submitted["maneuvering"] = True
        self.submit_maneuvering_btn.setEnabled(False)
        self.maneuvering_spin.setEnabled(False)

        self.results_display.append(f"Maneuvering army rolled {self.maneuvering_results} maneuver results.")
        self._check_completion()

    def _submit_counter_results(self):
        """Submit counter-maneuvering army results."""
        self.counter_results = self.counter_spin.value()
        self.results_submitted["counter"] = True
        self.submit_counter_btn.setEnabled(False)
        self.counter_spin.setEnabled(False)

        self.results_display.append(f"Counter-maneuvering army rolled {self.counter_results} maneuver results.")
        self._check_completion()

    def _check_completion(self):
        """Check if both results are submitted and show final result."""
        if all(self.results_submitted.values()):
            if self.maneuvering_results >= self.counter_results:
                result_text = f"MANEUVER SUCCEEDS! ({self.maneuvering_results} ≥ {self.counter_results})"
                self.results_display.append(f"\n{result_text}")
            else:
                result_text = f"MANEUVER FAILS! ({self.maneuvering_results} < {self.counter_results})"
                self.results_display.append(f"\n{result_text}")

            self.complete_btn.setEnabled(True)

    def _complete_maneuver(self):
        """Complete the maneuver and emit results."""
        self.rolls_completed.emit(self.maneuvering_results, self.counter_results)
        self.accept()


class ManeuverDialog(QDialog):
    """
    Main dialog coordinator for Dragon Dice maneuver flow.
    This dialog now serves as a coordinator and may not always show UI -
    it manages the proper Dragon Dice maneuver sequence.
    """

    maneuver_completed = Signal(dict)  # Emits maneuver results
    maneuver_cancelled = Signal()

    def __init__(
        self,
        current_player_name: str,
        acting_army: Dict[str, Any],
        all_players_data: Dict[str, Dict[str, Any]],
        terrain_data: Dict[str, Dict[str, Any]],
        game_engine,
        parent=None,
    ):
        super().__init__(parent)
        self.current_player_name = current_player_name
        self.acting_army = acting_army
        self.all_players_data = all_players_data
        self.terrain_data = terrain_data
        self.game_engine = game_engine

        # Connect to engine signals
        self.game_engine.counter_maneuver_requested.connect(self._handle_counter_maneuver_request)
        self.game_engine.simultaneous_maneuver_rolls_requested.connect(self._handle_simultaneous_rolls_request)
        self.game_engine.terrain_direction_choice_requested.connect(self._handle_terrain_direction_request)
        # Connect to game state changes to auto-close when maneuver is complete
        self.game_engine.game_state_updated.connect(self._check_if_should_close)

        # This coordinator dialog should never be visible - it just manages the flow
        self.setWindowTitle("Maneuver Coordinator")
        self.setModal(False)  # Not modal since it's just a coordinator
        self.setVisible(False)  # Completely invisible
        self.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)  # Prevent showing

        # Automatically start the maneuver process
        self._start_maneuver_process()

    def _start_maneuver_process(self):
        """Start the Dragon Dice maneuver process through the engine."""
        # The engine will handle the logic and emit appropriate signals
        # This triggers the proper Dragon Dice maneuver flow
        self.game_engine.decide_maneuver(True)

    def _handle_counter_maneuver_request(self, location: str, opposing_armies: list):
        """Handle request for counter-maneuver decisions from opposing players."""
        print(f"ManeuverDialog: Handling counter-maneuver request at {location}")
        print(f"ManeuverDialog: Opposing armies: {opposing_armies}")

        # Get unique opposing players
        opposing_players = list(set(army["player"] for army in opposing_armies))
        print(f"ManeuverDialog: Opposing players: {opposing_players}")

        self.pending_decisions: Dict[str, Any] = {}
        self.expected_decisions = set(opposing_players)
        self.active_decision_dialogs: List[Any] = []

        # Handle players sequentially (since typically it's one at a time in Dragon Dice)
        for player_name in opposing_players:
            print(f"ManeuverDialog: Showing decision dialog for {player_name}")
            decision_dialog = CounterManeuverDecisionDialog(player_name, location, self.current_player_name, None)
            decision_dialog.decision_made.connect(self._handle_counter_decision)

            # Show the dialog and wait for decision
            result = decision_dialog.exec()  # This will block until decision is made
            print(f"ManeuverDialog: Dialog result for {player_name}: {result}")

            # The signal should have been emitted by now

    def _handle_counter_decision(self, player_name: str, will_counter: bool):
        """Handle a player's counter-maneuver decision."""
        print(f"ManeuverDialog: {player_name} counter-maneuver decision: {will_counter}")

        # Submit the decision immediately to the engine
        self.game_engine.submit_counter_maneuver_decision(player_name, will_counter)

    def _handle_simultaneous_rolls_request(
        self,
        maneuvering_player: str,
        maneuvering_army: dict,
        opposing_armies: list,
        counter_responses: dict,
    ):
        """Handle request for simultaneous maneuver rolls."""
        print("ManeuverDialog: Handling simultaneous rolls request")

        # Get players who chose to counter-maneuver
        counter_players = [player for player, decision in counter_responses.items() if decision]
        location = maneuvering_army.get("location", "Unknown Location")

        # Show simultaneous roll dialog
        roll_dialog = SimultaneousManeuverRollDialog(
            maneuvering_player, maneuvering_army, counter_players, location, None
        )
        roll_dialog.rolls_completed.connect(self._handle_roll_results)
        roll_dialog.exec()  # Use exec() to ensure modal and visible

    def _handle_roll_results(self, maneuvering_results: int, counter_results: int):
        """Handle the results from simultaneous rolling."""
        print(f"ManeuverDialog: Roll results - Maneuvering: {maneuvering_results}, Counter: {counter_results}")

        # Submit results to engine for processing
        self.game_engine.submit_maneuver_roll_results(maneuvering_results, counter_results)

        # Close this coordinator dialog
        self.accept()

    def _handle_terrain_direction_request(self, location: str, current_face: int):
        """Handle request for terrain direction choice."""
        print(f"ManeuverDialog: Handling terrain direction request for {location} (face {current_face})")

        # Show terrain direction choice dialog
        # Use None as parent to avoid visibility issues with invisible coordinator
        direction_dialog = TerrainDirectionDialog(location, current_face, None)
        direction_dialog.direction_chosen.connect(self._handle_direction_choice)
        direction_dialog.exec()  # Use exec() instead of show() to ensure it's modal and visible

    def _handle_direction_choice(self, direction: str):
        """Handle the player's terrain direction choice."""
        print(f"ManeuverDialog: Player chose direction: {direction}")

        # Submit direction choice to engine
        self.game_engine.submit_terrain_direction_choice(direction)

        # Close the coordinator dialog
        self.accept()

    def _check_if_should_close(self):
        """Check if the dialog should auto-close based on game state."""
        try:
            current_march_step = self.game_engine.get_current_march_step()
            print(f"[ManeuverDialog] Game state updated, march step: {current_march_step}")

            # If we've moved to SELECT_ACTION, the maneuver is complete
            if current_march_step == "SELECT_ACTION":
                print("[ManeuverDialog] Auto-closing due to SELECT_ACTION state")
                self.accept()
        except Exception as e:
            print(f"[ManeuverDialog] Error checking game state: {e}")

    def closeEvent(self, event):
        """Handle dialog close event."""
        print("[ManeuverDialog] Dialog closing")
        self.maneuver_cancelled.emit()
        super().closeEvent(event)
