import pygame
from render_stocks import create_stock_image

# Initialize Pygame
pygame.init()

# Window dimensions
adjusted_width, adjusted_height = 64 * 40, 32 * 40

# Create window
window = pygame.display.set_mode((adjusted_width, adjusted_height))
pygame.display.set_caption("Pixel Stock Display")

# Vars managing the frequency of stock updates
SECONDS_IN_10_MINUTES = 600
update_counter = 0

# Fetch initial stock image 
img = create_stock_image()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Always update the stock image. (Consider reducing the frequency if you find it excessive.)
    img = create_stock_image('AAPL')
    
    pygame_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
    
    window.blit(pygame_img, (0, 0))
    pygame.display.flip()

    pygame.time.wait(1000)  # Wait for a second before the next loop iteration
    update_counter += 1  # Increment the counter by 1 for each passed second

    # Update the stock data only every 10 minutes
    if update_counter >= SECONDS_IN_10_MINUTES:
        img = create_stock_image('AAPL')
        update_counter = 0  # Reset the counter

pygame.quit()

