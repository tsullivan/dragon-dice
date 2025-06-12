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
        """Processes the outcome of the initial Horde Army roll."""
        if self.game_state.setup_step != 'DETERMINING_FRONTIER':
            return

        # Set the official Frontier Terrain
        player_who_proposed = next