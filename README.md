import pygame
pygame.init()

# -----------------------------
# Font
# -----------------------------
font = pygame.font.SysFont(None, 30)

manual_button = pygame.Rect(20, 180, 180, 40)
obstacle_button = pygame.Rect(20, 230, 180, 40)
lane_button = pygame.Rect(20, 280, 180, 40)
# -----------------------------
# Feature Variables
# -----------------------------
manual_mode = False          # False = Autonomous, True = Manual
obstacle_detection = True    # Obstacle detection enabled
lane_detection = True        # Lane detection enabled


LANES = [
    ROAD_X + 40,
    ROAD_X + 120,
    ROAD_X + 200
]

current_lane = 1
car.x = LANES[current_lane]


running = True

while running:

    clock.tick(60)
    # -------------------------
    # Events
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_m:
                manual_mode = not manual_mode
                print("Manual Mode:", manual_mode)

            elif event.key == pygame.K_o:
                obstacle_detection = not obstacle_detection
                print("Obstacle Detection:", obstacle_detection)

            elif event.key == pygame.K_l:
                lane_detection = not lane_detection
                print("Lane Detection:", lane_detection)

            elif manual_mode:

                if event.key == pygame.K_LEFT:
                    if current_lane > 0:
                        current_lane -= 1
                        car.x = LANES[current_lane]

                elif event.key == pygame.K_RIGHT:
                    if current_lane < 2:
                        current_lane += 1
                        car.x = LANES[current_lane]
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
    crossing_area = pygame.Rect(
        ROAD_X,
        ZEBRA_Y - 20,
        ROAD_WIDTH,
        60
    )

    pedestrian_on_crossing = pedestrian.colliderect(crossing_area)

    # Get keyboard state
    keys = pygame.key.get_pressed()

    # -----------------------------------
    # Car Movement
    # -----------------------------------
    if manual_mode:

        if keys[pygame.K_UP]:
            car.y -= car_speed

        if keys[pygame.K_DOWN]:
            car.y += car_speed

    else:

        if obstacle_detection and pedestrian_on_crossing:

            # Stop before crossing
            if car.top > ZEBRA_Y + 40:
                car.y -= car_speed

        else:
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

    if lane_detection:
        # Left lane line
        pygame.draw.line(
            screen,
            WHITE,
            (ROAD_X + 100, 0),
            (ROAD_X + 100, HEIGHT),
            2
        )

        # Right lane line
        pygame.draw.line(
            screen,
            WHITE,
            (ROAD_X + 200, 0),
            (ROAD_X + 200, HEIGHT),
            2
        )

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

    # -----------------------------
    # Draw Buttons
    # -----------------------------
    screen.blit(font.render("M : Manual Mode", True, BLACK), (20, 180))
    screen.blit(font.render("O : Obstacle Detection", True, BLACK), (20, 210))
    screen.blit(font.render("L : Lane Detection", True, BLACK), (20, 240))

    screen.blit(
        font.render(f"Manual: {'ON' if manual_mode else 'OFF'}", True, WHITE),
        (30, 190)
    )

    screen.blit(
        font.render(f"Obstacle: {'ON' if obstacle_detection else 'OFF'}", True, WHITE),
        (30, 240)
    )

    screen.blit(
        font.render(f"Lane Detect: {'ON' if lane_detection else 'OFF'}", True, WHITE),
        (30, 290)
    )

    pygame.display.flip()

pygame.quit()
sys.exit()

