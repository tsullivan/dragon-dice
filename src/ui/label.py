import pygame

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