import pygame

class DisplayBox:
    """A non-interactive box for displaying text, styled like an input box."""
    def __init__(self, x, y, width, height, text='', font_size=24, text_color="white", bg_color="#30353A", border_color="#D0D0D0"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=8)

        text_surf = self.font.render(self.text, True, self.text_color)
        # Vertically center the text and horizontally center it
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    def handle_event(self, event, panel_rect_on_screen=None, scroll_offset_x=0): pass # Non-interactive