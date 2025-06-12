import pygame

class Button:
    """A clickable button that can be in an active/inactive state."""
    def __init__(self, x, y, width, height, text, callback, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.is_active = False # To show if it's selected

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
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
        self.is_active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

    def draw(self, screen):
        border_color = "#FFFF99" if self.is_active else "white"
        pygame.draw.rect(screen, "#333333", self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        text_surf = self.font.render(self.text, True, "white")
        # Position text inside the box
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 5))


class UIManager:
    def __init__(self):
        self.elements = []

    def create_welcome_ui(self, selections, callbacks):
        self.elements = []
        # Player Count Buttons
        for i, count in enumerate([1, 2, 3, 4]):
            btn = Button(445 + i * 90, 300, 60, 40, str(count), lambda c=count: callbacks['on_player_select'](c))
            if selections['num_players'] == count: btn.is_active = True
            self.elements.append(btn)

        # Point Value Buttons
        for i, val in enumerate([15, 24, 30, 36, 60]):
            btn = Button(355 + i * 90, 400, 60, 40, str(val), lambda v=val: callbacks['on_point_select'](v))
            if selections['point_value'] == val: btn.is_active = True
            self.elements.append(btn)

        # Proceed Button
        proceed_btn = Button(560, 500, 160, 50, "Proceed to Setup", callbacks['on_proceed'])
        # Enable button only if both selections have been made
        if selections['num_players'] and selections['point_value']:
            proceed_btn.is_active = True
        self.elements.append(proceed_btn)

    def create_player_setup_ui(self, player_index, selections, callbacks):
        self.elements = []
        y_offset = -100

        # Name Input Box
        name_box = TextInputBox(490, 200 + y_offset, 300, 40, selections['name'])
        self.elements.append(name_box)

        # Home Terrain Buttons
        standard_terrains = ['Coastland', 'Deadland', 'Flatland', 'Highland', 'Swampland', 'Feyland', 'Wasteland']
        for i, terrain in enumerate(standard_terrains):
            btn = Button(350, 280 + i * 45 + y_offset, 200, 40, terrain, lambda t=terrain: callbacks['on_home_select'](t))
            if selections['home_terrain'] == terrain: btn.is_active = True
            self.elements.append(btn)

        # Add Frontier Terrain Buttons
        standard_terrains = ['Coastland', 'Deadland', 'Flatland', 'Highland', 'Swampland', 'Feyland', 'Wasteland']
        advanced_terrains = ['Castle', "Dragon's Lair", 'Grove', 'Vortex']
        all_frontier_options = standard_terrains + advanced_terrains
        
        for i, terrain in enumerate(all_frontier_options):
            btn = Button(650, 280 + i * 35 + y_offset, 200, 30, terrain, lambda t=terrain: callbacks['on_frontier_select'](t), font_size=20)
            if selections['frontier_terrain'] == terrain: btn.is_active = True
            self.elements.append(btn)

        # Next/Start Button
        is_last_player = player_index == selections['total_players'] - 1
        btn_text = "Start Game" if is_last_player else "Next Player"
        next_btn = Button(560, 550 + y_offset, 160, 50, btn_text, callbacks['on_next'])
        if selections['name'] and selections['home_terrain']: # and frontier terrain later
            next_btn.is_active = True
        self.elements.append(next_btn)

    def handle_event(self, event):
        for element in self.elements:
            element.handle_event(event)
            # Update name from text box (a bit simplified)
            if isinstance(element, TextInputBox) and event.type == pygame.KEYDOWN:
                 return element.text # Return new text to update state in main
        return None

    def draw(self, screen):
        for element in self.elements:
            element.draw(screen)
            
    def create_frontier_selection_ui(self, players, selections, callbacks):
        """Builds the UI for selecting the first player and Frontier Terrain."""
        self.elements = []
        y_offset = -100
        
        # We'll use buttons for selection to keep it simple.
        # Who is playing first?
        for i, player in enumerate(players):
            btn = Button(350, 280 + i * 45 + y_offset, 200, 40, player.name, 
                         lambda p=player: callbacks['on_first_player_select'](p.name))
            if selections['first_player'] == player.name:
                btn.is_active = True
            self.elements.append(btn)

        # Which terrain is the Frontier?
        for i, player in enumerate(players):
            text = f"{player.name}'s: {player.proposed_frontier}"
            btn = Button(650, 280 + i * 45 + y_offset, 280, 40, text, 
                         lambda t=player.proposed_frontier: callbacks['on_frontier_select'](t), font_size=22)
            if selections['frontier_terrain'] == player.proposed_frontier:
                btn.is_active = True
            self.elements.append(btn)

        # Confirm Button
        confirm_btn = Button(540, 500, 200, 50, "Confirm Selections", callbacks['on_submit'])
        if selections['first_player'] and selections['frontier_terrain']:
            confirm_btn.is_active = True
        self.elements.append(confirm_btn)

    def create_distance_rolls_ui(self, terrains, callbacks):
        """Builds the UI for inputting terrain distance rolls."""
        self.elements = []
        y_pos = 200
        input_boxes = []

        for terrain in terrains:
            if not terrain: continue
            
            # Label
            label_text = f"{terrain.owner_name}'s {terrain.type}"
            label = Button(400, y_pos, 250, 40, label_text, lambda: None)
            self.elements.append(label)

            # Input box
            input_box = TextInputBox(660, y_pos, 80, 40)
            self.elements.append(input_box)
            input_boxes.append({"terrain_id": terrain.id, "input_box": input_box})
            y_pos += 50
        
        submit_btn = Button(540, y_pos + 20, 200, 50, "Submit Rolls & Start", 
                            lambda: callbacks['on_submit'](input_boxes))
        submit_btn.is_active = True
        self.elements.append(submit_btn)