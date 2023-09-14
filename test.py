import pygame
from PIL import Image, ImageDraw

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 64, 32
SCALING_FACTOR = 20  # to upscale the 64x32 for visibility

# Initialize the screen and clock
screen = pygame.display.set_mode((WIDTH * SCALING_FACTOR, HEIGHT * SCALING_FACTOR))
pygame.display.set_caption('Emulated 64x32 Display with PIL and Pygame')
clock = pygame.time.Clock()

def draw_on_pil_image(start_y):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Draw a simple horizontal red line
    d.line((0, start_y, WIDTH, start_y), fill=(255,0,0), width=1)
    
    # Draw a simple green triangle (polygon)
    test_polygon = [(0, start_y), (16, start_y - 8), (32, start_y + 8), (WIDTH, start_y)]
    d.polygon(test_polygon, fill=(0,255,0), outline=(0,0,0))
    
    return img
start_y_global = 26  # Initially set to the middle of the screen

def main():
    global start_y_global
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    start_y_global -= 1
                elif event.key == pygame.K_DOWN:
                    start_y_global += 1
        
        pil_image = draw_on_pil_image(start_y_global)
        pygame_image = pygame.image.fromstring(pil_image.tobytes(), pil_image.size, pil_image.mode)
        
        # Scale for display
        pygame_image = pygame.transform.scale(pygame_image, (WIDTH * SCALING_FACTOR, HEIGHT * SCALING_FACTOR))
        
        screen.blit(pygame_image, (0, 0))
        pygame.display.flip()
        
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
