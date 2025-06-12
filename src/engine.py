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
        self.setups = setups # Store setups for later access to army names

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

        # --- Initial Army Placement (Partial: Home & Horde Armies) ---
        # Campaign armies are placed after Frontier is determined.
        num_players = len(self.game_state.players)
        for i, player in enumerate(self.game_state.players):
            # Place Home Army at own Home Terrain 
            home_terrain = self.game_state.terrains[i]
            # Find the corresponding setup data to get the army name
            setup_data = next(s for s in setups if s['name'] == player.name)
            home_terrain.armies_present.append(
                {"player_name": player.name, "army_type": "Home", "army_name": setup_data.get('home_army_name', 'Home Army')}
            )

            # Place Horde Army at an opponent's Home Terrain
            # Horde armies are typically placed on an opponent's terrain.
            # In a 1-player game, this step can be skipped for the single player's Horde army.
            if num_players > 1:
                # Find the corresponding setup data to get the army name
                setup_data = next(s for s in setups if s['name'] == player.name)
                opponent_index = (i + 1) % num_players
                opponent_home_terrain = self.game_state.terrains[opponent_index]
                opponent_home_terrain.armies_present.append(
                    {"player_name": player.name, "army_type": "Horde", "army_name": setup_data.get('horde_army_name', 'Horde Army')}
                )

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

        # --- Place Campaign Armies (Rulebook Step 4 continued) ---
        if self.game_state.frontier_terrain:
            for player in self.game_state.players:
                # Find the original setup data for this player
                player_setup_data = next((s for s in self.setups if s['name'] == player.name), None)
                campaign_army_name = "Campaign Army" # Default
                if player_setup_data:
                    campaign_army_name = player_setup_data.get('campaign_army_name', "Campaign Army")
                self.game_state.frontier_terrain.armies_present.append(
                    {"player_name": player.name, "army_type": "Campaign", "army_name": campaign_army_name}
                )
        else:
            # This should ideally not happen if logic is correct
            print("Error: Frontier terrain not set, cannot place campaign armies.")
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

    def _advance_to_next_phase_or_player(self):
        """
        Advances the game to the next logical phase or player turn.
        This should be called after a current phase/step's primary action is completed
        and gs.current_march_step is set to 'COMPLETE'.
        """
        gs = self.game_state
        current_player_name = gs.players[gs.current_player_index].name

        if gs.current_march_step != 'COMPLETE':
            # This method should only be called when a step is truly done.
            print(f"Warning: _advance_to_next_phase_or_player called but current step {gs.current_march_step} is not 'COMPLETE'.")
            return

        if gs.current_turn_phase == 'FIRST_MARCH':
            print(f"Player {current_player_name}'s First March complete.")
            gs.current_turn_phase = 'SECOND_MARCH'
            gs.current_march_step = 'DECIDE_MANEUVER' 
            print(f"Transitioning to Second March for player {current_player_name}.")
        
        elif gs.current_turn_phase == 'SECOND_MARCH':
            print(f"Player {current_player_name}'s Second March complete.")
            gs.current_turn_phase = 'RESERVES'
            # Assuming RESERVES phase might have its own steps, e.g., 'PLACE_RESERVES'
            # For now, let's set it to a generic placeholder or None if it's a simple phase.
            gs.current_march_step = None # Or 'ACTION_RESERVES'
            print(f"Transitioning to Reserves phase for player {current_player_name}.")

        elif gs.current_turn_phase == 'RESERVES':
            # Assuming Reserves phase actions are completed and current_march_step becomes 'COMPLETE'
            print(f"Player {current_player_name}'s Reserves phase complete.")
            self._advance_player_turn()

    def _advance_player_turn(self):
        """Advances to the next player and resets to the First March phase."""
        gs = self.game_state
        gs.current_player_index = (gs.current_player_index + 1) % len(gs.players)
        gs.current_turn_phase = 'FIRST_MARCH'
        gs.current_march_step = 'DECIDE_MANEUVER'
        new_player_name = gs.players[gs.current_player_index].name
        print(f"Turn advanced. It is now {new_player_name}'s turn (First March).")

    def process_maneuver_decision(self, will_maneuver: bool):
        """Processes the player's decision on whether to maneuver."""
        gs = self.game_state
        if not (gs.game_phase == 'GAMEPLAY' and 
                gs.current_turn_phase in ['FIRST_MARCH', 'SECOND_MARCH'] and # Maneuver in march phases
                gs.current_march_step == 'DECIDE_MANEUVER'):
            print(f"Error: Not in correct state for maneuver decision. Phase: {gs.current_turn_phase}, Step: {gs.current_march_step}")
            return

        current_player_name = gs.players[gs.current_player_index].name
        if will_maneuver:
            gs.current_march_step = 'AWAITING_MANEUVER_INPUT'
            print(f"Player {current_player_name} ({gs.current_turn_phase}) chose to maneuver. Awaiting input.")
        else:
            gs.current_march_step = 'ROLL_FOR_MARCH'
            print(f"Player {current_player_name} ({gs.current_turn_phase}) chose not to maneuver. Proceeding to roll for march.")
        # After this, the UI would update. If 'ROLL_FOR_MARCH', the UI for rolling dice would appear.
        # Once that's submitted, a method like 'process_march_roll(results)' would be called.
        # 'process_march_roll' would then, after applying roll effects, set 
        # gs.current_march_step = 'COMPLETE' and then call self._advance_to_next_phase_or_player().

    def draw(self, screen: pygame.Surface):
        """
        Draws the current game state.
        """
        if self.game_state.game_phase == 'GAMEPLAY': # Or other conditions as needed
            self._draw_player_panels(screen)
            self._draw_terrain_info(screen)
            self._draw_current_prompt(screen)
    
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
        
        current_terrain_y_start = start_y + 20 # Y-coordinate for the top of the current terrain's info
        all_terrains = self.game_state.terrains + ([self.game_state.frontier_terrain] if self.game_state.frontier_terrain else [])
        
        for terrain in all_terrains:
            y_cursor = current_terrain_y_start # Reset y_cursor for each terrain

            # Terrain Name
            name_text = f"{terrain.owner_name}'s {terrain.type}"
            name_surf = self.font_medium.render(name_text, True, "white")
            screen.blit(name_surf, (start_x + 20, y_cursor))
            y_cursor += name_surf.get_height() + 5 # Add padding

            # Distance
            dist_text = f"Distance: {terrain.current_value or 'Not Set'}"
            dist_surf = self.font_small.render(dist_text, True, "#AAAAAA")
            screen.blit(dist_surf, (start_x + 20, y_cursor))
            y_cursor += dist_surf.get_height() + 5 # Add padding

            # Armies Present Label
            armies_label_surf = self.font_small.render("Armies Present:", True, "#CCCCCC")
            screen.blit(armies_label_surf, (start_x + 20, y_cursor))
            y_cursor += armies_label_surf.get_height() + 2 # Smaller padding before list

            army_detail_indent_x = start_x + 30 # Indent for the list of armies

            if terrain.armies_present:
                player_army_map = {}
                for army_detail in terrain.armies_present:
                    player_name = army_detail.get('player_name', 'Unknown Player')
                    # Use custom name if available, else fall back to army_type, then a generic default
                    army_name = army_detail.get('army_name') or army_detail.get('army_type', 'Unknown Army')
                    if player_name not in player_army_map:
                        player_army_map[player_name] = [] # Use a list to store army names/types for this player
                    player_army_map[player_name].append(army_name)
                
                for player_name, army_types_set in player_army_map.items():
                    # Display player name and then list their armies on separate lines or comma-separated
                    # Let's list them comma-separated for now, indented
                    armies_list_str = ", ".join(sorted(player_army_map[player_name])) # Sort army names for consistency
                    part_text = f"{player_name}: {armies_list_str}"
                    part_surf = self.font_small.render(part_text, True, "#CCCCCC")
                    screen.blit(part_surf, (army_detail_indent_x, y_cursor))
                    y_cursor += part_surf.get_height() # Move to next line for next player's army info
            else:
                none_surf = self.font_small.render("None", True, "#CCCCCC")
                screen.blit(none_surf, (army_detail_indent_x, y_cursor))
                y_cursor += none_surf.get_height()

            current_terrain_y_start = y_cursor + 15 # Add padding for the next terrain block
            
    def _draw_current_prompt(self, screen: pygame.Surface):
        """Draws the central prompt for the player's action."""
        width, height = screen.get_width(), screen.get_height()
        prompt_text = ""

        gs = self.game_state
        current_player_name = gs.players[gs.current_player_index].name

        if gs.game_phase == 'GAMEPLAY':
            if gs.current_turn_phase in ['FIRST_MARCH', 'SECOND_MARCH']:
                if gs.current_march_step == 'DECIDE_MANEUVER':
                    prompt_text = f"{current_player_name}, do you want to Maneuver for {gs.current_turn_phase.replace('_', ' ')}?"
                elif gs.current_march_step == 'AWAITING_MANEUVER_INPUT':
                    prompt_text = f"{current_player_name}, select army and target for {gs.current_turn_phase.replace('_', ' ')} maneuver."
                elif gs.current_march_step == 'ROLL_FOR_MARCH':
                    prompt_text = f"{current_player_name}, roll for your {gs.current_turn_phase.replace('_', ' ')}."
            # Add prompts for 'RESERVES' phase and other steps as they are implemented
        
        if prompt_text:
            prompt_surf = self.font_medium.render(prompt_text, True, "white")
            # Draw a simple background for the prompt
            bg_rect = prompt_surf.get_rect(center=(width / 2, height / 2)).inflate(40, 30)
            prompt_bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            prompt_bg_surf.fill((20, 20, 20, 180))
            screen.blit(prompt_bg_surf, bg_rect)
            
            prompt_rect = prompt_surf.get_rect(center=bg_rect.center)
            screen.blit(prompt_surf, prompt_rect)