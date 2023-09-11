import pygame
from gettime import get_current_time
from render import create_time_image
from getweather import get_weather  # Import the get_weather function

# Init Pygame
pygame.init()

# Window dimensions
adjusted_width, adjusted_height = 64 * 40, 32 * 40

# Create window
window = pygame.display.set_mode((adjusted_width, adjusted_height))
pygame.display.set_caption("Pixel Time Display")

# Vars managing the frequency of weather updates
SECONDS_IN_10_MINUTES = 600
update_counter = 0

# Fetch initial weather icon and temperature
weather_icon_path, _ = get_weather()

# Fetch initial image 
img = create_time_image(get_current_time())

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Always update time.
    img = create_time_image(get_current_time(), weather_icon_path)
    
    # Update the weather only every 10 minutes
    if update_counter >= SECONDS_IN_10_MINUTES:
        weather_icon_path, _ = get_weather()  # Fetch the updated weather icon path every 10 minutes
        update_counter = 0  # Reset the counter

    pygame_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
    
    window.blit(pygame_img, (0, 0))
    pygame.display.flip()

    pygame.time.wait(1000)  # Wait for a second before the next loop iteration
    update_counter += 1  # Increment the counter by 1 for each passed second

pygame.quit()

