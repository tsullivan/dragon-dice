from PySide6.QtCore import QObject, Signal

class GameEngine(QObject):
    """
    Manages the core game logic and state for the PySide6 version.
    """
    game_state_updated = Signal() # Emitted when significant game state changes
    current_player_changed = Signal(str)
    current_phase_changed = Signal(str)

    def __init__(self, player_setup_data, first_player_name, frontier_terrain, distance_rolls, parent=None):
        super().__init__(parent)
        self.player_setup_data = player_setup_data
        # Extract player names and create a simple list of player objects or dicts if needed
        self.players_info = [{"name": p['name'], "home_terrain": p['home_terrain']} for p in player_setup_data]
        self.player_names = [p['name'] for p in self.players_info]

        self.first_player_name = first_player_name
        self.frontier_terrain = frontier_terrain
        self.distance_rolls = distance_rolls # List of (player_name, distance)

        self.current_player_idx = self.player_names.index(first_player_name) if first_player_name in self.player_names else 0
        self.current_phase = "FIRST_MARCH"  # Example starting phase from PyGame version
        self.current_march_step = "DECIDE_MANEUVER" # Example starting step

        print(f"GameEngine Initialized: First Player: {self.get_current_player_name()}, Phase: {self.current_phase}, Step: {self.current_march_step}")

    def get_current_player_name(self):
        return self.player_names[self.current_player_idx]

    def get_current_phase_display(self):
        return f"{self.current_phase.replace('_', ' ').title()} - {self.current_march_step.replace('_', ' ').title()}"

    def decide_maneuver(self, wants_to_maneuver: bool):
        print(f"Player {self.get_current_player_name()} decided maneuver: {wants_to_maneuver}")
        # Example state transition
        self.current_march_step = "AWAITING_MANEUVER_INPUT" if wants_to_maneuver else "ROLL_FOR_MARCH"
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()

    def submit_maneuver_input(self, details: str):
        print(f"Player {self.get_current_player_name()} submitted maneuver details: {details}")
        # Process details if necessary
        self.current_march_step = "ROLL_FOR_MARCH" # Next step after input
        self.current_phase_changed.emit(self.get_current_phase_display())
        self.game_state_updated.emit()
