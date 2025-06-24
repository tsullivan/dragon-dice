class HelpTextModel:
    """
    Provides structured help text for different parts of the application.
    """

    def get_welcome_help(self) -> str:
        return """
<b>Welcome to the Dragon Dice Companion!</b>
<p>Dragon Dice is a game of fantasy battles where players assemble armies of dice representing different fantasy races and creatures.
Each die has unique icons for movement, melee, missiles, magic, and special abilities.
Players maneuver their armies across terrain dice, engage in combat, and attempt to capture two terrains to win the game.
This application will help you track game state, turns, and phases, but all dice rolling and physical army management is done by you with your Dragon Dice!</p>
<p>This screen helps you start a new game.</p>
<p><b>UI Elements:</b></p>
<ul>
    <li><b>Select Number of Players:</b> Choose how many people are playing (currently 2-4).</li>
    <li><b>Proceed to Player Setup:</b> Click this button to continue to the next step after making your selections.</li>
</ul>
<p><b>Current Phase: Initial Game Setup</b></p>
<p>You are at the very beginning of setting up your Dragon Dice game. The choices made here will determine the number of players and the scale of the armies involved.</p>
"""

    def get_player_setup_help(
        self, player_num: int, num_players: int, force_size: int = 24
    ) -> str:
        horde_army_help = ""
        if num_players > 1:
            horde_army_help = "<li><b>Horde Army:</b> This army will start at an opponent's Home Terrain. It must have at least one unit.</li>"

        max_points_per_army = force_size // 2

        return f"""
<b>Player {player_num} Setup</b>
<p>In this phase, Player {player_num} will secretly assemble their forces using {force_size} points total.</p>
<p><b>Army Assembly Rules:</b></p>
<ul>
    <li><b>Total Force Size:</b> All armies combined must use exactly {force_size} points</li>
    <li><b>Army Size Limit:</b> No single army can exceed {max_points_per_army} points (50% of total force)</li>
    <li><b>Minimum Units:</b> Each army must contain at least one unit</li>
    <li><b>Unit Cost:</b> Each unit's point cost equals its health value</li>
</ul>
<p><b>UI Elements:</b></p>
<ul>
    <li><b>Player Name:</b> Enter your name.</li>
    <li><b>Home Terrain:</b> Select the type of terrain where your main army (Home Army) will start.</li>
    <li><b>Home Army:</b> This army starts at your Home Terrain. Maximum {max_points_per_army} points.</li>
    <li><b>Campaign Army:</b> This army will start at the Frontier Terrain. Maximum {max_points_per_army} points.</li>
    {horde_army_help}
    <li><b>Propose Frontier Terrain:</b> Each player suggests a terrain type. One of these will be chosen as the central Frontier Terrain for the game.</li>
    <li><b>Next Player/Start Game Button:</b> Click to finalize this player's setup and move to the next player, or to proceed if all players are set up.</li>
</ul>
<p>Click "Manage Units" for each army to select units. The status bar will show validation errors if army requirements are not met.</p>
"""

    def get_frontier_selection_help(self) -> str:
        return """
<b>Determine Frontier & First Player</b>
<p>This screen finalizes the battlefield setup and who goes first.</p>
<p><b>UI Elements:</b></p>
<ul>
    <li><b>Select First Player:</b> Choose which player will take the first turn.
        (<i>Rulebook Note: Typically, all players roll their Horde Armies. The highest roller chooses to either take the first turn OR select the Frontier Terrain. If they choose to play first, the player with the next highest total selects the Frontier Terrain. This UI simplifies this decision.</i>)</li>
    <li><b>Select Frontier Terrain:</b> From the terrains proposed by players during setup, select one to be the Frontier Terrain for this game. All other proposed terrains are removed.</li>
    <li><b>Submit Selections:</b> Click to confirm your choices and proceed.</li>
</ul>
<p><b>Current Phase: Setting the Battlefield & Order of Play (Rulebook pg. 9-10)</b></p>
<p>You are determining the central Frontier Terrain and the player order. The Frontier Terrain is adjacent to every Home Terrain. After this, players will place their armies and determine starting distances.</p>
"""

    def get_distance_rolls_help(self, frontier_terrain: str) -> str:
        return f"""
<b>Enter Starting Distances</b>
<p>This step determines the initial battle distances at each terrain.</p>
<p><b>UI Elements:</b></p>
<ul>
    <li><b>Rolling distance to: {frontier_terrain}</b>: Indicates the central Frontier Terrain.</li>
    <li>For each player listed (e.g., "Player 1 (Home: Plains)"): Enter the result of their Home Terrain die roll.</li>
    <li>The player who selected the Frontier Terrain also rolls that die; enter its result in the corresponding player's input field (or a dedicated field if added).</li>
    <li><b>Submit All Rolls:</b> Click once all required distance rolls are entered.</li>
</ul>
<p><b>Current Phase: Determine Starting Distance (Rulebook pg. 10)</b></p>
<p>Each player rolls their Home Terrain die. The player that selected the Frontier Terrain rolls that die.
If an 8 is rolled, roll again. If a 7 is rolled, turn the die down to 6. All terrains will therefore start the game showing a number between 1 and 6. Input these final 1-6 values.</p>
"""

    def get_main_gameplay_help(self, current_step: str) -> str:
        ui_explanation = """
<b>UI Elements:</b>
<ul>
    <li><b>Current Player:</b> Shows whose turn it is.</li>
    <li><b>Phase:</b> Displays the current game phase and step.</li>
    <li><i>Action buttons and input fields will appear based on the current step.</i></li>
</ul>
"""
        phase_explanation_map = {
            "FIRST_MARCH": """
<p><b>🎮 Game Start: First March Phase</b></p>
<p><strong>Welcome to Dragon Dice gameplay!</strong> The game begins with your First March phase.</p>
<p><b>Army Selection:</b> Choose one of your three armies for this march:</p>
<ul>
    <li><b>Home Army:</b> Located at your Home Terrain</li>
    <li><b>Campaign Army:</b> Located at the Frontier Terrain</li>
    <li><b>Horde Army:</b> Located at an opponent's Home Terrain</li>
</ul>
<p><b>What happens next:</b> Your selected army may maneuver (change terrain distance) and/or take an action (Melee, Missile, or Magic) based on the terrain's current face.</p>
<p><b>Strategy tip:</b> Consider which army is best positioned to advance your objectives or capture terrain.</p>
""",
            "DECIDE_MANEUVER": """
<p><b>Current Step: Decide Maneuver (within First/Second March)</b></p>
<p>Choose one of your armies for this march phase. The selected army will attempt to maneuver and/or take an action.</p>
<p><b>Army Selection:</b> You should choose which army (Home, Campaign, or Horde) will be active for this march. Consider which army is best positioned for your strategy.</p>
<p><b>Maneuver Decision:</b> Decide if your selected army will attempt to maneuver. Maneuvering changes the distance on the terrain die where the army is located. If an opponent is at the same terrain, they may oppose the maneuver. (Rulebook pg. 11)</p>
<p><b>Actions:</b> Click 'Maneuver: Yes' to attempt a maneuver, or 'Maneuver: No' to skip the maneuver step and proceed to selecting an action.</p>
""",
            "AWAITING_MANEUVER_INPUT": """
<p><b>Current Step: Awaiting Maneuver Input (within First/Second March)</b></p>
<p>The player chose to maneuver. If unopposed, the maneuver is automatic. If opposed, both players roll their armies and count maneuver results. Input the outcome or relevant dice results into the 'Enter Maneuver Details' field. The companion app does not roll dice for you. (Rulebook pg. 11)</p>
<p><b>Actions:</b> Enter the details/results of the maneuver roll and click 'Submit Maneuver'.</p>
""",
            "SELECT_ACTION": """
<p><b>Current Step: Select Action (within First/Second March)</b></p>
<p>The army may now take an action: Melee, Missile, or Magic. The available action is usually determined by the icon on the terrain die. If the terrain is on its 8th face, the controlling army has more options. An army in the Reserve Area may only take a Magic action. (Rulebook pg. 12)</p>
<p><b>Actions:</b> Click the button corresponding to the action you wish to take.</p>
""",
            "AWAITING_ATTACKER_MELEE_ROLL": """
<p><b>Current Step: Attacker Melee Roll (within Melee Action)</b></p>
<p>The attacking army makes a melee roll. Count melee results and resolve any applicable SAIs first. Input the total melee results. (Rulebook pg. 12)</p>
<p><b>Actions:</b> Enter the attacker's melee results and click 'Submit Attacker Melee'.</p>
""",
            "AWAITING_DEFENDER_SAVES": """
<p><b>Current Step: Defender Save Roll (within Melee Action)</b></p>
<p>The defending army makes a save roll. Resolve SAIs, then subtract save results from the attacker's melee results to determine damage. (Rulebook pg. 12)</p>
<p><b>Actions:</b> Enter the defender's save results and click 'Submit Defender Saves'.</p>
""",
        }
        # Add explanations for other phases
        phase_explanation_map.update(
            {
                "EXPIRE_EFFECTS": """
<p><b>Current Phase: Expire Effects</b></p>
<p>Certain ongoing effects from spells or abilities may expire at the start of the turn. Check any active effects and resolve their expiration according to the rules. (Rulebook pg. 11)</p>
<p><b>Actions:</b> After resolving, click 'Continue' (or similar button when implemented) to proceed to the next phase.</p>
""",
                "EIGHTH_FACE": """
<p><b>Current Phase: Eighth Face</b></p>
<p>If any terrain dice are showing their 8th face, the player controlling that terrain may use its special ability. (Rulebook pg. 11, pg. 6 for terrain effects)</p>
<p><b>Actions:</b> Resolve any 8th face abilities. Click 'Continue' to proceed.</p>
""",
                "DRAGON_ATTACK": """
<p><b>Current Phase: Dragon Attack</b></p>
<p>The current player may have their dragons attack. Dragons can attack other dragons or armies at the same terrain. (Rulebook pg. 11, pg. 17-18 for dragon combat)</p>
<p><b>Actions:</b> Follow prompts for dragon attacks (selecting dragons, targets, rolling dice, resolving damage). Click 'Continue' when all dragon attacks are resolved.</p>
""",
                "SPECIES_ABILITIES": """
<p><b>Current Phase: Species Abilities</b></p>
<p>The current player may use certain special abilities of their units, often indicated by SAIs (Special Action Icons) or described in the species rules. (Rulebook pg. 11, pg. 21+ for species)</p>
<p><b>Actions:</b> Announce and resolve any species abilities. Click 'Continue' to proceed.</p>
""",
                "RESERVES": """
<p><b>Current Phase: Reserves</b></p>
<p>The current player may bring units from their Summoning Pool into their Reserve Area, or promote units already in Reserves. (Rulebook pg. 11, pg. 16 for reserves)</p>
<p><b>Actions:</b> Manage your reserves. Click 'Continue' to end your turn.</p>
""",
            }
        )

        phase_explanation = phase_explanation_map.get(
            current_step,
            f"<p><b>Current Step: {current_step.replace('_', ' ').title()}</b></p><p>Follow the on-screen prompts and refer to the rulebook for detailed rules for this step.</p>",
        )
        return f"<html><body>{ui_explanation}{phase_explanation}</body></html>"