# Controlling the entire simulation
class Game:
    def __init__(self):
        pass

    def run(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

# Autonomous vehicle
class Car:
    def __init__(self):
        self.speed = 0
        self.lane = 1
        self.health = 100

    def move(self):
        pass

    def brake(self):
        pass

    def accelerate(self):
        pass

    def change_lane(self, direction):
        pass

    def draw(self, screen):
        pass

# AI controlled vehicles
class Vehicle:
    def __init__(self):
        self.speed = 0

    def update(self):
        pass

    def draw(self, screen):
        pass
# Pedestrian control
class Pedestrian:
    def __init__(self):
        self.walking = False

    def walk(self):
        pass

    def draw(self, screen):
        pass

# -----------------------------
# Font
# -----------------------------
font = pygame.font.SysFont(None, 30)

manual_button = pygame.Rect(20, 180, 180, 40)
obstacle_button = pygame.Rect(20, 230, 180, 40)
lane_button = pygame.Rect(20, 280, 180, 40)
# -----------------------------
# Feature Variables
# -----------------------------
manual_mode = False          # False = Autonomous, True = Manual
obstacle_detection = True    # Obstacle detection enabled
lane_detection = True        # Lane detection enabled


LANES = [
    ROAD_X + 40,
    ROAD_X + 120,
    ROAD_X + 200
]

current_lane = 1
car.x = LANES[current_lane]


running = True

while running:

    clock.tick(60)
    # -------------------------
    # Events
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_m:
                manual_mode = not manual_mode
                print("Manual Mode:", manual_mode)

            elif event.key == pygame.K_o:
                obstacle_detection = not obstacle_detection
                print("Obstacle Detection:", obstacle_detection)

            elif event.key == pygame.K_l:
                lane_detection = not lane_detection
                print("Lane Detection:", lane_detection)

            elif manual_mode:

                if event.key == pygame.K_LEFT:
                    if current_lane > 0:
                        current_lane -= 1
                        car.x = LANES[current_lane]

                elif event.key == pygame.K_RIGHT:
                    if current_lane < 2:
                        current_lane += 1
                        car.x = LANES[current_lane]
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
    crossing_area = pygame.Rect(
        ROAD_X,
        ZEBRA_Y - 20,
        ROAD_WIDTH,
        60
    )

    pedestrian_on_crossing = pedestrian.colliderect(crossing_area)

    # Get keyboard state
    keys = pygame.key.get_pressed()

    # -----------------------------------
    # Car Movement
    # -----------------------------------
    if manual_mode:

        if keys[pygame.K_UP]:
            car.y -= car_speed

        if keys[pygame.K_DOWN]:
            car.y += car_speed

    else:

        if obstacle_detection and pedestrian_on_crossing:

            # Stop before crossing
            if car.top > ZEBRA_Y + 40:
                car.y -= car_speed

        else:
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

    if lane_detection:
        # Left lane line
        pygame.draw.line(
            screen,
            WHITE,
            (ROAD_X + 100, 0),
            (ROAD_X + 100, HEIGHT),
            2
        )

        # Right lane line
        pygame.draw.line(
            screen,
            WHITE,
            (ROAD_X + 200, 0),
            (ROAD_X + 200, HEIGHT),
            2
        )

# Zebra crossing
class ZebraCrossing:
    def __init__(self):
        self.has_pedestrians = False

    def update(self):
        pass

    def draw(self, screen):
        pass

# Traffic lighting
class TrafficLight:
    def __init__(self):
        self.state = "GREEN"

    def change(self):
        pass

    def draw(self, screen):
        pass

# Road alignment
class Road:
    def __init__(self):
        self.lanes = 3

    def draw(self, screen):
        pass

# Main window
class Dashboard:
    def __init__(self):
        pass

    def draw(self, screen):
        pass

# Camera viewing
class Camera:
    def __init__(self):
        self.detected_objects = []

    def scan(self):
        pass

    def draw(self, screen):
        pass

# Obstacle detection
class ObstacleDetector:
    def __init__(self):
        pass

    def detect(self):
        pass

# Lane detection
class LaneDetector:
    def __init__(self):
        pass

    def detect_lane(self):
        pass

# Positioning
class GPS:
    def __init__(self):
        self.destination = ""

    def update(self):
        pass

    def draw(self, screen):
        pass

# Fuel system
class FuelSystem:
    def __init__(self):
        self.fuel = 100

    def consume(self):
        pass

    def refill(self):
        pass

# Game Events
class EventLog:
    def __init__(self):
        self.events = []

    def add(self, message):
        self.events.append(message)

    def draw(self, screen):
        pass

# Button controls
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, screen):
        pass

    def clicked(self, position):
        return self.rect.collidepoint(position)

# Main menu
class Menu:
    def __init__(self):
        pass

    def draw(self):
        pass

    def update(self):
        pass

# Automation
class AIController:
    def __init__(self):
        pass

    def make_decision(self):
        pass

    def brake(self):
        pass

    def change_lane(self):
        pass

    def accelerate(self):
        pass
