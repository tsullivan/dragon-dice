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
        # Get terrain icon for the frontier terrain
        terrain_icon = "🗺️"  # Default
        import constants

        for terrain_name, icon in constants.TERRAIN_ICONS.items():
            if terrain_name in frontier_terrain:
                terrain_icon = icon
                break

        return f"""
<b>🎲 Enter Starting Distances</b>
<p>This step determines the initial battle distances at each terrain.</p>
<p><b>🎯 UI Elements:</b></p>
<ul>
    <li><b>🗺️ Rolling distance to: {terrain_icon} {frontier_terrain}</b>: The central Frontier Terrain for this game.</li>
    <li><b>🏰 Home Terrain Rolls:</b> Each player selects their Home Terrain die roll result (1-6).</li>
    <li><b>🚩 Frontier Terrain Roll:</b> The first player (who was selected to go first) also rolls the frontier terrain die and selects the result (1-6).</li>
    <li><b>📤 Submit All Rolls:</b> Click once all required distance rolls are entered using the radio buttons.</li>
</ul>
<p><b>📖 Current Phase: Determine Starting Distance (Rulebook pg. 10)</b></p>
<p>🎲 Each player rolls their Home Terrain die. The first player also rolls the Frontier Terrain die.
⚠️ If an 8 is rolled, roll again. If a 7 is rolled, turn the die down to 6. All terrains will therefore start the game showing a number between 1 and 6. Select these final 1-6 values using the radio buttons.</p>
"""

    def get_main_gameplay_help(self, current_step: str) -> str:
        ui_explanation = """
<b>🎯 UI Elements:</b>
<ul>
    <li><b>👤 Current Player:</b> Shows whose turn it is.</li>
    <li><b>⚡ Phase:</b> Displays the current game phase and step.</li>
    <li><i>🎮 Action buttons and input fields will appear based on the current step.</i></li>
</ul>
"""
        phase_explanation_map = {
            "FIRST_MARCH": """
<p><b>🎮 Game Start: First March Phase</b></p>
<p><strong>Welcome to Dragon Dice gameplay!</strong> The game begins with your First March phase.</p>
<p><b>⚔️ Army Selection:</b> Choose one of your three armies for this march:</p>
<ul>
    <li><b>🏰 Home Army:</b> Located at your Home Terrain</li>
    <li><b>🚩 Campaign Army:</b> Located at the Frontier Terrain</li>
    <li><b>🌊 Horde Army:</b> Located at an opponent's Home Terrain</li>
</ul>
<p><b>🎯 What happens next:</b> Your selected army may maneuver (change terrain distance) and/or take an action (⚔️ Melee, 🏹 Missile, or ✨ Magic) based on the terrain's current face.</p>
<p><b>💡 Strategy tip:</b> Consider which army is best positioned to advance your objectives or capture terrain.</p>
""",
            "CHOOSE_ACTING_ARMY": """
<p><b>⚔️ Choose Acting Army</b></p>
<p>Select which army will be active for both the Maneuver and Action steps of this March phase.</p>
<p><b>🏰 Your Armies:</b></p>
<ul>
    <li><b>🏰 Home Army:</b> Located at your Home Terrain - strong defensive position</li>
    <li><b>🚩 Campaign Army:</b> Located at the Frontier Terrain - central position for offense</li>
    <li><b>🌊 Horde Army:</b> Located at opponent's Home Terrain - deep strike position</li>
</ul>
<p><b>📍 Location Info:</b> Each army shows its current terrain, terrain type, and die face. The terrain die face determines what actions are available:</p>
<ul>
    <li><b>Face 1+:</b> ⚔️ Melee actions available</li>
    <li><b>Face 2+:</b> 🏹 Missile actions available</li>
    <li><b>Face 3+:</b> ✨ Magic actions available</li>
</ul>
<p><b>💡 Strategy:</b> Choose the army best positioned for your tactical goals. Your choice persists through both Maneuver and Action steps.</p>
""",
            "DECIDE_MANEUVER": """
<p><b>🚀 Decide Maneuver</b></p>
<p>Your acting army is ready! Now decide if it will attempt to maneuver.</p>
<p><b>🎯 Maneuver Decision:</b> Maneuvering allows your army to change the distance (die face) on the terrain where it's located. This can:</p>
<ul>
    <li><b>📈 Turn Up:</b> Increase the terrain die face (more action options)</li>
    <li><b>📉 Turn Down:</b> Decrease the terrain die face (fewer action options for opponents)</li>
</ul>
<p><b>⚠️ Opposition:</b> If an opponent army is at the same terrain, they may choose to counter-maneuver, leading to opposed rolls. (Rulebook pg. 11)</p>
<p><b>🎮 Actions:</b></p>
<ul>
    <li><b>✅ Maneuver: Yes</b> - Open the maneuver dialog to attempt maneuvering</li>
    <li><b>❌ Maneuver: No</b> - Skip maneuvering and proceed to action selection</li>
</ul>
""",
            "AWAITING_MANEUVER_INPUT": """
<p><b>🎲 Awaiting Maneuver Input</b></p>
<p>You chose to maneuver! The maneuver dialog will guide you through the complete process.</p>
<p><b>🔄 Maneuver Process:</b></p>
<ul>
    <li><b>🛡️ Counter-Maneuver:</b> Opponents at the same terrain may choose to oppose</li>
    <li><b>🎲 Resolution:</b> Roll armies and count 🏃 maneuver results</li>
    <li><b>📈📉 Outcome:</b> Winner chooses to turn terrain up or down by 1</li>
</ul>
<p><b>⚠️ Note:</b> This app provides the interface but doesn't roll dice for you. Use your physical Dragon Dice! (Rulebook pg. 11)</p>
""",
            "DECIDE_ACTION": """
<p><b>⚡ Decide Action</b></p>
<p>Your acting army has completed any maneuvering. Now decide if it will take an action.</p>
<p><b>🎯 Available Actions:</b> The actions available depend on the terrain die face where your army is located:</p>
<ul>
    <li><b>Face 1+:</b> ⚔️ Melee (Close combat attack)</li>
    <li><b>Face 2+:</b> 🏹 Missile (Ranged attack)</li>
    <li><b>Face 3+:</b> ✨ Magic (Spell casting)</li>
</ul>
<p><b>🎮 Decision:</b></p>
<ul>
    <li><b>✅ Take Action: Yes</b> - Proceed to select specific action type</li>
    <li><b>❌ Take Action: No</b> - End your march and advance to next phase</li>
</ul>
<p><b>💡 Strategy:</b> Consider whether an action will advance your position or if it's better to conserve your army for later phases.</p>
""",
            "SELECT_ACTION": """
<p><b>🎯 Select Action</b></p>
<p>Choose the specific action your acting army will take. Only actions available based on the terrain die face are shown.</p>
<p><b>⚔️ Action Types:</b></p>
<ul>
    <li><b>⚔️ Melee Action:</b> Close combat attack against armies at the same terrain</li>
    <li><b>🏹 Missile Action:</b> Ranged attack that can target multiple terrains</li>
    <li><b>✨ Magic Action:</b> Spell casting with various effects and targets</li>
</ul>
<p><b>🗺️ Terrain Limitations:</b> Your terrain die face determines available actions:</p>
<ul>
    <li><b>Face 1:</b> Only ⚔️ Melee available</li>
    <li><b>Face 2:</b> ⚔️ Melee and 🏹 Missile available</li>
    <li><b>Face 3+:</b> All actions (⚔️ Melee, 🏹 Missile, ✨ Magic) available</li>
</ul>
<p><b>🎮 Actions:</b> Click the button for your chosen action type. (Rulebook pg. 12)</p>
""",
            "AWAITING_ATTACKER_MELEE_ROLL": """
<p><b>⚔️ Attacker Melee Roll</b></p>
<p>The attacking army makes a melee roll with their dice. Time to count your results!</p>
<p><b>🎲 Roll Process:</b></p>
<ul>
    <li><b>1️⃣ Roll:</b> Roll all dice in your attacking army</li>
    <li><b>2️⃣ Count ⚔️:</b> Count all melee icons that come up</li>
    <li><b>3️⃣ Resolve 💎 SAIs:</b> Apply any Special Action Icons first</li>
    <li><b>4️⃣ Total:</b> Calculate final melee results after all modifiers</li>
</ul>
<p><b>📋 Actions:</b> Enter your total melee results and click '📤 Submit Attacker Melee'. (Rulebook pg. 12)</p>
""",
            "AWAITING_DEFENDER_SAVES": """
<p><b>🛡️ Defender Save Roll</b></p>
<p>The defending army makes a save roll to reduce incoming damage.</p>
<p><b>🎲 Save Process:</b></p>
<ul>
    <li><b>1️⃣ Roll:</b> Roll all dice in your defending army</li>
    <li><b>2️⃣ Count 🛡️:</b> Count all save icons that come up</li>
    <li><b>3️⃣ Resolve 💎 SAIs:</b> Apply any Special Action Icons that affect saves</li>
    <li><b>4️⃣ Subtract:</b> Saves reduce the attacker's melee results</li>
</ul>
<p><b>📋 Actions:</b> Enter your total save results and click '📤 Submit Defender Saves'. (Rulebook pg. 12)</p>
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
