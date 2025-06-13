import pygame

class Button:
    """A clickable button that can be in an active/inactive state."""
    def __init__(self, x, y, width, height, text, callback, font_size=24, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.is_active = False # To show if it's selected
        self.icon = icon

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
        bg_color = "#FFFFFF" if self.is_active else "#505A60" # Image: Light grey inactive, white active
        text_color = "#000000" if self.is_active else "#FFFFFF"
        border_color = "#FFFFFF" if self.is_active else "#707A80" # Image: Lighter border for inactive
        
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        if self.icon:
            # Draw icon
            icon_color = text_color # Use text_color for icon
            if self.icon == "left_arrow":
                points = [
                    (self.rect.centerx + 5, self.rect.top + 10),
                    (self.rect.centerx - 5, self.rect.centery),
                    (self.rect.centerx + 5, self.rect.bottom - 10)
                ]
                pygame.draw.lines(screen, icon_color, False, points, 2)
            elif self.icon == "right_arrow":
                points = [
                    (self.rect.centerx - 5, self.rect.top + 10),
                    (self.rect.centerx + 5, self.rect.centery),
                    (self.rect.centerx - 5, self.rect.bottom - 10)
                ]
                pygame.draw.lines(screen, icon_color, False, points, 2)
        else:
            text_surf = self.font.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)