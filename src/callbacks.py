def handle_selection(app_state, state_key, value):
    """Generic handler to update state and flag UI for a rebuild."""
    if app_state[state_key] != value:
        app_state[state_key] = value
        app_state["ui_needs_update"] = True

def proceed_to_setup(app_state):
    """Transitions from the welcome screen to player setup."""
    if not app_state["num_players"] or not app_state["point_value"]:
        return
    app_state["screen"] = "player_setup"
    app_state["current_name"] = f"Player {app_state['current_setup_index'] + 1}"
    app_state["ui_needs_update"] = True

def handle_cycle_terrain(app_state, state_key_terrain_name: str, direction: int):
    """Cycles through terrain options for Home or Frontier."""
    standard_terrains = ['Coastland', 'Deadland', 'Flatland', 'Highland', 'Swampland', 'Feyland', 'Wasteland']
    advanced_terrains = ['Castle', "Dragon's Lair", 'Grove', 'Vortex']
    
    options_list = []
    if state_key_terrain_name == "current_home_terrain":
        options_list = standard_terrains
    elif state_key_terrain_name == "current_frontier_terrain":
        options_list = standard_terrains + advanced_terrains
    else:
        return # Should not happen

    current_selection = app_state[state_key_terrain_name]
    current_index = -1
    if current_selection in options_list:
        current_index = options_list.index(current_selection)
    
    new_index = (current_index + direction + len(options_list)) % len(options_list)
    app_state[state_key_terrain_name] = options_list[new_index]
    app_state["ui_needs_update"] = True

def handle_next_player(app_state, GameEngine):
    """Saves the current player's setup and moves to the next, or starts the game."""
    required_app_state_keys = [
        'current_name', 'current_home_terrain', 'current_frontier_terrain',
        'current_home_army_name', 'current_campaign_army_name',
        'current_home_army_points', 'current_campaign_army_points'
    ]
    num_players = app_state.get("num_players", 1)
    if num_players > 1:
        required_app_state_keys.extend(['current_horde_army_name', 'current_horde_army_points'])

    if not all(app_state.get(key) for key in required_app_state_keys):
        print("Error: Not all required fields are filled for player setup.")
        return
    
    # Point validation before proceeding
    try:
        game_limit = int(app_state.get("point_value", 0))
        max_per_army = game_limit // 2

        home_pts = int(app_state["current_home_army_points"])
        campaign_pts = int(app_state["current_campaign_army_points"])
        horde_pts = 0
        if num_players > 1:
            horde_pts = int(app_state["current_horde_army_points"])

        current_total_allocated = home_pts + campaign_pts + horde_pts

        if current_total_allocated != game_limit:
            print(f"Error: Total allocated points ({current_total_allocated}) do not match game limit ({game_limit}).")
            return
        
        for pts_val in [home_pts, campaign_pts] + ([horde_pts] if num_players > 1 else []):
            if pts_val <= 0 or pts_val > max_per_army:
                print(f"Error: Army points ({pts_val}) are invalid (must be > 0 and <= {max_per_army}).")
                return
    except ValueError:
        print("Error: Army point values must be numbers.")
        return

    app_state["all_player_setups"].append({
        "name": app_state['current_name'],
        "home_terrain": app_state['current_home_terrain'],
        "frontier_terrain": app_state['current_frontier_terrain'],
        "home_army_name": app_state['current_home_army_name'],
        "horde_army_name": app_state['current_horde_army_name'],
        "campaign_army_name": app_state['current_campaign_army_name'],
        "home_army_points": app_state['current_home_army_points'],
        "horde_army_points": app_state['current_horde_army_points'],
        "campaign_army_points": app_state['current_campaign_army_points'],
    })

    if app_state["current_setup_index"] < app_state["num_players"] - 1:
        app_state["current_setup_index"] += 1
        app_state["current_name"] = f"Player {app_state['current_setup_index'] + 1}"
        app_state["current_home_terrain"] = None
        app_state["current_home_army_name"] = ""
        app_state["current_horde_army_name"] = ""
        app_state["current_campaign_army_name"] = ""
        app_state["current_home_army_points"] = ""
        app_state["current_horde_army_points"] = ""
        app_state["current_campaign_army_points"] = ""
        app_state["current_frontier_terrain"] = None
    else:
        app_state["game_engine"] = GameEngine(app_state["point_value"], app_state["all_player_setups"])
        app_state["screen"] = "gameplay"
    
    app_state["ui_needs_update"] = True

def handle_frontier_submission(app_state):
    """Submits the chosen frontier and first player to the game engine."""
    selections = app_state
    if selections["current_frontier_selection"] and selections["current_first_player_selection"]:
        if selections["game_engine"]: # Ensure game_engine exists
            selections["game_engine"].submit_frontier_selection(
                selections["current_frontier_selection"],
                selections["current_first_player_selection"]
            )
            app_state["ui_needs_update"] = True

def handle_rolls_submission(app_state, input_boxes):
    """Submits the terrain distance rolls to the game engine."""
    rolls = [
        {"terrain_id": item["terrain_id"], "value": item["input_box"].text}
        for item in input_boxes
    ]
    if app_state["game_engine"]: # Ensure game_engine exists
        app_state["game_engine"].submit_distance_rolls(rolls)
        app_state["ui_needs_update"] = True

def handle_maneuver_decision(app_state, will_maneuver: bool):
    """Handles the player's maneuver decision by calling the engine."""
    engine = app_state.get("game_engine")
    if engine:
        engine.process_maneuver_decision(will_maneuver)
        app_state["ui_needs_update"] = True