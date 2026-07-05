import pygame
import random
import sys

# ======================================================
# INITIALIZATION
# ======================================================

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Self-Driving Car Simulator")

clock = pygame.time.Clock()
FPS = 60

# ======================================================
# COLORS
# ======================================================

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (120,120,120)
GREEN = (34,177,76)
RED = (220,20,60)
BLUE = (0,120,255)
YELLOW = (255,255,0)
ORANGE = (255,165,0)

# ======================================================
# ROAD SETTINGS
# ======================================================

ROAD_WIDTH = 420
ROAD_X = (WIDTH-ROAD_WIDTH)//2

LANE_WIDTH = ROAD_WIDTH//3

LANE_CENTERS = [

ROAD_X + LANE_WIDTH//2,

ROAD_X + LANE_WIDTH + LANE_WIDTH//2,

ROAD_X + 2*LANE_WIDTH + LANE_WIDTH//2

]

ROAD_SPEED = 6

line_offset = 0

# ======================================================
# PLAYER SETTINGS
# ======================================================

CAR_WIDTH = 55
CAR_HEIGHT = 95

current_lane = 1

car_x = LANE_CENTERS[current_lane] - CAR_WIDTH//2
car_y = HEIGHT-140

speed = ROAD_SPEED

max_speed = 10
min_speed = 2

autonomous = False

distance_remaining = 50000

# ======================================================
# LOAD IMAGES
# ======================================================

player_car = pygame.image.load(
    "images/player_car.png"
).convert_alpha()

player_car = pygame.transform.scale(
    player_car,
    (CAR_WIDTH,CAR_HEIGHT)
)

traffic_car = pygame.image.load(
    "images/traffic_car.png"
).convert_alpha()

traffic_car = pygame.transform.scale(
    traffic_car,
    (CAR_WIDTH,CAR_HEIGHT)
)

pedestrian_img = pygame.image.load(
    "images/pedestrian.png"
).convert_alpha()

pedestrian_img = pygame.transform.scale(
    pedestrian_img,
    (45,70)
)

# ======================================================
# FONTS
# ======================================================

font = pygame.font.SysFont("Arial",22)
big_font = pygame.font.SysFont("Arial",38)

# ======================================================
# TRAFFIC
# ======================================================

traffic = []

for i in range(5):

    lane = random.randint(0, 2)

    direction = random.choice([1, -1])  # 1 = down, -1 = up

    if direction == 1:
        y_pos = -i * 250
    else:
        y_pos = HEIGHT + i * 250

    traffic.append({

        "lane": lane,

        "x": LANE_CENTERS[lane] - CAR_WIDTH // 2,

        "y": y_pos,

        "speed": random.randint(4, 8),

        "direction": direction
    })

# ======================================================
# TRAFFIC LIGHT
# ======================================================

traffic_light_state = "GREEN"

traffic_timer = 0

traffic_light_y = -800

# ======================================================
# PEDESTRIAN
# ======================================================

pedestrian_active = False

pedestrian_x = ROAD_X-40

pedestrian_y = traffic_light_y+90

pedestrian_speed = 2

# ======================================================
# ZEBRA CROSSING
# ======================================================

zebra_y = traffic_light_y + 70

# ======================================================
# WARNING FLAGS
# ======================================================

collision_warning = False

destination_reached = False

# ======================================================
# FUNCTIONS
# ======================================================

def draw_road():

    global line_offset

    screen.fill(GREEN)

    pygame.draw.rect(
        screen,
        GRAY,
        (ROAD_X,0,ROAD_WIDTH,HEIGHT)
    )

    pygame.draw.line(
        screen,
        YELLOW,
        (ROAD_X,0),
        (ROAD_X,HEIGHT),
        5
    )

    pygame.draw.line(
        screen,
        YELLOW,
        (ROAD_X+ROAD_WIDTH,0),
        (ROAD_X+ROAD_WIDTH,HEIGHT),
        5
    )

    for y in range(-60,HEIGHT+60,60):

        pygame.draw.line(
            screen,
            WHITE,
            (ROAD_X+LANE_WIDTH,
             y+line_offset),
            (ROAD_X+LANE_WIDTH,
             y+30+line_offset),
            5
        )

        pygame.draw.line(
            screen,
            WHITE,
            (ROAD_X+2*LANE_WIDTH,
             y+line_offset),
            (ROAD_X+2*LANE_WIDTH,
             y+30+line_offset),
            5
        )

    line_offset += speed

    if line_offset >= 60:
        line_offset = 0
# ======================================================
# PLAYER FUNCTIONS
# ======================================================

def get_player_rect():
    return pygame.Rect(car_x, car_y, CAR_WIDTH, CAR_HEIGHT)


