import pygame
import random
from src.models import (
    GameState,
    Player,
    Terrain,
    PlayerSetupData,
)

class GameEngine:
    """
    Manages the game state and enforces all rules. This class does not
    handle user events directly but provides methods for the UI layer to call.
    """

    def __init__(self, point_value: int, setups: list[PlayerSetupData]):
        """
        Initializes the GameEngine and the GameState.
        """
        self.game_state = GameState(point_value=point_value)
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)

        self._setup_game(setups)

    def _setup_game(self, setups: list[PlayerSetupData]):
        """
        Creates all the initial Player and Terrain objects and sets the
        first step for the interactive setup process.
        """
        print(f"Setting up a game with a {self.game_state.point_value} point limit.")

        for i, setup in enumerate(setups):
            player = Player(
                player_number=i + 1,
                name=setup['name'],
                home_terrain=setup['home_terrain'],
                proposed_frontier=setup['frontier_terrain'],
            )
            self.game_state.players.append(player)
            
            home_terrain = Terrain(id=i, owner_name=player.name, type=player.home_terrain)
            self.game_state.terrains.append(home_terrain)

        # The game is now waiting for the user to input the result of the
        # off-screen Horde Army roll to determine the Frontier Terrain.
        self.game_state.setup_step = 'DETERMINING_FRONTIER'
        print(f"Initial setup state: {self.game_state.setup_step}")
        
    # --------------------------------------------------------------------------
    # PUBLIC METHODS (Called by the UI/Controller)
    # --------------------------------------------------------------------------
        
    def submit_frontier_selection(self, chosen_terrain_type: str, first_player_name: str):
        # ... (This method is likely already correct from our last discussion)
        # It sets the frontier_terrain, sets currentPlayerIndex, and then...
        self.game_state.setup_step = 'AWAITING_DISTANCE_ROLLS'
        print(f"Setup state updated to: {self.game_state.setup_step}")

    def submit_distance_rolls(self, rolls: list[dict]):
        """Processes the starting distance rolls for all terrains."""
        if self.game_state.setup_step != 'AWAITING_DISTANCE_ROLLS':
            return
        
        # Process and validate rolls according to the rules
        for roll_data in rolls:
            value = int(roll_data['value'])
            if value >= 8 or value <= 0:
                print(f"Invalid roll of {value} submitted. Must be between 1 and 7.")
                # In a real app, you would show an error message to the user
                return # Abort
            
            final_value = 6 if value == 7 else value

            # Find and update the terrain in the game state
            terrain = next((t for t in self.game_state.terrains if t.id == roll_data['terrain_id']), None)
            if not terrain:
                # Check if the frontier_terrain exists and matches the ID
                if self.game_state.frontier_terrain and self.game_state.frontier_terrain.id == roll_data['terrain_id']:
                    terrain = self.game_state.frontier_terrain
            
            if terrain:
                terrain.current_value = final_value

        # Transition to gameplay
        self.game_state.game_phase = 'GAMEPLAY'
        self.game_state.current_turn_phase = 'FIRST_MARCH'
        self.game_state.current_march_step = 'DECIDE_MANEUVER'
        print("Setup complete. Starting gameplay.")