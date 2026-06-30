import pygame
import sys

pygame.init()

# -----------------------------
# Screen Settings
# -----------------------------
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zebra Crossing Demo")

clock = pygame.time.Clock()

# -----------------------------
# Colors
# -----------------------------
GREEN = (34, 177, 76)
GRAY = (70, 70, 70)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)

# -----------------------------
# Road
# -----------------------------
ROAD_X = 250
ROAD_WIDTH = 300

# Zebra Crossing
ZEBRA_Y = 260
STRIPE_WIDTH = 30
STRIPE_HEIGHT = 10
NUM_STRIPES = 8

# -----------------------------
# Car
# -----------------------------
car = pygame.Rect(ROAD_X + 120, 500, 60, 100)
car_speed = 3

# -----------------------------
# Pedestrian
# -----------------------------
pedestrian = pygame.Rect(ROAD_X - 40, ZEBRA_Y - 15, 20, 30)
pedestrian_speed = 2

pedestrian_crossing = True

# -----------------------------
# Font
# -----------------------------
font = pygame.font.SysFont(None, 30)

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -----------------------------------
    # Move Pedestrian
    # -----------------------------------
    if pedestrian_crossing:
        pedestrian.x += pedestrian_speed

        if pedestrian.left > ROAD_X + ROAD_WIDTH + 40:
            pedestrian_crossing = False

    # -----------------------------------
    # Detect pedestrian on crossing
    # -----------------------------------
    crossing_area = pygame.Rect(ROAD_X, ZEBRA_Y - 20, ROAD_WIDTH, 60)

    pedestrian_on_crossing = pedestrian.colliderect(crossing_area)

    # -----------------------------------
    # Automatic Braking
    # -----------------------------------
    if pedestrian_on_crossing:

        # Stop before crossing
        if car.top > ZEBRA_Y + 40:
            car.y -= car_speed

    else:
        # Continue driving
        car.y -= car_speed

    # Loop car
    if car.bottom < 0:
        car.y = HEIGHT

    # -----------------------------------
    # Draw
    # -----------------------------------
    screen.fill(GREEN)

    # Road
    pygame.draw.rect(screen, GRAY, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))

    # Zebra Crossing
    for i in range(NUM_STRIPES):
        stripe_x = ROAD_X + i * 40
        pygame.draw.rect(
            screen,
            WHITE,
            (stripe_x, ZEBRA_Y, STRIPE_WIDTH, STRIPE_HEIGHT)
        )

    # Car
    pygame.draw.rect(screen, BLUE, car)

    # Pedestrian
    pygame.draw.circle(
        screen,
        RED,
        (pedestrian.centerx, pedestrian.y + 8),
        8
    )

    pygame.draw.rect(
        screen,
        RED,
        (pedestrian.x + 7,
         pedestrian.y + 16,
         6,
         14)
    )

    # Status
    if pedestrian_on_crossing:
        text = font.render("Pedestrian Detected - BRAKING", True, BLACK)
    else:
        text = font.render("Road Clear - Driving", True, BLACK)

    screen.blit(text, (20, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
