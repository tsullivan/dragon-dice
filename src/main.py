import pygame
from ui_manager import UIManager
from engine import GameEngine
from models import PlayerSetupData
from help_texts import HELP_TEXTS
from ui_utils import blit_text_wrap

def main():
    # --- PyGame and Font Initialization ---
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Dragon Dice Companion")
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    font_help = pygame.font.Font(None, 22) # For help text

    # --- High-Level Application State ---
    app_state = {
        "screen": "welcome",
        # Welcome screen selections
        "num_players": None,
        "point_value": None,
        # Player setup state
        "all_player_setups": [],
        "current_setup_index": 0,
        "current_name": "",
        "current_home_terrain": None,
        "current_home_army_name": "",
        "current_horde_army_name": "",
        "current_campaign_army_name": "",
        "current_frontier_terrain": None,
        # Engine setup selections
        "current_first_player_selection": None,
        "current_frontier_selection": None,
        # The game itself
        "game_engine": None,
        # State trackers for efficient UI updates
        "ui_needs_update": True,
        "help_scroll_offset_y": 0,
        "total_help_text_height": 0,
        "current_rendered_help_key": None, # Tracks when help text content changes
    }
    
    ui_manager = UIManager()


    # --- Callback Functions (The "Controller" Logic) ---

    def handle_selection(state_key, value):
        """Generic handler to update state and flag UI for a rebuild."""
        if app_state[state_key] != value:
            app_state[state_key] = value
            app_state["ui_needs_update"] = True
    
    def proceed_to_setup():
        """Transitions from the welcome screen to player setup."""
        if not app_state["num_players"] or not app_state["point_value"]:
            return
        app_state["screen"] = "player_setup"
        app_state["current_name"] = f"Player {app_state['current_setup_index'] + 1}"
        app_state["ui_needs_update"] = True

    def handle_next_player():
        """Saves the current player's setup and moves to the next, or starts the game."""
        if not app_state['current_name'] or not app_state['current_home_terrain'] or not app_state['current_frontier_terrain']:
            # Add checks for army names if they become mandatory
            return

        app_state["all_player_setups"].append({
            "name": app_state['current_name'],
            "home_terrain": app_state['current_home_terrain'],
            "home_army_name": app_state['current_home_army_name'],
            "horde_army_name": app_state['current_horde_army_name'],
            "campaign_army_name": app_state['current_campaign_army_name'],
            "frontier_terrain": app_state['current_frontier_terrain'],
        })

        if app_state["current_setup_index"] < app_state["num_players"] - 1:
            app_state["current_setup_index"] += 1
            app_state["current_name"] = f"Player {app_state['current_setup_index'] + 1}"
            app_state["current_home_terrain"] = None
            app_state["current_home_army_name"] = ""
            app_state["current_horde_army_name"] = ""
            app_state["current_campaign_army_name"] = ""
            app_state["current_frontier_terrain"] = None
        else:
            app_state["game_engine"] = GameEngine(app_state["point_value"], app_state["all_player_setups"])
            app_state["screen"] = "gameplay"
        
        app_state["ui_needs_update"] = True

    def handle_frontier_submission():
        """Submits the chosen frontier and first player to the game engine."""
        selections = app_state
        if selections["current_frontier_selection"] and selections["current_first_player_selection"]:
            selections["game_engine"].submit_frontier_selection(
                selections["current_frontier_selection"],
                selections["current_first_player_selection"]
            )
            app_state["ui_needs_update"] = True
    
    def handle_rolls_submission(input_boxes):
        """Submits the terrain distance rolls to the game engine."""
        rolls = [
            {"terrain_id": item["terrain_id"], "value": item["input_box"].text}
            for item in input_boxes
        ]
        app_state["game_engine"].submit_distance_rolls(rolls)
        app_state["ui_needs_update"] = True

    def handle_maneuver_decision(will_maneuver: bool):
        """Handles the player's maneuver decision by calling the engine."""
        engine = app_state.get("game_engine")
        if engine:
            engine.process_maneuver_decision(will_maneuver)
            app_state["ui_needs_update"] = True


    # --- Main Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                app_state["ui_needs_update"] = True

            if event.type == pygame.MOUSEWHEEL:
                # Check if mouse is over the help panel before processing scroll
                # help_panel_rect is defined in the drawing section, ensure it's accurate or pass screen dimensions
                # For simplicity, we assume help_panel_rect from the last frame is a decent check
                # A more robust way would be to calculate it here based on current_screen_height/width
                temp_help_panel_rect = pygame.Rect(40, screen.get_height() - 130 - 20, screen.get_width() - 80, 130)
                if temp_help_panel_rect.collidepoint(pygame.mouse.get_pos()):
                    scroll_speed = 30 # Pixels per wheel tick
                    app_state["help_scroll_offset_y"] -= event.y * scroll_speed
                    
                    # Clamp scroll offset
                    max_scroll = max(0, app_state["total_help_text_height"] - (temp_help_panel_rect.height - 2 * 10)) # 10 is HELP_PANEL_PADDING_Y
                    app_state["help_scroll_offset_y"] = max(0, min(app_state["help_scroll_offset_y"], max_scroll))

            # Pass event to UI manager to handle button clicks and text input
            updated_text = ui_manager.handle_event(event)
            # If updated_text is not None, it means a TextInputBox processed a KEYDOWN event.
            # We update the app_state's current_name, but we do NOT need to trigger a full
            # UI rebuild for this, as the TextInputBox will draw its own updated text.
            # Button clicks, handled by callbacks, will correctly set ui_needs_update.
            if updated_text is not None:
                # Determine which input box was active based on current screen/state
                if app_state["screen"] == "player_setup":
                    # This is a simplified approach assuming only one text input is active at a time
                    # or that the order of inputs is consistent. A more robust solution
                    # would involve the TextInputBox returning an identifier.
                    # For now, we'll assume the first active text box is the name,
                    # and subsequent ones (if any) are army names. This needs refinement.
                    # Let's update based on which input box is currently active in UIManager
                    # This requires UIManager to track which box returned text
                    pass # UIManager now handles returning text from the active box

        # --- UI & State Update Logic ---
        if app_state["ui_needs_update"]:
            ui_manager.elements = [] # Clear all previous UI elements
            
            if app_state["screen"] == "welcome":
                ui_manager.create_welcome_ui(
                    {"num_players": app_state["num_players"], "point_value": app_state["point_value"]},
                    {
                        'on_player_select': lambda n: handle_selection("num_players", n),
                        'on_point_select': lambda p: handle_selection("point_value", p),
                        'on_proceed': proceed_to_setup
                    }
                )
            elif app_state["screen"] == "player_setup":
                ui_manager.create_player_setup_ui(
                    app_state['current_setup_index'],
                    {
                        "name": app_state["current_name"],
                        "home_terrain": app_state["current_home_terrain"],
                        "frontier_terrain": app_state["current_frontier_terrain"],
                        "home_army_name": app_state["current_home_army_name"],
                        "horde_army_name": app_state["current_horde_army_name"],
                        "campaign_army_name": app_state["current_campaign_army_name"],
                        "total_players": app_state["num_players"]
                    },
                    {
                        'on_home_select': lambda t: handle_selection("current_home_terrain", t),
                        'on_frontier_select': lambda t: handle_selection("current_frontier_terrain", t),
                        'on_next': handle_next_player
                    }
                ) # UIManager will create the text boxes. We need to handle their input below.
                # After creating UI, find the text boxes and link their input to app_state
                ui_manager.link_text_inputs_to_state(app_state) # New method in UIManager

            elif app_state["screen"] == "gameplay":
                engine_state = app_state["game_engine"].game_state
                if engine_state.game_phase == 'SETUP':
                    if engine_state.setup_step == 'DETERMINING_FRONTIER':
                        ui_manager.create_frontier_selection_ui(
                            engine_state.players,
                            {"first_player": app_state["current_first_player_selection"], 
                             "frontier_terrain": app_state["current_frontier_selection"]},
                            {
                                'on_first_player_select': lambda p: handle_selection("current_first_player_selection", p),
                                'on_frontier_select': lambda t: handle_selection("current_frontier_selection", t),
                                'on_submit': handle_frontier_submission
                            }
                        )
                    elif engine_state.setup_step == 'AWAITING_DISTANCE_ROLLS':
                        terrains = engine_state.terrains + ([engine_state.frontier_terrain] or [])
                        ui_manager.create_distance_rolls_ui(terrains, {'on_submit': handle_rolls_submission})
                
                elif engine_state.game_phase == 'GAMEPLAY':
                    # Current player's turn actions
                    if engine_state.current_turn_phase == 'FIRST_MARCH':
                        if engine_state.current_march_step == 'DECIDE_MANEUVER':
                            ui_manager.create_maneuver_decision_ui(
                                {
                                    'on_maneuver_yes': lambda: handle_maneuver_decision(True),
                                    'on_maneuver_no': lambda: handle_maneuver_decision(False)
                                }
                            )
                        # elif engine_state.current_march_step == 'AWAITING_MANEUVER_INPUT':
                        #     # Future: ui_manager.create_maneuver_input_ui(...)
                        #     pass 
                        # elif engine_state.current_march_step == 'ROLL_FOR_MARCH':
                        #     # Future: ui_manager.create_march_roll_ui(...)
                        #     pass
                            
            app_state["ui_needs_update"] = False # UI is now up to date

        # --- Drawing ---
        screen.fill("#404040")
        
        current_screen_width, current_screen_height = screen.get_size()

        # --- Help Panel Constants ---
        HELP_PANEL_TOTAL_HEIGHT = 130  # Overall visual height of the panel
        HELP_PANEL_BOTTOM_MARGIN = 20
        help_panel_rect = pygame.Rect(40, current_screen_height - HELP_PANEL_TOTAL_HEIGHT - HELP_PANEL_BOTTOM_MARGIN, current_screen_width - 80, HELP_PANEL_TOTAL_HEIGHT)
        HELP_PANEL_PADDING_X = 15
        HELP_PANEL_PADDING_Y = 10
        help_content_max_visible_height = help_panel_rect.height - 2 * HELP_PANEL_PADDING_Y
        help_content_width = help_panel_rect.width - 2 * HELP_PANEL_PADDING_X

        if app_state["screen"] == "welcome":
            title_surf = font_large.render("Welcome to Dragon Dice!", True, "white")
            title_rect = title_surf.get_rect(center=(screen.get_width() / 2, 150))
            screen.blit(title_surf, title_rect)

            players_label_surf = font_medium.render("Choose number of players:", True, "white")
            players_label_rect = players_label_surf.get_rect(center=(screen.get_width() / 2, 270))
            screen.blit(players_label_surf, players_label_rect)

            points_label_surf = font_medium.render("Choose army point size:", True, "white")
            points_label_rect = points_label_surf.get_rect(center=(screen.get_width() / 2, 370))
            screen.blit(points_label_surf, points_label_rect)
        
        elif app_state["screen"] == "player_setup":
            title_text = f"Player {app_state['current_setup_index'] + 1} Setup"
            title_surf = font_large.render(title_text, True, "white")
            title_rect = title_surf.get_rect(center=(screen.get_width() / 2, 80))
            screen.blit(title_surf, title_rect)

            name_label_surf = font_medium.render("Enter Player Name:", True, "white")
            name_label_rect = name_label_surf.get_rect(center=(screen.get_width() / 2, 160))
            screen.blit(name_label_surf, name_label_rect)

            # Labels for Army Names
            home_army_label_surf = font_medium.render("Name your Home Army:", True, "white")
            home_army_label_rect = home_army_label_surf.get_rect(center=(screen.get_width() / 2, 250))
            screen.blit(home_army_label_surf, home_army_label_rect)

            horde_army_label_surf = font_medium.render("Name your Horde Army:", True, "white")
            horde_army_label_rect = horde_army_label_surf.get_rect(center=(screen.get_width() / 2, 340))
            screen.blit(horde_army_label_surf, horde_army_label_rect)

            campaign_army_label_surf = font_medium.render("Name your Campaign Army:", True, "white")
            campaign_army_label_rect = campaign_army_label_surf.get_rect(center=(screen.get_width() / 2, 430))
            screen.blit(campaign_army_label_surf, campaign_army_label_rect)

            home_terrain_label_surf = font_medium.render("Choose Home Terrain:", True, "white")
            home_terrain_label_rect = home_terrain_label_surf.get_rect(center=(screen.get_width() / 2 - 200, 240)) # Adjusted for button layout
            screen.blit(home_terrain_label_surf, home_terrain_label_rect)

            frontier_proposal_label_surf = font_medium.render("Propose Frontier Terrain:", True, "white")
            frontier_proposal_label_rect = frontier_proposal_label_surf.get_rect(center=(screen.get_width() / 2 + 200, 240)) # Adjusted for button layout
            screen.blit(frontier_proposal_label_surf, frontier_proposal_label_rect)

        elif app_state["screen"] == "gameplay":
            app_state["game_engine"].draw(screen)

        # --- Drawing Help Panel (Common to most screens) ---
        current_help_key = None
        if app_state["screen"] == "welcome":
            current_help_key = "welcome"
        elif app_state["screen"] == "player_setup":
            current_help_key = "player_setup"
        elif app_state["screen"] == "gameplay" and app_state["game_engine"]:
            engine_state = app_state["game_engine"].game_state
            if engine_state.game_phase == 'SETUP':
                # Titles and labels for gameplay setup steps drawn here, before engine.draw()
                if engine_state.setup_step == 'DETERMINING_FRONTIER':
                    current_help_key = "gameplay_setup_frontier"
                    title_surf = font_large.render("Determine Frontier & First Player", True, "white")
                    title_rect = title_surf.get_rect(center=(screen.get_width() / 2, 80))
                    screen.blit(title_surf, title_rect)

                    first_player_label_surf = font_medium.render("Select First Player:", True, "white")
                    first_player_label_rect = first_player_label_surf.get_rect(center=(screen.get_width() / 2 - 200, 240))
                    screen.blit(first_player_label_surf, first_player_label_rect)

                    frontier_select_label_surf = font_medium.render("Select Frontier Terrain:", True, "white")
                    frontier_select_label_rect = frontier_select_label_surf.get_rect(center=(screen.get_width() / 2 + 200, 240))
                    screen.blit(frontier_select_label_surf, frontier_select_label_rect)

                elif engine_state.setup_step == 'AWAITING_DISTANCE_ROLLS':
                    current_help_key = "gameplay_setup_distance"
                    title_surf = font_large.render("Enter Starting Distances", True, "white")
                    title_rect = title_surf.get_rect(center=(screen.get_width() / 2, 80))
                    screen.blit(title_surf, title_rect)
                    # Labels for individual roll inputs are handled by UIManager in this case

            elif engine_state.game_phase == 'GAMEPLAY':
                if engine_state.current_turn_phase in ['FIRST_MARCH', 'SECOND_MARCH']:
                    if engine_state.current_march_step == 'DECIDE_MANEUVER':
                        current_help_key = "gameplay_maneuver_decision"
                    elif engine_state.current_march_step == 'AWAITING_MANEUVER_INPUT':
                        current_help_key = "gameplay_maneuver_input"
                    elif engine_state.current_march_step == 'ROLL_FOR_MARCH':
                        current_help_key = "gameplay_roll_for_march"
                elif engine_state.current_turn_phase == 'RESERVES': # Assuming a general help for reserves for now
                    current_help_key = "gameplay_reserves"


        if current_help_key and current_help_key in HELP_TEXTS:
            # Recalculate total text height if help content changed
            if app_state["current_rendered_help_key"] != current_help_key:
                text_to_render = HELP_TEXTS[current_help_key]
                calculated_total_height = blit_text_wrap(None, text_to_render, (0,0), font_help, "white", help_content_width, 4)
                app_state["total_help_text_height"] = calculated_total_height
                app_state["current_rendered_help_key"] = current_help_key
                app_state["help_scroll_offset_y"] = 0 # Reset scroll on new text

            # Draw the outer panel background
            help_panel_bg_surface = pygame.Surface(help_panel_rect.size, pygame.SRCALPHA)
            help_panel_bg_surface.fill((20, 20, 20, 210)) 
            screen.blit(help_panel_bg_surface, help_panel_rect.topleft)
            pygame.draw.rect(screen, (80, 80, 80), help_panel_rect, 1) # Border

            # Create a surface for the scrollable content (clipping)
            help_content_surface = pygame.Surface((help_content_width, help_content_max_visible_height), pygame.SRCALPHA)
            help_content_surface.fill((0,0,0,0)) # Transparent

            # Blit the wrapped text onto this content surface, offset by scrolling
            blit_text_wrap(help_content_surface, HELP_TEXTS[current_help_key],
                           (0, -app_state["help_scroll_offset_y"]), # Start drawing at y=0, scrolled up by offset
                           font_help, (220, 220, 220),
                           help_content_width)

            # Blit the content surface (with clipped text) onto the main screen
            screen.blit(help_content_surface, (help_panel_rect.left + HELP_PANEL_PADDING_X, help_panel_rect.top + HELP_PANEL_PADDING_Y))

            # Optional: Draw a scrollbar indicator
            if app_state["total_help_text_height"] > help_content_max_visible_height:
                scrollbar_track_height = help_content_max_visible_height - 4 # Small padding for scrollbar
                thumb_height_ratio = help_content_max_visible_height / app_state["total_help_text_height"]
                scrollbar_thumb_height = max(10, scrollbar_track_height * thumb_height_ratio) # Min thumb height 10px
                scroll_ratio = app_state["help_scroll_offset_y"] / (app_state["total_help_text_height"] - help_content_max_visible_height)
                scrollbar_thumb_y = (help_panel_rect.top + HELP_PANEL_PADDING_Y + 2) + scroll_ratio * (scrollbar_track_height - scrollbar_thumb_height)
                scrollbar_thumb_rect = pygame.Rect(help_panel_rect.right - HELP_PANEL_PADDING_X + 3, scrollbar_thumb_y, 8, scrollbar_thumb_height)
                pygame.draw.rect(screen, (100, 100, 100), scrollbar_thumb_rect, border_radius=4)

        ui_manager.draw(screen) # UIManager draws its elements (buttons, inputs) on top
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()