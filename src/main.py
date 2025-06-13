import pygame
from ui import UIManager
from engine import GameEngine
from models import PlayerSetupData
import help_texts
from ui_utils import blit_text_wrap
import callbacks

def main():
    # --- PyGame and Font Initialization ---
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Dragon Dice Companion")
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    font_help = pygame.font.Font(None, 22)

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
        "current_home_army_points": "",
        "current_horde_army_points": "",
        "current_campaign_army_points": "",
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
        "player_setup_panel_scroll_x": 0,
        "player_setup_panel_content_width": 0, # Calculated by UIManager
        "player_setup_panel_rect": None, # Calculated based on screen size
    }
    
    ui_manager = UIManager()

    # --- Main Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                app_state["ui_needs_update"] = True
                # Invalidate panel rect so it's recalculated
                app_state["player_setup_panel_rect"] = None

            if event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                # Horizontal scroll for player setup panel
                if app_state["screen"] == "player_setup" and app_state["player_setup_panel_rect"] and app_state["player_setup_panel_rect"].collidepoint(mouse_pos):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        scroll_speed = 40
                        app_state["player_setup_panel_scroll_x"] -= event.y * scroll_speed
                        max_scroll_x = max(0, app_state["player_setup_panel_content_width"] - app_state["player_setup_panel_rect"].width)
                        app_state["player_setup_panel_scroll_x"] = max(0, min(app_state["player_setup_panel_scroll_x"], max_scroll_x))
                # Vertical scroll for help panel
                elif app_state.get("help_panel_rect") and app_state["help_panel_rect"].collidepoint(mouse_pos): # help_panel_rect is now in app_state
                    help_panel_rect = app_state["help_panel_rect"] # Use the stored rect
                    scroll_speed = 30 # Pixels per wheel tick
                    app_state["help_scroll_offset_y"] -= event.y * scroll_speed
                    
                    # Clamp scroll offset
                    max_scroll = max(0, app_state["total_help_text_height"] - (help_panel_rect.height - 2 * 10)) # 10 is HELP_PANEL_PADDING_Y
                    app_state["help_scroll_offset_y"] = max(0, min(app_state["help_scroll_offset_y"], max_scroll))

            # Pass event to UI manager to handle button clicks and text input
            # For player_setup, pass panel_rect and scroll_x for coordinate transformation
            event_handling_args = {}
            if app_state["screen"] == "player_setup" and app_state["player_setup_panel_rect"]:
                event_handling_args["panel_rect_on_screen"] = app_state["player_setup_panel_rect"]
                event_handling_args["scroll_offset_x"] = app_state["player_setup_panel_scroll_x"]

            state_updates = ui_manager.handle_event(event, **event_handling_args)
            
            if state_updates:
                for key, value in state_updates.items():
                    # Map TextInputBox IDs to app_state keys
                    if key == "player_name": app_state["current_name"] = value
                    elif key == "home_army_name": app_state["current_home_army_name"] = value
                    elif key == "horde_army_name": app_state["current_horde_army_name"] = value
                    elif key == "campaign_army_name": app_state["current_campaign_army_name"] = value
                    elif key == "home_army_points": app_state["current_home_army_points"] = value
                    elif key == "horde_army_points": app_state["current_horde_army_points"] = value
                    elif key == "campaign_army_points": app_state["current_campaign_army_points"] = value
                    # Add other mappings if new text inputs are added with different IDs
                    app_state["ui_needs_update"] = True # Trigger UI refresh for validation display
                # No ui_needs_update = True here, as TextInputBox draws its own text.
                # However, if button active states depend on these, then it might be needed.
                # For now, the "Next/Start" button re-evaluates its active state during UI rebuild.

        # --- UI & State Update Logic ---
        if app_state["ui_needs_update"]:
            ui_manager.panel_elements = [] # Clear panel UI elements
            ui_manager.fixed_elements = [] # Clear fixed UI elements
            
            if app_state["screen"] == "welcome":
                # Reset player setup specific states when returning to welcome
                app_state["all_player_setups"] = []
                app_state["current_setup_index"] = 0
                app_state["current_name"] = ""
                app_state["current_home_terrain"] = None
                app_state["current_home_army_name"] = ""
                app_state["current_horde_army_name"] = ""
                app_state["current_campaign_army_name"] = ""
                app_state["current_home_army_points"] = ""
                app_state["current_horde_army_points"] = ""
                app_state["current_campaign_army_points"] = ""
                app_state["current_frontier_terrain"] = None
                app_state["game_engine"] = None # Clear previous game engine

                ui_manager.create_welcome_ui(
                    {"num_players": app_state["num_players"], "point_value": app_state["point_value"]},
                    {
                        'on_player_select': lambda n: callbacks.handle_selection(app_state, "num_players", n),
                        'on_point_select': lambda p: callbacks.handle_selection(app_state, "point_value", p),
                        'on_proceed': lambda: callbacks.proceed_to_setup(app_state)
                    }
                )
            elif app_state["screen"] == "player_setup":
                # Calculate points for UI display
                current_total_allocated = 0
                max_points_per_army = 0
                game_point_limit = app_state.get("point_value", 0)
                if game_point_limit: # Ensure point_value is set
                    max_points_per_army = game_point_limit // 2
                    try:
                        current_total_allocated += int(app_state.get("current_home_army_points") or 0)
                        current_total_allocated += int(app_state.get("current_campaign_army_points") or 0)
                        if app_state["num_players"] > 1:
                            current_total_allocated += int(app_state.get("current_horde_army_points") or 0)
                    except ValueError:
                        pass # Will be handled by UIManager's validation for button state

                content_width = ui_manager.create_player_setup_ui(
                    app_state['current_setup_index'],
                    {
                        "name": app_state["current_name"],
                        "home_terrain": app_state["current_home_terrain"],
                        "frontier_terrain": app_state["current_frontier_terrain"],
                        "home_army_name": app_state["current_home_army_name"],
                        "horde_army_name": app_state["current_horde_army_name"],
                        "campaign_army_name": app_state["current_campaign_army_name"],
                        "home_army_points": app_state["current_home_army_points"],
                        "horde_army_points": app_state["current_horde_army_points"],
                        "campaign_army_points": app_state["current_campaign_army_points"],
                        "total_players": app_state["num_players"],
                        # For display and validation in UIManager
                        "game_point_limit": game_point_limit,
                        "current_total_allocated_points_str": str(current_total_allocated),
                        "max_points_per_army": max_points_per_army,
                    },
                    {
                        'on_prev_home_terrain': lambda: callbacks.handle_cycle_terrain(app_state, "current_home_terrain", -1),
                        'on_next_home_terrain': lambda: callbacks.handle_cycle_terrain(app_state, "current_home_terrain", 1),
                        'on_prev_frontier_proposal': lambda: callbacks.handle_cycle_terrain(app_state, "current_frontier_terrain", -1),
                        'on_next_frontier_proposal': lambda: callbacks.handle_cycle_terrain(app_state, "current_frontier_terrain", 1),
                        'on_next': lambda: callbacks.handle_next_player(app_state, GameEngine)
                    }
                )
                app_state["player_setup_panel_content_width"] = content_width

            elif app_state["screen"] == "gameplay":
                game_engine_instance = app_state.get("game_engine")
                if game_engine_instance:
                    engine_state = game_engine_instance.game_state
                    if engine_state.game_phase == 'SETUP':
                        if engine_state.setup_step == 'DETERMINING_FRONTIER':
                            ui_manager.create_frontier_selection_ui(
                                engine_state.players,
                                {"first_player": app_state["current_first_player_selection"], 
                                 "frontier_terrain": app_state["current_frontier_selection"]},
                                {
                                    'on_first_player_select': lambda p_name: callbacks.handle_selection(app_state, "current_first_player_selection", p_name),
                                    'on_frontier_select': lambda t_type: callbacks.handle_selection(app_state, "current_frontier_selection", t_type),
                                    'on_submit': lambda: callbacks.handle_frontier_submission(app_state)
                                }
                            )
                        elif engine_state.setup_step == 'AWAITING_DISTANCE_ROLLS':
                            terrains = engine_state.terrains + ([engine_state.frontier_terrain] if engine_state.frontier_terrain else [])
                            ui_manager.create_distance_rolls_ui(terrains, {'on_submit': lambda ib: callbacks.handle_rolls_submission(app_state, ib)})
                    
                    elif engine_state.game_phase == 'GAMEPLAY':
                        # Current player's turn actions
                        if engine_state.current_turn_phase == 'FIRST_MARCH': # Check current_turn_phase first
                            if engine_state.current_march_step == 'DECIDE_MANEUVER':
                                ui_manager.create_maneuver_decision_ui(
                                    {
                                        'on_maneuver_yes': lambda: callbacks.handle_maneuver_decision(app_state, True),
                                        'on_maneuver_no': lambda: callbacks.handle_maneuver_decision(app_state, False)
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
        # Store help_panel_rect in app_state for consistent access in event handling
        app_state["help_panel_rect"] = pygame.Rect(40, current_screen_height - HELP_PANEL_TOTAL_HEIGHT - HELP_PANEL_BOTTOM_MARGIN, current_screen_width - 80, HELP_PANEL_TOTAL_HEIGHT)
        help_panel_rect = app_state["help_panel_rect"] # Use local variable for drawing
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
            # --- Player Setup Screen Drawing ---
            title_text = f"Player {app_state['current_setup_index'] + 1} Setup"
            title_surf = font_large.render(title_text, True, "white")
            title_rect = title_surf.get_rect(center=(screen.get_width() / 2, 60)) # Title higher
            screen.blit(title_surf, title_rect)

            # Define the main panel for player setup content
            panel_margin_x = 50
            panel_margin_top = 120 # Space below title
            scrollbar_height_with_margin = 25 # 15 for scrollbar + 5 top margin + 5 bottom margin
            continue_button_y_pos = 510 # As set in UIManager
            continue_button_height_with_margin = 50 + 10 # Button height + margin below it before help panel
            
            # Panel bottom should be above the scrollbar, which is above the continue button
            panel_bottom_y = continue_button_y_pos - scrollbar_height_with_margin - 10 # 10px margin above scrollbar
            panel_height = panel_bottom_y - panel_margin_top
            
            # This calculation might be off if screen height changes; dynamic calculation is better.
            # For now, this aims to fit the image's relative spacing.
            panel_margin_bottom = current_screen_height - panel_margin_top - panel_height # Recalculate based on new panel_height
            
            if app_state["player_setup_panel_rect"] is None: # Calculate if not set or screen resized
                app_state["player_setup_panel_rect"] = pygame.Rect(
                    panel_margin_x,
                    panel_margin_top,
                    current_screen_width - 2 * panel_margin_x,
                    current_screen_height - panel_margin_top - panel_margin_bottom
                )
            panel_rect = app_state["player_setup_panel_rect"]

            # Create content surface (wider than panel_rect for scrolling)
            content_surface_width = max(panel_rect.width, app_state["player_setup_panel_content_width"])
            content_surface = pygame.Surface((content_surface_width, panel_rect.height), pygame.SRCALPHA)
            content_surface.fill((40, 45, 50)) # Opaque dark background for panel content area
            
            # UIManager draws its panel elements onto the content_surface
            ui_manager.draw_panel_content(content_surface)

            # Blit the scrollable part of content_surface onto the screen
            source_area_rect = pygame.Rect(app_state["player_setup_panel_scroll_x"], 0, panel_rect.width, panel_rect.height)
            screen.blit(content_surface, panel_rect.topleft, source_area_rect)

            # Draw horizontal scrollbar for the panel
            if app_state["player_setup_panel_content_width"] > panel_rect.width:
                scrollbar_height = 15
                scrollbar_track_y = panel_rect.bottom + 5 # A little below the panel
                scrollbar_track_rect = pygame.Rect(panel_rect.left, scrollbar_track_y, panel_rect.width, scrollbar_height -2) # slightly thinner track
                pygame.draw.rect(screen, (70, 70, 70), scrollbar_track_rect, border_radius=7) # Scrollbar track

                thumb_width_ratio = panel_rect.width / app_state["player_setup_panel_content_width"]
                scrollbar_thumb_width = max(20, scrollbar_track_rect.width * thumb_width_ratio)
                
                max_scroll_x_for_content = app_state["player_setup_panel_content_width"] - panel_rect.width
                if max_scroll_x_for_content > 0:
                    scroll_ratio_for_thumb = app_state["player_setup_panel_scroll_x"] / max_scroll_x_for_content
                else:
                    scroll_ratio_for_thumb = 0
                scrollbar_thumb_x = scrollbar_track_rect.left + scroll_ratio_for_thumb * (scrollbar_track_rect.width - scrollbar_thumb_width)
                scrollbar_thumb_rect = pygame.Rect(scrollbar_thumb_x, scrollbar_track_y, scrollbar_thumb_width, scrollbar_height -2)
                pygame.draw.rect(screen, (150, 150, 150), scrollbar_thumb_rect, border_radius=7) # Scrollbar thumb

            # Draw panel frame
            pygame.draw.rect(screen, (70, 80, 90), panel_rect, 2, border_radius=5) # Frame, border 2px

        elif app_state["screen"] == "gameplay":
            if app_state["game_engine"]:
                app_state["game_engine"].draw(screen)

        # --- Drawing Help Panel (Common to most screens) ---
        current_help_key = None
        if app_state["screen"] == "welcome":
            current_help_key = "welcome"
        elif app_state["screen"] == "player_setup":
            current_help_key = "player_setup"
        elif app_state["screen"] == "gameplay" and app_state["game_engine"]:
            engine_state = app_state["game_engine"].game_state # Already checked app_state["game_engine"]
            # Ensure engine_state is not None, though it should be guaranteed if game_engine exists
            if engine_state and engine_state.game_phase == 'SETUP':
                # Titles and labels for gameplay setup steps
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
            elif engine_state and engine_state.game_phase == 'GAMEPLAY':
                if engine_state.current_turn_phase in ['FIRST_MARCH', 'SECOND_MARCH']:
                    if engine_state.current_march_step == 'DECIDE_MANEUVER':
                        current_help_key = "gameplay_maneuver_decision"
                    elif engine_state.current_march_step == 'AWAITING_MANEUVER_INPUT':
                        current_help_key = "gameplay_maneuver_input"
                    elif engine_state.current_march_step == 'ROLL_FOR_MARCH':
                        current_help_key = "gameplay_roll_for_march"
                elif engine_state.current_turn_phase == 'RESERVES': # Assuming a general help for reserves for now
                    current_help_key = "gameplay_reserves"

        # Fetch and render help text using the new function-based approach
        text_to_render = ""
        if current_help_key:
            if current_help_key == "welcome":
                text_to_render = help_texts.welcome_text()
            elif current_help_key == "player_setup":
                text_to_render = help_texts.player_setup_text(
                    app_state['current_setup_index'] + 1,
                    app_state['num_players'],
                    app_state['point_value']
                )
            elif current_help_key == "gameplay_setup_frontier":
                text_to_render = help_texts.gameplay_setup_frontier_text()
            elif current_help_key == "gameplay_setup_distance":
                text_to_render = help_texts.gameplay_setup_distance_text()
            else: # Gameplay help texts that require game_engine
                game_engine_instance = app_state.get("game_engine")
                if game_engine_instance:
                    gs = game_engine_instance.game_state
                    if current_help_key == "gameplay_maneuver_decision":
                        player_name = gs.players[gs.current_player_index].name
                        turn_phase_display = gs.current_turn_phase.replace('_', ' ').title()
                        text_to_render = help_texts.gameplay_maneuver_decision_text(player_name, turn_phase_display)
                    elif current_help_key == "gameplay_maneuver_input":
                        player_name = gs.players[gs.current_player_index].name
                        turn_phase_display = gs.current_turn_phase.replace('_', ' ').title()
                        text_to_render = help_texts.gameplay_maneuver_input_text(player_name, turn_phase_display)
                    elif current_help_key == "gameplay_roll_for_march":
                        player_name = gs.players[gs.current_player_index].name
                        turn_phase_display = gs.current_turn_phase.replace('_', ' ').title()
                        action_type = "March" # Placeholder
                        text_to_render = help_texts.gameplay_roll_for_march_text(player_name, turn_phase_display, action_type)
                    elif current_help_key == "gameplay_reserves":
                        player_name = gs.players[gs.current_player_index].name
                        text_to_render = help_texts.gameplay_reserves_text(player_name)
                # Fallback or general gameplay help if specific context not met but key is gameplay_general
                elif current_help_key == "gameplay_general":
                    text_to_render = help_texts.gameplay_general_text()

        if text_to_render:
            # Recalculate total text height if help content changed
            if app_state["current_rendered_help_key"] != current_help_key:
                calculated_total_height = blit_text_wrap(None, text_to_render, (0,0), font_help, "white", help_content_width, 4)
                app_state["total_help_text_height"] = calculated_total_height
                app_state["current_rendered_help_key"] = current_help_key
                app_state["help_scroll_offset_y"] = 0 # Reset scroll on new text

            if text_to_render: # Ensure we have text before trying to draw
                # Draw the outer panel background
                help_panel_bg_surface = pygame.Surface(help_panel_rect.size, pygame.SRCALPHA)
                help_panel_bg_surface.fill((20, 20, 20, 210)) 
                screen.blit(help_panel_bg_surface, help_panel_rect.topleft)
                pygame.draw.rect(screen, (80, 80, 80), help_panel_rect, 1) # Border

                # Create a surface for the scrollable content (clipping)
                help_content_surface = pygame.Surface((help_content_width, help_content_max_visible_height), pygame.SRCALPHA)
                help_content_surface.fill((0,0,0,0)) # Transparent

                # Blit the wrapped text onto this content surface, offset by scrolling
                blit_text_wrap(help_content_surface, text_to_render,
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
                    if (app_state["total_help_text_height"] - help_content_max_visible_height) > 0: # Avoid division by zero
                        scroll_ratio = app_state["help_scroll_offset_y"] / (app_state["total_help_text_height"] - help_content_max_visible_height)
                    else:
                        scroll_ratio = 0
                    scrollbar_thumb_y = (help_panel_rect.top + HELP_PANEL_PADDING_Y + 2) + scroll_ratio * (scrollbar_track_height - scrollbar_thumb_height)
                    scrollbar_thumb_rect = pygame.Rect(help_panel_rect.right - HELP_PANEL_PADDING_X + 3, scrollbar_thumb_y, 8, scrollbar_thumb_height)
                    pygame.draw.rect(screen, (100, 100, 100), scrollbar_thumb_rect, border_radius=4)

        # UIManager draws its fixed elements (buttons, inputs not on a panel)
        ui_manager.draw_fixed_content(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()