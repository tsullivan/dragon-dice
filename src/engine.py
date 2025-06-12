import pygame
from models import (
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

        # --- Initial Army Placement (Rulebook Step 4) ---
        # This simulates placing the initial Home, Horde, and Campaign armies.
        num_players = len(self.game_state.players)
        for i, player in enumerate(self.game_state.players):
            # Place Home Army at own Home Terrain 
            home_terrain = self.game_state.terrains[i]
            home_terrain.armies_present.append(player.name)

            # Place Horde Army at an opponent's Home Terrain 
            # In a 2-player game, this is always the other player.
            opponent_index = (i + 1) % num_players
            opponent_home_terrain = self.game_state.terrains[opponent_index]
            opponent_home_terrain.armies_present.append(player.name)

            # Place Campaign Army at the Frontier Terrain 
            if self.game_state.frontier_terrain:
                self.game_state.frontier_terrain.armies_present.append(player.name)
        
        # The game is now waiting for the user to input the result of the
        # off-screen Horde Army roll to determine the Frontier Terrain.
        self.game_state.setup_step = 'DETERMINING_FRONTIER'
        print(f"Initial setup state: {self.game_state.setup_step}")
        
    # --------------------------------------------------------------------------
    # PUBLIC METHODS (Called by the UI/Controller)
    # --------------------------------------------------------------------------
        
    def submit_frontier_selection(self, chosen_terrain_type: str, first_player_name: str):
        """
        Sets the Frontier Terrain for the game and determines the first player.
        """
        if self.game_state.setup_step != 'DETERMINING_FRONTIER':
            print("Error: Not in the correct setup step to determine frontier.")
            return

        # Find the player who proposed the chosen_terrain_type to be its owner for now
        # The rules imply the frontier terrain is selected *from* proposals.
        frontier_proposer_name = "Unknown" # Default
        for p in self.game_state.players:
            if p.proposed_frontier == chosen_terrain_type:
                frontier_proposer_name = p.name
                break
        
        # Create the Frontier Terrain object
        # Assign a unique ID; home terrains are 0 to num_players-1
        frontier_terrain_id = len(self.game_state.players) 
        self.game_state.frontier_terrain = Terrain(
            id=frontier_terrain_id,
            owner_name=frontier_proposer_name, # Or could be a generic "Frontier"
            type=chosen_terrain_type
        )

        # Set the current player index
        first_player_index = next((i for i, p in enumerate(self.game_state.players) if p.name == first_player_name), -1)
        if first_player_index != -1:
            self.game_state.current_player_index = first_player_index
        else:
            print(f"Error: Could not find player named {first_player_name}")
            # Potentially revert or handle error

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

    def draw(self, screen: pygame.Surface):
        """
        Draws the current game state.
        (Placeholder - to be implemented based on game phase)
        """
        # Example: Draw current player's name or current phase
        pass
    
    def _draw_player_panels(self, screen: pygame.Surface):
        """Draws player info on the left, now with a background panel."""
        start_x, start_y, width, height = 20, 150, 300, 400
        
        # Draw a semi-transparent panel background
        panel_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 80)) # Black with some transparency
        screen.blit(panel_surf, (start_x, start_y))

        # Draw content on top
        text_y = start_y + 20
        for player in self.game_state.players:
            color = "#FFFF99" if player.player_number - 1 == self.game_state.current_player_index else "white"
            name_surf = self.font_medium.render(player.name, True, color)
            screen.blit(name_surf, (start_x + 20, text_y))
            
            terrain_surf = self.font_small.render(f"Terrains Captured: {player.captured_terrains} / 2", True, "#AAAAAA")
            screen.blit(terrain_surf, (start_x + 20, text_y + 35))
            
            text_y += 80

    def _draw_terrain_info(self, screen: pygame.Surface):
        """Draws terrain info on the right, including armies present."""
        width = screen.get_width()
        start_x, start_y, panel_width, height = width - 320, 150, 300, 550

        panel_surf = pygame.Surface((panel_width, height), pygame.SRCALPHA)
        panel_surf.fill((0, 0, 0, 80))
        screen.blit(panel_surf, (start_x, start_y))
        
        text_y = start_y + 20
        all_terrains = self.game_state.terrains + ([self.game_state.frontier_terrain] if self.game_state.frontier_terrain else [])
        
        for terrain in all_terrains:
            name_text = f"{terrain.owner_name}'s {terrain.type}"
            name_surf = self.font_medium.render(name_text, True, "white")
            screen.blit(name_surf, (start_x + 20, text_y))

            dist_text = f"Distance: {terrain.current_value or 'Not Set'}"
            dist_surf = self.font_small.render(dist_text, True, "#AAAAAA")
            screen.blit(dist_surf, (start_x + 20, text_y + 35))

            # NEW: Draw the armies present at this terrain
            armies_text = f"Armies Present: {', '.join(terrain.armies_present)}"
            armies_surf = self.font_small.render(armies_text, True, "#CCCCCC")
            screen.blit(armies_surf, (start_x + 20, text_y + 55))

            text_y += 90
            
    def _draw_current_prompt(self, screen: pygame.Surface):
        """Draws the central prompt for the player's action."""
        width, height = screen.get_width(), screen.get_height()
        prompt_text = ""

        gs = self.game_state
        if gs.game_phase == 'GAMEPLAY':
            # This logic can be expanded for other phases
            if gs.current_turn_phase == 'FIRST_MARCH' and gs.current_march_step == 'DECIDE_MANEUVER':
                prompt_text = "Do you want to Maneuver?"
        
        if prompt_text:
            prompt_surf = self.font_medium.render(prompt_text, True, "white")
            # Draw a simple background for the prompt
            bg_rect = prompt_surf.get_rect(center=(width / 2, height / 2)).inflate(40, 30)
            prompt_bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            prompt_bg_surf.fill((20, 20, 20, 180))
            screen.blit(prompt_bg_surf, bg_rect)
            
            prompt_rect = prompt_surf.get_rect(center=bg_rect.center)
            screen.blit(prompt_surf, prompt_rect)