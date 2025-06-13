import pygame
from typing import Optional # Import Optional

class Button:
    """A clickable button that can be in an active/inactive state."""
    def __init__(self, x, y, width, height, text, callback, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.is_active = False # To show if it's selected

    def handle_event(self, event, panel_rect_on_screen=None, scroll_offset_x=0):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            target_rect = self.rect
            mouse_pos = event.pos # Access event.pos only for MOUSEBUTTONDOWN
            
            if panel_rect_on_screen: # This element is on a scrolled panel
                if not panel_rect_on_screen.collidepoint(mouse_pos):
                    return # Click is outside the panel's visible area
                # Transform mouse coordinates to be relative to the content surface
                content_mouse_x = mouse_pos[0] - panel_rect_on_screen.left + scroll_offset_x
                content_mouse_y = mouse_pos[1] - panel_rect_on_screen.top
                mouse_pos = (content_mouse_x, content_mouse_y)
            if target_rect.collidepoint(mouse_pos):
                self.callback()                

    def draw(self, screen):
        bg_color = "#FFFFFF" if self.is_active else "#333333"
        text_color = "#000000" if self.is_active else "#FFFFFF"
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, "white", self.rect, 2, border_radius=8)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class TextInputBox:
    """A box for user text input."""
    def __init__(self, x, y, width, height, text='', font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.id: Optional[str] = None # ID can be a string or None
        self.is_active = False
        self.is_focused_for_input = False # New state for actual text input focus

    def handle_event(self, event, panel_rect_on_screen=None, scroll_offset_x=0):
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_target_rect = self.rect
            mouse_pos = event.pos # Access event.pos only for MOUSEBUTTONDOWN
            effective_mouse_pos = mouse_pos

            if panel_rect_on_screen:
                if not panel_rect_on_screen.collidepoint(mouse_pos):
                    self.is_focused_for_input = False; return
                effective_mouse_pos = (mouse_pos[0] - panel_rect_on_screen.left + scroll_offset_x, mouse_pos[1] - panel_rect_on_screen.top)
            
            if current_target_rect.collidepoint(effective_mouse_pos):
                self.is_focused_for_input = True; self.is_active = True # is_active for border, is_focused for input
            else:
                self.is_focused_for_input = False; self.is_active = False
        if event.type == pygame.KEYDOWN and self.is_focused_for_input:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode.isprintable(): # Only add printable characters
                    self.text += event.unicode

    def draw(self, screen):
        border_color = "#FFFF99" if self.is_focused_for_input else "white"
        pygame.draw.rect(screen, "#333333", self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        text_surf = self.font.render(self.text, True, "white")
        # Vertically center the text and add left padding
        text_rect = text_surf.get_rect(left=self.rect.x + 10, centery=self.rect.centery)
        screen.blit(text_surf, text_rect)

class Label:
    """A simple text label."""
    def __init__(self, x, y, text, font_size=32, color="white"):
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.rect = pygame.Rect(x,y,0,0) # Placeholder, actual rect computed in draw

    def draw(self, screen):
        text_surf = self.font.render(self.text, True, self.color)
        self.rect = text_surf.get_rect(topleft=(self.x, self.y))
        screen.blit(text_surf, self.rect)
    def handle_event(self, event, panel_rect_on_screen=None, scroll_offset_x=0): pass # Labels don't handle events


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
        current_x = 20  # Starting X for the first section in the content panel
        section_padding = 50 # Padding between horizontal sections
        label_font_size = 28
        input_width = 300
        input_height = 40
        button_height = 40
        v_spacing = 10 # Vertical spacing between elements in a section

        # --- Section 1: Player and Army Names ---
        sec1_y = 20
        self.panel_elements.append(Label(current_x, sec1_y, "Player Name:", font_size=label_font_size))
        sec1_y += 35
        name_box = TextInputBox(current_x, sec1_y, input_width, input_height, selections['name'])
        name_box.id = "player_name"
        self.panel_elements.append(name_box)
        sec1_y += input_height + v_spacing + 15

        self.panel_elements.append(Label(current_x, sec1_y, "Home Army Name:", font_size=label_font_size))
        sec1_y += 35
        home_army_name_box = TextInputBox(current_x, sec1_y, input_width, input_height, selections.get('home_army_name', ''))
        home_army_name_box.id = "home_army_name"
        self.panel_elements.append(home_army_name_box)
        sec1_y += input_height + v_spacing

        if selections.get('total_players', 1) > 1: # Only show Horde army name for multiplayer
            self.panel_elements.append(Label(current_x, sec1_y, "Horde Army Name:", font_size=label_font_size))
            sec1_y += 35
            horde_army_name_box = TextInputBox(current_x, sec1_y, input_width, input_height, selections.get('horde_army_name', ''))
            horde_army_name_box.id = "horde_army_name"
            self.panel_elements.append(horde_army_name_box)
            sec1_y += input_height + v_spacing
        
        self.panel_elements.append(Label(current_x, sec1_y, "Campaign Army Name:", font_size=label_font_size))
        sec1_y += 35
        campaign_army_name_box = TextInputBox(current_x, sec1_y, input_width, input_height, selections.get('campaign_army_name', ''))
        campaign_army_name_box.id = "campaign_army_name"
        self.panel_elements.append(campaign_army_name_box)
        
        section1_width = input_width + 20 # Max width of this section
        current_x += section1_width + section_padding

        # --- Section 2: Home Terrain Selection ---
        sec2_y = 20
        self.panel_elements.append(Label(current_x, sec2_y, "Choose Home Terrain:", font_size=label_font_size))
        sec2_y += 35
        standard_terrains = ['Coastland', 'Deadland', 'Flatland', 'Highland', 'Swampland', 'Feyland', 'Wasteland']
        for i, terrain in enumerate(standard_terrains):
            btn = Button(current_x, sec2_y + i * (button_height + v_spacing), 200, button_height, terrain, lambda t=terrain: callbacks['on_home_select'](t))
            if selections['home_terrain'] == terrain: btn.is_active = True
            self.panel_elements.append(btn)
        section2_width = 200 + 20
        current_x += section2_width + section_padding

        # --- Section 3: Frontier Terrain Proposal ---
        sec3_y = 20
        self.panel_elements.append(Label(current_x, sec3_y, "Propose Frontier Terrain:", font_size=label_font_size))
        sec3_y += 35
        advanced_terrains = ['Castle', "Dragon's Lair", 'Grove', 'Vortex']
        all_frontier_options = standard_terrains + advanced_terrains
        for i, terrain in enumerate(all_frontier_options):
            btn = Button(current_x, sec3_y + i * (30 + v_spacing), 200, 30, terrain, lambda t=terrain: callbacks['on_frontier_select'](t), font_size=20)
            if selections['frontier_terrain'] == terrain: btn.is_active = True
            self.panel_elements.append(btn)
        section3_width = 200 + 20
        current_x += section3_width # This is the total content width

        total_content_width = current_x

        # Next/Start Button - This button is NOT part of the scrollable panel.
        # Its position is relative to the main screen. It will be drawn by the main ui_manager.draw(screen) call.
        # Position it near the bottom center of the screen, above the help panel.
        # Assuming screen height of 720 for now. Help panel top is ~570. Button height 50. Margin 10.
        # So button Y can be 570 - 50 - 10 = 510.
        is_last_player = player_index == selections['total_players'] - 1
        btn_text = "Start Game" if is_last_player else "Next Player"
        next_btn = Button(560, 510, 160, 50, btn_text, callbacks['on_next']) # Adjusted Y position
        
        # Enable button if required fields are filled
        required_fields = ['name', 'home_terrain', 'frontier_terrain', 'home_army_name', 'campaign_army_name']
        if selections.get('total_players', 1) > 1:
            required_fields.append('horde_army_name')
        
        if all(selections.get(field) for field in required_fields):
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