def move_player():

    global car_x
    global speed
    global current_lane

    keys = pygame.key.get_pressed()

    # Steering
    if keys[pygame.K_LEFT]:
        car_x -= 6

    if keys[pygame.K_RIGHT]:
        car_x += 6

    # Speed control
    if keys[pygame.K_UP]:
        speed += 0.05

    if keys[pygame.K_DOWN]:
        speed -= 0.05

    # Limit speed
    if speed > max_speed:
        speed = max_speed

    if speed < min_speed:
        speed = min_speed

    # Stay inside road
    left = ROAD_X
    right = ROAD_X + ROAD_WIDTH - CAR_WIDTH

    if car_x < left:
        car_x = left

    if car_x > right:
        car_x = right

    # Update current lane
    distances = []

    for lane in LANE_CENTERS:
        distances.append(abs((car_x + CAR_WIDTH // 2) - lane))

    current_lane = distances.index(min(distances))

def is_at_zebra(car):

    zebra_zone_top = zebra_y
    zebra_zone_bottom = zebra_y + 80

    car_bottom = car["y"] + CAR_HEIGHT

    return zebra_zone_top - 10 <= car_bottom <= zebra_zone_bottom + 10


# ======================================================
# TRAFFIC FUNCTIONS
# ======================================================

def update_traffic():

    global collision_warning

    collision_warning = False

    SAFE_DISTANCE = 130

    player_rect = get_player_rect()

    stop_line = zebra_y - CAR_HEIGHT - 20

    for car in traffic:

        blocked = False

        # ==================================================
        # 1. SAFE DISTANCE (prevents overlapping cars)
        # ==================================================
        for other in traffic:
            if other == car:
                continue

            if other["lane"] == car["lane"]:

                if other["y"] > car["y"]:  # car ahead

                    if other["y"] - car["y"] < SAFE_DISTANCE:
                        blocked = True
                        break

        # STOP at zebra crossing
        if is_at_zebra(car):
            blocked = True


        # ==================================================
        # 2. TRAFFIC LIGHT STOP
        # ==================================================
        if traffic_light_state == "RED" and is_at_zebra(car):
            blocked = True

        # ==================================================
        # 3. PEDESTRIAN CROSSING STOP
        # ==================================================
        if pedestrian_active and is_at_zebra(car):
            blocked = True

        # ==================================================
        # MOVE IF SAFE
        # ==================================================
        if not blocked:
            car["y"] += car["speed"] * car["direction"]

        # ==================================================
        # RESPAWN CAR
        # ==================================================
        if car["y"] > HEIGHT + 150 or car["y"] < -300:

            lane = random.randint(0, 2)

            car["lane"] = lane
            car["x"] = LANE_CENTERS[lane] - CAR_WIDTH // 2

            car["direction"] = random.choice([1, -1])

            if car["direction"] == 1:
                car["y"] = -random.randint(-900, -200)
            else:
                car["y"] = random.randint(HEIGHT + 200, HEIGHT + 900)
            car["speed"] = random.randint(4, 8)

        # ==================================================
        # COLLISION CHECK (player vs traffic)
        # ==================================================
        rect = pygame.Rect(
            car["x"],
            car["y"],
            CAR_WIDTH,
            CAR_HEIGHT
        )

        if player_rect.colliderect(rect):
            collision_warning = True

def draw_traffic():

    for car in traffic:

        screen.blit(
            traffic_car,
            (car["x"], car["y"])
        )


# ======================================================
# AUTONOMOUS DRIVING
# ======================================================

def autonomous_drive():

    global car_x, current_lane, speed

    target_lane = current_lane
    obstacle = None

    player_rect = get_player_rect()

    # ==================================================
    # FIND NEAREST OBSTACLE AHEAD
    # ==================================================
    for car in traffic:

        if car["lane"] != current_lane:
            continue

        if car["y"] < car_y:

            distance = car_y - car["y"]

            if obstacle is None:
                obstacle = (car, distance)

            elif distance < obstacle[1]:
                obstacle = (car, distance)

    # ==================================================
    # STOP LOGIC (TRAFFIC LIGHT + PEDESTRIAN)
    # ==================================================
    stop_zone = zebra_y

    if traffic_light_state == "RED" or pedestrian_active:

        if car_y < stop_zone < car_y + 140:
            speed = max(speed - 0.25, 0)
            return

    # ==================================================
    # OBSTACLE AVOIDANCE
    # ==================================================
    if obstacle:

        car_data, distance = obstacle

        if distance < 180:

            speed = max(speed - 0.1, 2)

            left_free = True
            right_free = True

            # check left lane
            if current_lane > 0:
                for other in traffic:
                    if other["lane"] == current_lane - 1:
                        if abs(other["y"] - car_y) < 140:
                            left_free = False
            else:
                left_free = False

            # check right lane
            if current_lane < 2:
                for other in traffic:
                    if other["lane"] == current_lane + 1:
                        if abs(other["y"] - car_y) < 140:
                            right_free = False
            else:
                right_free = False

            if left_free:
                target_lane = current_lane - 1

            elif right_free:
                target_lane = current_lane + 1

        else:
            speed = min(speed + 0.05, max_speed)

    else:
        speed = min(speed + 0.05, max_speed)

    # ==================================================
    # SMOOTH LANE MOVEMENT
    # ==================================================
    target_x = LANE_CENTERS[target_lane] - CAR_WIDTH // 2

    if car_x < target_x:
        car_x += 4
    elif car_x > target_x:
        car_x -= 4

    current_lane = target_lane
# ======================================================
# PLAYER DRAW
# ======================================================

def draw_player():

    screen.blit(
        player_car,
        (car_x, car_y)
    )


# ======================================================
# DESTINATION
# ======================================================

def update_destination():

    global distance_remaining
    global destination_reached

    if not destination_reached:

        distance_remaining -= speed

        if distance_remaining <= 0:

            distance_remaining = 0

            destination_reached = True
# ======================================================
# TRAFFIC LIGHT FUNCTIONS
# ======================================================

def update_traffic_light():

    global traffic_timer
    global traffic_light_state
    global traffic_light_y
    global zebra_y
    global pedestrian_y
    global pedestrian_active

    traffic_timer += 1

    if traffic_timer >= 300:
        traffic_timer = 0

        if traffic_light_state == "GREEN":
            traffic_light_state = "YELLOW"

        elif traffic_light_state == "YELLOW":
            traffic_light_state = "RED"
            pedestrian_active = True

        else:
            traffic_light_state = "GREEN"
            pedestrian_active = False

    traffic_light_y += speed
    zebra_y += speed
    pedestrian_y += speed

    if traffic_light_y > HEIGHT + 100:

        traffic_light_y = -900
        zebra_y = traffic_light_y + 70
        pedestrian_y = zebra_y
        pedestrian_active = False


def draw_traffic_light():

    pole_x = ROAD_X + ROAD_WIDTH + 30

    pygame.draw.rect(
        screen,
        BLACK,
        (pole_x, traffic_light_y, 18, 90)
    )

    color = GREEN

    if traffic_light_state == "RED":
        color = RED

    elif traffic_light_state == "YELLOW":
        color = ORANGE

    pygame.draw.circle(
        screen,
        color,
        (pole_x + 9, traffic_light_y + 20),
        8
    )


# ======================================================
# ZEBRA CROSSING
# ======================================================

def draw_zebra():

    for i in range(10):

        pygame.draw.rect(
            screen,
            WHITE,
            (
                ROAD_X + i * 42,
                zebra_y,
                20,
                12
            )
        )


# ======================================================
# PEDESTRIAN
# ======================================================

def update_pedestrian():

    global pedestrian_x

    if pedestrian_active:

        pedestrian_x += pedestrian_speed

        if pedestrian_x > ROAD_X + ROAD_WIDTH + 30:

            pedestrian_x = ROAD_X - 40


def draw_pedestrian():

    if pedestrian_active:

        screen.blit(
            pedestrian_img,
            (pedestrian_x, pedestrian_y - 40)
        )


# ======================================================
# DASHBOARD
# ======================================================

def draw_dashboard():

    pygame.draw.rect(
        screen,
        (40, 40, 40),
        (10, 10, 270, 170),
        border_radius=10
    )

    mode = "AUTONOMOUS"

    if not autonomous:
        mode = "MANUAL"

    dashboard = [

        f"Speed : {speed:.1f}",

        f"Lane : {current_lane + 1}",

        f"Mode : {mode}",

        f"Destination : {int(distance_remaining)} m",

        f"Traffic Light : {traffic_light_state}"

    ]

    if collision_warning:

        dashboard.append("WARNING : Vehicle Ahead")

    for i, text in enumerate(dashboard):

        surface = font.render(text, True, WHITE)

        screen.blit(
            surface,
            (25, 25 + i * 28)
        )


# ======================================================
# DESTINATION SCREEN
# ======================================================

def draw_destination():

    if destination_reached:

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)

        screen.blit(overlay, (0, 0))

        txt = big_font.render(
            "DESTINATION REACHED",
            True,
            GREEN
        )

        screen.blit(
            txt,
            (
                WIDTH // 2 - txt.get_width() // 2,
                HEIGHT // 2 - 30
            )
        )


# ======================================================
# MAIN GAME LOOP
# ======================================================

running = True

while running:

    clock.tick(FPS)

    # ---------------- EVENTS ----------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_a:
                autonomous = not autonomous

    # ---------------- UPDATE ----------------

    update_destination()

    update_traffic()

    update_traffic_light()

    update_pedestrian()

    if autonomous:

        autonomous_drive()

    else:

        move_player()

    # ---------------- DRAW ----------------

    draw_road()

    draw_zebra()

    draw_traffic()

    draw_player()

    draw_traffic_light()

    draw_pedestrian()

    draw_dashboard()

    draw_destination()

    pygame.display.flip()

pygame.quit()
sys.exit()