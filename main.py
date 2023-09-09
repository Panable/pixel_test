import pygame
from gettime import get_current_time
import render

# Initialize Pygame
pygame.init()

# Define the logical window size
logical_width, logical_height = 64, 32

# Define the scaling factor
scaling_factor = 40

# Calculate the actual window size
window_width, window_height = logical_width * scaling_factor, logical_height * scaling_factor

# Create a window with the actual size
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Scaled Window")

# Create a clock to control the frame rate
clock = pygame.time.Clock()

# Create a 2D array to represent pixel colors (64x32 pixels)
pixel_colors = [[(0, 0, 0) for _ in range(logical_height)] for _ in range(logical_width)]

def format_time(current_time):
    hour_str = str(current_time[0]).zfill(2)
    minute_str = str(current_time[1]).zfill(2)
    return hour_str, minute_str

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    window.fill((0, 0, 0))  # Fill with black

    # Update the time
    current_time = get_current_time()
    hour_str, minute_str = format_time(current_time)

    # Clear time region 
    x_margin, y_margin = 20, 2
    render.clear_region(x_margin, x_margin + 24, y_margin, y_margin + 7, pixel_colors)  
    # Render the new time
    render.render_time(hour_str, minute_str, pixel_colors)

    # Draw pixels 
    for x in range(logical_width):
        for y in range(logical_height):
            color = pixel_colors[x][y]  # Use [x][y] indexing
            scaled_x, scaled_y = x * scaling_factor, y * scaling_factor
            pygame.draw.rect(window, color, (scaled_x, scaled_y, scaling_factor, scaling_factor))

    # Update the display
    pygame.display.flip()

    # Limit the frame rate
    clock.tick(50)

# Quit Pygame
pygame.quit()

