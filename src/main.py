import pygame
from src.ui_manager import UIManager
from src.engine import GameEngine

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Dragon Dice Companion")
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 32)

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
        "current_frontier_terrain": None, # For future implementation
        # The game itself
        "game_engine": None,
    }
    
    ui_manager = UIManager()

    def update_ui():
        """A single function to call to rebuild the UI for the current state."""
        if app_state["screen"] == "welcome":
            selections = {"num_players": app_state["num_players"], "point_value": app_state["point_value"]}
            callbacks = {
                'on_player_select': lambda n: app_state.update(num_players=n),
                'on_point_select': lambda p: app_state.update(point_value=p),
                'on_proceed': proceed_to_setup
            }
            ui_manager.create_welcome_ui(selections, callbacks)
        
        elif app_state["screen"] == "player_setup":
            selections = {
                "name": app_state["current_name"],
                "home_terrain": app_state["current_home_terrain"],
                "total_players": app_state["num_players"]
            }
            callbacks = {
                'on_home_select': lambda t: app_state.update(current_home_terrain=t),
                'on_next': handle_next_player
            }
            ui_manager.create_player_setup_ui(app_state['current_setup_index'], selections, callbacks)

    def proceed_to_setup():
        if not app_state["num_players"] or not app_state["point_value"]:
            print("Please make all selections first.")
            return
        
        app_state["screen"] = "player_setup"
        app_state["current_name"] = f"Player {app_state['current_setup_index'] + 1}"
        update_ui() # Rebuild UI for the next screen

    def handle_next_player():
        # Validation
        if not app_state['current_name'] or not app_state['current_home_terrain']:
            print("Please enter a name and select a terrain.")
            return

        # Save the current player's data
        app_state["all_player_setups"].append({
            "name": app_state['current_name'],
            "home_terrain": app_state['current_home_terrain'],
            "frontier_terrain": "Not Implemented" # Placeholder
        })

        # Check if there are more players to set up
        if app_state["current_setup_index"] < app_state["num_players"] - 1:
            app_state["current_setup_index"] += 1
            app_state["current_name"] = f"Player {app_state['current_setup_index'] + 1}"
            app_state["current_home_terrain"] = None
            update_ui()
        else:
            # All players are set up, start the game
            print("All players set up. Starting game engine...")
            app_state["game_engine"] = GameEngine(app_state["point_value"], app_state["all_player_setups"])
            app_state["screen"] = "gameplay"
            ui_manager.elements = [] # Clear the setup UI

    # --- Initial UI Creation ---
    update_ui()
    
    running = True
    while running:
        # --- Event Handling ---
        new_text = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Pass event to UI manager and check if it returned updated text
            updated_text = ui_manager.handle_event(event)
            if updated_text is not None: new_text = updated_text
        
        if new_text is not None and app_state['screen'] == 'player_setup':
            app_state['current_name'] = new_text

        # Rebuild UI if state changed (simplistic for now)
        # This is needed to update button active states
        if app_state['screen'] in ['welcome', 'player_setup']:
            update_ui()

        # --- Drawing ---
        screen.fill("#404040")

        if app_state["screen"] == "welcome":
            title_surf = font_large.render("Welcome to Dragon Dice!", True, "white")
            screen.blit(title_surf, (screen.get_width() / 2 - title_surf.get_width() / 2, 150))
            #... draw other labels
        
        elif app_state["screen"] == "player_setup":
            title_text = f"Player {app_state['current_setup_index'] + 1} Setup"
            title_surf = font_large.render(title_text, True, "white")
            screen.blit(title_surf, (screen.get_width() / 2 - title_surf.get_width() / 2, 80))
            # ... draw other labels

        elif app_state["screen"] == "gameplay":
            app_state["game_engine"].draw(screen)

        ui_manager.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()