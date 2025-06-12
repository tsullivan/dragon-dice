import pygame
from ui_manager import UIManager
from engine import GameEngine
from models import PlayerSetupData

def main():
    # --- PyGame and Font Initialization ---
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    pygame.display.set_caption("Dragon Dice Companion")
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

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
        "current_frontier_terrain": None,
        # Engine setup selections
        "current_first_player_selection": None,
        "current_frontier_selection": None,
        # The game itself
        "game_engine": None,
        # State trackers for efficient UI updates
        "ui_needs_update": True,
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
            return

        app_state["all_player_setups"].append({
            "name": app_state['current_name'],
            "home_terrain": app_state['current_home_terrain'],
            "frontier_terrain": app_state['current_frontier_terrain'],
        })

        if app_state["current_setup_index"] < app_state["num_players"] - 1:
            app_state["current_setup_index"] += 1
            app_state["current_name"] = f"Player {app_state['current_setup_index'] + 1}"
            app_state["current_home_terrain"] = None
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


    # --- Main Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                app_state["ui_needs_update"] = True

            # Pass event to UI manager to handle button clicks and text input
            updated_text = ui_manager.handle_event(event)
            if updated_text is not None:
                app_state['current_name'] = updated_text
                app_state["ui_needs_update"] = True

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
                        "total_players": app_state["num_players"]
                    },
                    {
                        'on_home_select': lambda t: handle_selection("current_home_terrain", t),
                        'on_frontier_select': lambda t: handle_selection("current_frontier_terrain", t),
                        'on_next': handle_next_player
                    }
                )
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
                    # Logic for turn-based gameplay UI will go here
                    pass

            app_state["ui_needs_update"] = False # UI is now up to date

        # --- Drawing ---
        screen.fill("#404040")

        if app_state["screen"] == "welcome":
            title_surf = font_large.render("Welcome to Dragon Dice!", True, "white")
            screen.blit(title_surf, (screen.get_width() / 2 - title_surf.get_width() / 2, 150))
            # ... draw other labels
        
        elif app_state["screen"] == "player_setup":
            title_text = f"Player {app_state['current_setup_index'] + 1} Setup"
            title_surf = font_large.render(title_text, True, "white")
            screen.blit(title_surf, (screen.get_width() / 2 - title_surf.get_width() / 2, 80))
            # ... draw other labels

        elif app_state["screen"] == "gameplay":
            app_state["game_engine"].draw(screen)

        ui_manager.draw(screen) # UIManager draws its elements (buttons, inputs) on top
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()