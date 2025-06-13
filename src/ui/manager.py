import pygame
from typing import Optional
from .button import Button
from .text_input_box import TextInputBox
from .display_box import DisplayBox
from .label import Label

class UIManager:
    def __init__(self):
        self.panel_elements = [] # Elements for a scrollable panel
        self.fixed_elements = [] # Elements fixed on the screen

    def create_welcome_ui(self, selections, callbacks):
        self.panel_elements = [] # No panel elements for welcome screen
        self.fixed_elements = []
        # Player Count Buttons
        for i, count in enumerate([1, 2, 3, 4]):
            btn = Button(445 + i * 90, 300, 60, 40, str(count), lambda c=count: callbacks['on_player_select'](c))
            if selections['num_players'] == count: btn.is_active = True
            self.fixed_elements.append(btn)

        # Point Value Buttons
        for i, val in enumerate([15, 24, 30, 36, 60]):
            btn = Button(355 + i * 90, 400, 60, 40, str(val), lambda v=val: callbacks['on_point_select'](v))
            if selections['point_value'] == val: btn.is_active = True
            self.fixed_elements.append(btn)

        # Proceed Button
        proceed_btn = Button(560, 500, 160, 50, "Proceed to Setup", callbacks['on_proceed'])
        # Enable button only if both selections have been made
        if selections['num_players'] and selections['point_value']:
            proceed_btn.is_active = True
        self.fixed_elements.append(proceed_btn)

    def create_player_setup_ui(self, player_index, selections, callbacks):
        self.panel_elements = [] # Elements for the scrollable panel
        self.fixed_elements = [] # For the Next/Start button
        current_x = 30  # Initial X padding inside the panel
        section_padding = 60 # Padding between horizontal sections
        section_title_font_size = 26 # Font size for "PLAYER & ARMY NAMES" etc.
        label_font_size = 22 # Font size for "Player Name:"
        name_input_width = 220 # Width for name inputs
        points_input_width = 80 # Width for points inputs
        points_label_width = 70
        input_height = 35
        # Carousel specific dimensions
        carousel_display_width = 150 # Width of the terrain display box, made smaller for arrows
        carousel_arrow_button_width = 35 # Width of the arrow icon buttons
        carousel_arrow_button_height = 30 # Height of arrow buttons for carousel
        v_spacing = 8 # Vertical spacing between elements in a section
        section_title_y_offset = 20 # Y position for section titles
        label_to_input_spacing = 5 # Space between a label like "Player Name:" and its input box
        inter_element_spacing = 15 # Space between (label+input) groups

        # --- Section 1: Player and Army Names ---
        sec1_y = section_title_y_offset
        self.panel_elements.append(Label(current_x, sec1_y, "PLAYER & ARMY NAMES", font_size=section_title_font_size))
        sec1_y += section_title_font_size + inter_element_spacing # Space after title

        self.panel_elements.append(Label(current_x, sec1_y, "Player Name:", font_size=label_font_size))
        sec1_y += label_font_size + label_to_input_spacing
        name_box = TextInputBox(current_x, sec1_y, name_input_width, input_height, selections['name'])
        name_box.id = "player_name"
        self.panel_elements.append(name_box)
        sec1_y += input_height + inter_element_spacing

        # Army Names and Points (Name on left, Points on right)
        army_details_x_start = current_x
        points_x_start = army_details_x_start + name_input_width + v_spacing * 2

        self.panel_elements.append(Label(current_x, sec1_y, "Home Army Name:", font_size=label_font_size))
        self.panel_elements.append(Label(points_x_start, sec1_y, "Points:", font_size=label_font_size))
        sec1_y += label_font_size + label_to_input_spacing
        home_army_name_box = TextInputBox(army_details_x_start, sec1_y, name_input_width, input_height, selections.get('home_army_name', ''))
        home_army_name_box.id = "home_army_name"
        self.panel_elements.append(home_army_name_box)
        home_army_points_box = TextInputBox(points_x_start, sec1_y, points_input_width, input_height, selections.get('home_army_points', ''))
        home_army_points_box.id = "home_army_points"
        self.panel_elements.append(home_army_points_box)
        sec1_y += input_height + inter_element_spacing

        if selections.get('total_players', 1) > 1: # Only show Horde army name for multiplayer
            self.panel_elements.append(Label(current_x, sec1_y, "Horde Army Name:", font_size=label_font_size))
            self.panel_elements.append(Label(points_x_start, sec1_y, "Points:", font_size=label_font_size))
            sec1_y += label_font_size + label_to_input_spacing
            horde_army_name_box = TextInputBox(army_details_x_start, sec1_y, name_input_width, input_height, selections.get('horde_army_name', ''))
            horde_army_name_box.id = "horde_army_name"
            self.panel_elements.append(horde_army_name_box)
            horde_army_points_box = TextInputBox(points_x_start, sec1_y, points_input_width, input_height, selections.get('horde_army_points', ''))
            horde_army_points_box.id = "horde_army_points"
            self.panel_elements.append(horde_army_points_box)
            sec1_y += input_height + inter_element_spacing
        
        self.panel_elements.append(Label(current_x, sec1_y, "Campaign Army Name:", font_size=label_font_size))
        self.panel_elements.append(Label(points_x_start, sec1_y, "Points:", font_size=label_font_size))
        sec1_y += label_font_size + label_to_input_spacing
        campaign_army_name_box = TextInputBox(army_details_x_start, sec1_y, name_input_width, input_height, selections.get('campaign_army_name', ''))
        campaign_army_name_box.id = "campaign_army_name"
        self.panel_elements.append(campaign_army_name_box)
        campaign_army_points_box = TextInputBox(points_x_start, sec1_y, points_input_width, input_height, selections.get('campaign_army_points', ''))
        campaign_army_points_box.id = "campaign_army_points"
        self.panel_elements.append(campaign_army_points_box)

        # Point Validation Display
        sec1_y += input_height + inter_element_spacing # Space after last input
        total_allocated_str = selections.get('current_total_allocated_points_str', "0")
        game_limit_str = str(selections.get('game_point_limit', 'N/A'))
        max_per_army_str = str(selections.get('max_points_per_army', 'N/A'))

        self.panel_elements.append(
            Label(army_details_x_start, sec1_y, f"Total Allocated: {total_allocated_str} / {game_limit_str}", font_size=label_font_size - 2)
        )
        sec1_y += (label_font_size - 2) + v_spacing
        self.panel_elements.append(
            Label(army_details_x_start, sec1_y, f"Max per Army: {max_per_army_str}", font_size=label_font_size - 2)
        )

        section1_width = points_x_start + points_input_width # Max width of this section
        current_x += section1_width + section_padding

        # --- Section 2: Home Terrain Selection ---
        sec2_y = section_title_y_offset
        self.panel_elements.append(Label(current_x, sec2_y, "HOME TERRAIN", font_size=section_title_font_size))
        sec2_y += section_title_font_size + inter_element_spacing 
        
        standard_terrains = ['Coastland', 'Deadland', 'Flatland', 'Highland', 'Swampland', 'Feyland', 'Wasteland']

        home_prev_btn = Button(current_x, sec2_y + (input_height - carousel_arrow_button_height) // 2, carousel_arrow_button_width, carousel_arrow_button_height, "", callbacks['on_prev_home_terrain'], icon="left_arrow")
        self.panel_elements.append(home_prev_btn)
        
        home_display_text = selections['home_terrain'] if selections['home_terrain'] else "Select"
        home_display_box_x = current_x + carousel_arrow_button_width + v_spacing
        home_display_box = DisplayBox(home_display_box_x, sec2_y, carousel_display_width, input_height, home_display_text, font_size=20)
        self.panel_elements.append(home_display_box)

        home_next_btn_x = home_display_box_x + carousel_display_width + v_spacing
        home_next_btn = Button(home_next_btn_x, sec2_y + (input_height - carousel_arrow_button_height) // 2, carousel_arrow_button_width, carousel_arrow_button_height, "", callbacks['on_next_home_terrain'], icon="right_arrow")
        self.panel_elements.append(home_next_btn)
        
        section2_width = carousel_arrow_button_width * 2 + carousel_display_width + v_spacing * 2 # Total width of the carousel
        current_x += section2_width + section_padding

        # --- Section 3: Frontier Terrain Proposal ---
        sec3_y = section_title_y_offset
        self.panel_elements.append(Label(current_x, sec3_y, "FRONTIER PROPOSAL", font_size=section_title_font_size))
        sec3_y += section_title_font_size + inter_element_spacing

        advanced_terrains = ['Castle', "Dragon's Lair", 'Grove', 'Vortex']
        all_frontier_options = standard_terrains + advanced_terrains

        frontier_prev_btn = Button(current_x, sec3_y + (input_height - carousel_arrow_button_height) // 2, carousel_arrow_button_width, carousel_arrow_button_height, "", callbacks['on_prev_frontier_proposal'], icon="left_arrow")
        self.panel_elements.append(frontier_prev_btn)

        frontier_display_text = selections['frontier_terrain'] if selections['frontier_terrain'] else "Select"
        frontier_display_box_x = current_x + carousel_arrow_button_width + v_spacing
        frontier_display_box = DisplayBox(frontier_display_box_x, sec3_y, carousel_display_width, input_height, frontier_display_text, font_size=20)
        self.panel_elements.append(frontier_display_box)

        frontier_next_btn_x = frontier_display_box_x + carousel_display_width + v_spacing
        frontier_next_btn = Button(frontier_next_btn_x, sec3_y + (input_height - carousel_arrow_button_height) // 2, carousel_arrow_button_width, carousel_arrow_button_height, "", callbacks['on_next_frontier_proposal'], icon="right_arrow")
        self.panel_elements.append(frontier_next_btn)

        section3_width = carousel_arrow_button_width * 2 + carousel_display_width + v_spacing * 2 # Total width of the carousel
        current_x += section3_width # This is the total content width

        total_content_width = current_x

        # Next/Start Button - This button is NOT part of the scrollable panel.
        # Its position is relative to the main screen. It will be drawn by the main ui_manager.draw(screen) call.
        # Position it near the bottom center of the screen, above the help panel.
        # Assuming screen height of 720 for now. Help panel top is ~570. Button height 50. Margin 10.
        # So button Y can be 570 - 50 - 10 = 510.
        is_last_player = player_index == selections['total_players'] - 1
        btn_text = "Start Game" if is_last_player else "Next Player"
        next_btn = Button(560, 510, 160, 50, btn_text, callbacks['on_next'], font_size=24) # Adjusted Y position
        
        # Enable button if required fields are filled
        required_fields = [
            'name', 'home_terrain', 'frontier_terrain', 
            'home_army_name', 'campaign_army_name',
            'home_army_points', 'campaign_army_points'
        ]
        num_players = selections.get('total_players', 1)
        if num_players > 1:
            required_fields.append('horde_army_name')
            required_fields.append('horde_army_points')
        
        all_fields_filled = all(selections.get(field) for field in required_fields)
        points_are_valid = False
        if all_fields_filled:
            try:
                home_pts = int(selections['home_army_points'])
                campaign_pts = int(selections['campaign_army_points'])
                horde_pts = 0
                if num_players > 1:
                    horde_pts = int(selections['horde_army_points'])

                current_total_allocated = home_pts + campaign_pts + horde_pts
                game_limit = int(selections.get('game_point_limit', 0))
                max_per_army = int(selections.get('max_points_per_army', 0))

                valid_individual_limits = True
                for pts_str_key in ['home_army_points', 'campaign_army_points'] + (['horde_army_points'] if num_players > 1 else []):
                    pts = int(selections[pts_str_key])
                    if pts <= 0 or pts > max_per_army: # Each army must have some points, and not exceed max
                        valid_individual_limits = False; break
                
                if current_total_allocated == game_limit and valid_individual_limits:
                    points_are_valid = True
            except ValueError:
                points_are_valid = False # Non-integer input

        if all_fields_filled and points_are_valid:
            next_btn.is_active = True
        self.fixed_elements.append(next_btn) # Add to fixed_elements
        
        return total_content_width

    def handle_event(self, event, panel_rect_on_screen=None, scroll_offset_x=0):
        state_updates = {} # Dictionary to collect updates {state_key: new_value}

        # Handle panel elements with panel context
        if panel_rect_on_screen: # Only if panel context is relevant for this screen's elements
            for element in self.panel_elements:
                element.handle_event(event, panel_rect_on_screen, scroll_offset_x)
                if isinstance(element, TextInputBox) and element.id and element.is_focused_for_input and event.type == pygame.KEYDOWN:
                    state_updates[element.id] = element.text
        
        # Handle fixed elements without panel context
        for element in self.fixed_elements:
            element.handle_event(event) # No panel_rect_on_screen or scroll_offset_x
            if isinstance(element, TextInputBox) and element.id and element.is_focused_for_input and event.type == pygame.KEYDOWN:
                 # This case might not happen if fixed elements are usually buttons, but good to have
                 state_updates[element.id] = element.text
        return state_updates

    def draw_panel_content(self, screen):
        """Draws elements intended for a scrollable panel."""
        for element in self.panel_elements:
            element.draw(screen)

    def draw_fixed_content(self, screen):
        """Draws elements fixed on the main screen."""
        for element in self.fixed_elements:
            element.draw(screen)
            
    def create_frontier_selection_ui(self, players, selections, callbacks):
        """Builds the UI for selecting the first player and Frontier Terrain."""
        self.panel_elements = []
        self.fixed_elements = []
        y_offset = -100
        
        # We'll use buttons for selection to keep it simple.
        # Who is playing first?
        for i, player in enumerate(players):
            btn = Button(350, 280 + i * 45 + y_offset, 200, 40, player.name, 
                         lambda p=player: callbacks['on_first_player_select'](p.name))
            if selections['first_player'] == player.name:
                btn.is_active = True
            self.fixed_elements.append(btn)

        # Which terrain is the Frontier?
        for i, player in enumerate(players):
            text = f"{player.name}'s: {player.proposed_frontier}"
            btn = Button(650, 280 + i * 45 + y_offset, 280, 40, text, 
                         lambda t=player.proposed_frontier: callbacks['on_frontier_select'](t), font_size=22)
            if selections['frontier_terrain'] == player.proposed_frontier:
                btn.is_active = True
            self.fixed_elements.append(btn)

        # Confirm Button
        confirm_btn = Button(540, 500, 200, 50, "Confirm Selections", callbacks['on_submit'])
        if selections['first_player'] and selections['frontier_terrain']:
            confirm_btn.is_active = True
        self.fixed_elements.append(confirm_btn)

    def create_distance_rolls_ui(self, terrains, callbacks):
        """Builds the UI for inputting terrain distance rolls."""
        self.panel_elements = []
        self.fixed_elements = []
        y_pos = 200
        input_boxes = []

        for i, terrain_obj in enumerate(terrains): # Renamed to avoid conflict
            if not terrain_obj: continue
            
            # Label (as a non-interactive button for now)
            label_text = f"{terrain_obj.owner_name}'s {terrain_obj.type}"
            label = Button(400, y_pos + i * 50, 250, 40, label_text, lambda: None) 
            self.fixed_elements.append(label)

            # Input box
            input_box = TextInputBox(660, y_pos + i * 50, 80, 40)
            self.fixed_elements.append(input_box)
            input_boxes.append({"terrain_id": terrain_obj.id, "input_box": input_box})
        
        submit_btn_y = y_pos + len(terrains) * 50 + 20
        submit_btn = Button(540, submit_btn_y, 200, 50, "Submit Rolls & Start", 
                            lambda: callbacks['on_submit'](input_boxes))
        submit_btn.is_active = True
        self.fixed_elements.append(submit_btn)

    def create_maneuver_decision_ui(self, callbacks):
        """Creates Yes/No buttons for the maneuver decision."""
        self.panel_elements = []
        self.fixed_elements = []
        
        # Example positions, assuming a 1280x720 screen.
        # These buttons will appear below the prompt drawn by the GameEngine.
        center_x = 1280 / 2 
        center_y = 720 / 2 
        prompt_offset_y = 60 # Distance below the centrally drawn prompt text

        yes_btn = Button(center_x - 150 - 10, center_y + prompt_offset_y, 150, 50, "Yes, Maneuver", callbacks['on_maneuver_yes'])
        yes_btn.is_active = True # Visually "enabled"
        self.fixed_elements.append(yes_btn)

        no_btn = Button(center_x + 10, center_y + prompt_offset_y, 150, 50, "No, March On", callbacks['on_maneuver_no'])
        no_btn.is_active = True # Visually "enabled"
        self.fixed_elements.append(no_btn)