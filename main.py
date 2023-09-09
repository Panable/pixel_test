import pygame
from gettime import get_current_time
from render import create_time_image

# Initialize Pygame (for testing this is in main)
pygame.init()

# Window dimensions
adjusted_width, adjusted_height = 64 * 40, 32 * 40  # Scaling factor applied directly here for clarity

# Create the window
window = pygame.display.set_mode((adjusted_width, adjusted_height))
pygame.display.set_caption("Pixel Time Display")

# Variables for managing the frequency of weather updates
SECONDS_IN_10_MINUTES = 600
update_counter = 0

# Fetch initial image 
img = create_time_image(get_current_time())

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the weather only every 10 minutes
    if update_counter >= SECONDS_IN_10_MINUTES:
        img = create_time_image(get_current_time())
        update_counter = 0  # Reset the counter

    pygame_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
    
    window.blit(pygame_img, (0, 0))
    pygame.display.flip()

    pygame.time.wait(1000)  # Wait for a second before the next loop iteration
    update_counter += 1  # Increment the counter by 1 for each passed second

pygame.quit()

