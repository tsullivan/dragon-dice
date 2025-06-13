import pygame
from typing import Optional

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
        bg_color = "#30353A" # Image: Dark grey background
        border_color = "#FFFF99" if self.is_focused_for_input else "#D0D0D0" # Image: Light grey inactive border
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        text_surf = self.font.render(self.text, True, "white")
        # Vertically center the text and add left padding
        text_rect = text_surf.get_rect(left=self.rect.x + 10, centery=self.rect.centery)
        screen.blit(text_surf, text_rect)