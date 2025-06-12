import pygame
from typing import Optional

def blit_text_wrap(surface: Optional[pygame.Surface], text: str, pos: tuple[int, int], font: pygame.font.Font, color: str | tuple[int,int,int], max_width: int, line_spacing: int = 4):
    """
    Draws text wrapped to fit inside a max_width.
    If 'surface' is None, only calculates and returns the total height the text would occupy.
    Otherwise, draws to the surface and returns the total height.
    """
    words = [word.split(' ') for word in text.splitlines()]
    space_width = font.size(' ')[0]
    current_x, current_y = pos
    line_height = font.get_linesize()
    initial_y = pos[1]

    for line_words in words:
        for i, word in enumerate(line_words):
            # Check if word is empty or just spaces, font.size might behave unexpectedly
            if not word.strip(): # If word is empty or just spaces
                if surface: # If rendering, and it's not the first "word" on line, add space
                    if current_x != pos[0]:
                         current_x += space_width
                else: # If calculating, and not first "word", add space
                    if current_x != pos[0]:
                        current_x += space_width
                continue # Skip rendering/further processing for this empty/space word

            word_w, word_h = font.size(word) # Use font.size for dimensions
            if current_x + word_w > pos[0] + max_width and current_x > pos[0]: # Ensure not to wrap if it's the first word and line is too narrow
                current_x = pos[0]  # Reset x to start of line
                current_y += line_height + line_spacing # Move to next line
            
            if surface: # Only render if a surface is provided
                word_surface = font.render(word, True, color)
                surface.blit(word_surface, (current_x, current_y))
            
            current_x += word_w + space_width
        current_x = pos[0]  # Reset x for new paragraph line
        current_y += line_height + line_spacing # Move to next line after a paragraph line

    # Calculate total height
    total_height_span = current_y - initial_y
    if not words or not any(words): return 0 # No text, no height
    # The content ends line_spacing pixels above where current_y is (as current_y is for the *next* line)
    actual_content_height = total_height_span - line_spacing
    return max(0, actual_content_height)