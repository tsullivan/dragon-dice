# help_texts.py

def welcome_text():
    return (
        "Welcome to the Dragon Dice Digital Companion!\n\n"
        "Select the number of players participating and the agreed-upon total point value for each player's force. "
        "Click 'Proceed to Setup' to continue."
    )

def player_setup_text(player_number, total_players, game_point_limit):
    horde_info = "Horde, " if total_players > 1 else ""
    return (
        f"Player {player_number} Setup:\n\n"
        "Enter your player name.\n"
        f"Name your Home, {horde_info}and Campaign armies.\n"
        f"Enter the point value for each of these armies. The total points for your armies should not exceed {game_point_limit}. "
        f"No single army can be more than {game_point_limit // 2} points (half of your total force points, rounded down).\n"
        "Use the '< Prev' and 'Next >' buttons to select your Home Terrain (from standard terrains) and propose a Frontier Terrain (from standard or advanced terrains).\n"
        "Click 'Next Player' or 'Start Game' when done. Use Shift + Mouse Wheel to scroll horizontally if needed."
    )

def gameplay_setup_frontier_text():
    return (
        "Determine Frontier & First Player:\n\n"
        "Players should now make a maneuver roll with their physical Horde Armies (as per rulebook Step 4: Determine Order of Play).\n"
        "The player who rolled the most maneuver results chooses to either take the first turn OR select which proposed Frontier Terrain will be used.\n"
        "Input these two selections using the buttons above. Click 'Confirm Selections' to proceed."
    )

def gameplay_setup_distance_text():
    return (
        "Enter Starting Distances (Rulebook Step 5):\n\n"
        "Each player rolls their Home Terrain die to determine its initial battle distance. The player who selected the Frontier Terrain rolls that die.\n"
        "If a terrain die rolls an 8, roll again. If it rolls a 7, turn it down to 6.\n"
        "Enter the resulting number (1-6) for each terrain listed above. Click 'Submit Rolls & Start' to begin the game."
    )

def gameplay_maneuver_decision_text(player_name, current_turn_phase_display):
    return (
        f"Maneuver Decision for {player_name}:\n\n"
        f"It is your turn, during the {current_turn_phase_display} phase.\n"
        "Do you wish to attempt a maneuver with your army at the current terrain? "
        "If yes, you will select an army and potentially face a counter-maneuver. "
        "If no, you will proceed to the Action step of this march (if applicable) or the next phase."
    )

def gameplay_maneuver_input_text(player_name, current_turn_phase_display):
    return (
        f"Maneuver Action for {player_name} ({current_turn_phase_display}):\n\n"
        "Select the army you wish to maneuver and the target terrain (if multiple options exist).\n"
        "If an opponent has an army at the same terrain, they may oppose. Both players make a maneuver roll with their physical dice.\n"
        "Enter the results into the application when prompted. (Input UI for this step is pending)."
    )

def gameplay_roll_for_march_text(player_name, current_turn_phase_display, action_type):
    return (
        f"Roll for {action_type} Action ({player_name} - {current_turn_phase_display}):\n\n"
        f"You should now roll your physical dice for the {action_type} action as indicated by the terrain or army location (Reserves).\n"
        "Resolve any Special Action Icons (SAIs) first. Then, input the total results. (Input UI for this step is pending)."
    )

def gameplay_reserves_text(player_name):
    return (
        f"Reserves Phase for {player_name}:\n\n"
        "1. Reinforce Step: You may move any or all units from your Reserve Area to any terrains.\n"
        "2. Retreat Step: After reinforcing, you may move any or all of your units from any terrains to your Reserve Area.\n"
        "(Detailed UI for these actions is pending)."
    )

def gameplay_general_text():
    return (
        "General Gameplay:\n\n"
        "Follow the turn sequence: Expire Effects, Eighth Face, Dragon Attack, Species Abilities, First March, Second March, Reserves.\n"
        "The application will guide you through each phase and step, prompting for actions and results.\n"
        "Remember, all dice rolling and physical army management happens outside this app."
    )

# You might still want a helper function here or in main.py to format phase names
# if you need it for multiple help text functions.
# For example:
# def _format_phase_name(phase_str):
#     return phase_str.replace('_', ' ').title()