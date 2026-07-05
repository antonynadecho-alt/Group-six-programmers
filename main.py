import pygame
import sys
import random
import time

pygame.init()

# -----------------------------
# Screen Settings
# -----------------------------
WIDTH = 800
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Matatu - Self-Driving Simulation")
clock = pygame.time.Clock()

# -----------------------------
# Colors
# -----------------------------
GREEN = (34, 177, 76)
GRAY = (60, 60, 60)
LANE_LINE = (230, 230, 230)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
YELLOW = (255, 220, 0)

# -----------------------------
# Road & Lane Setup
# -----------------------------
ROAD_X = 200
ROAD_WIDTH = 400
NUM_LANES = 3
LANE_WIDTH = ROAD_WIDTH // NUM_LANES
LANE_CENTERS = [ROAD_X + LANE_WIDTH * i + LANE_WIDTH // 2 for i in range(NUM_LANES)]

# -----------------------------
# Fonts
# -----------------------------
font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 22)

# -----------------------------
# Matatu (Self-Driving Vehicle)
# -----------------------------
CAR_W, CAR_H = 50, 90
current_lane = 1
car = pygame.Rect(0, 0, CAR_W, CAR_H)
car.centerx = LANE_CENTERS[current_lane]
car.bottom = 600

base_speed = 5
car_speed = base_speed
braking = False
was_stopped = False
lane_change_cooldown = 0
LANE_CHANGE_DELAY = 20

# -----------------------------
# Game state
# -----------------------------
score = 0
distance_m = 0
collisions = 0
start_time = time.time()

# -----------------------------
# Obstacle Classes
# -----------------------------
class Vehicle:
    def __init__(self):
        self.lane = random.randint(0, NUM_LANES - 1)
        self.rect = pygame.Rect(0, 0, 50, 90)
        self.rect.centerx = LANE_CENTERS[self.lane]
        self.rect.bottom = -50
        self.color = random.choice([ORANGE, (150, 0, 200), (0, 150, 150)])
        self.danger = 3
        self.kind = "Vehicle"

    def update(self, scroll_speed):
        self.rect.y += scroll_speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=6)


class ZebraCrossing:
    def __init__(self):
        self.rect = pygame.Rect(ROAD_X, -40, ROAD_WIDTH, 30)
        self.pedestrian_present = random.random() < 0.35  # most crossings are empty

        if self.pedestrian_present:
            self.walk_dir = random.choice([1, -1])  # 1 = left->right, -1 = right->left
            self.ped_speed = 2.5

            if self.walk_dir == 1:
                start_x = ROAD_X - 30
            else:
                start_x = ROAD_X + ROAD_WIDTH + 10

            self.ped_rect = pygame.Rect(0, 0, 18, 26)
            self.ped_rect.x = start_x
            self.ped_rect.centery = self.rect.centery
            self.has_started_walking = False

        self.danger = 3 if self.pedestrian_present else 0
        self.kind = "Zebra Crossing"

    def update(self, scroll_speed, near_car):
        self.rect.y += scroll_speed
        if self.pedestrian_present:
            self.ped_rect.y = self.rect.centery - self.ped_rect.height // 2

            if near_car:
                self.has_started_walking = True

            if self.has_started_walking:
                self.ped_rect.x += self.ped_speed * self.walk_dir

                if self.walk_dir == 1 and self.ped_rect.x > ROAD_X + ROAD_WIDTH + 10:
                    self.pedestrian_present = False
                elif self.walk_dir == -1 and self.ped_rect.right < ROAD_X - 10:
                    self.pedestrian_present = False

    def draw(self, screen):
        for i in range(8):
            stripe = pygame.Rect(ROAD_X + i * (ROAD_WIDTH // 8), self.rect.y, 25, 30)
            pygame.draw.rect(screen, WHITE, stripe)
        if self.pedestrian_present:
            pygame.draw.circle(screen, RED, (self.ped_rect.centerx, self.ped_rect.y + 6), 7)
            pygame.draw.rect(screen, RED, (self.ped_rect.x + 4, self.ped_rect.y + 12, 8, 14))


obstacles = []

# Vehicles spawn-check frequently
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1300)

# Zebra crossings spawn-check far less often, creating a bigger gap between them
ZEBRA_SPAWN_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ZEBRA_SPAWN_EVENT, 4000)

scroll_offset = 0

# -----------------------------
# Event log
# -----------------------------
event_log = []
def log_event(msg):
    event_log.append(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if len(event_log) > 4:
        event_log.pop(0)

log_event("Autonomous trip started.")

# -----------------------------
# Lookahead zone (for lane-change decisions on vehicles)
# -----------------------------
LOOKAHEAD_TOP = car.top - 180
LOOKAHEAD_BOTTOM = car.top + 10

def get_danger_in_lane(lane_index):
    lookahead_rect = pygame.Rect(LANE_CENTERS[lane_index] - LANE_WIDTH // 2,
                                  LOOKAHEAD_TOP, LANE_WIDTH, LOOKAHEAD_BOTTOM - LOOKAHEAD_TOP)
    highest = 0
    for obs in obstacles:
        if isinstance(obs, Vehicle):
            if obs.lane == lane_index and obs.rect.colliderect(lookahead_rect):
                highest = max(highest, obs.danger)
    return highest


# -----------------------------
# Stop zone (close range, only for pedestrian crossings)
# -----------------------------
STOP_ZONE_TOP = car.top - 70
STOP_ZONE_BOTTOM = car.top + 10
NEAR_ZONE_TOP = car.top - 150
NEAR_ZONE_BOTTOM = car.top + 10

def crossing_is_near(obs):
    near_zone = pygame.Rect(ROAD_X, NEAR_ZONE_TOP, ROAD_WIDTH, NEAR_ZONE_BOTTOM - NEAR_ZONE_TOP)
    return obs.rect.colliderect(near_zone)

def pedestrian_blocking_car():
    stop_zone = pygame.Rect(ROAD_X, STOP_ZONE_TOP, ROAD_WIDTH, STOP_ZONE_BOTTOM - STOP_ZONE_TOP)
    for obs in obstacles:
        if isinstance(obs, ZebraCrossing) and obs.pedestrian_present:
            if obs.ped_rect.colliderect(stop_zone):
                return obs
    return None


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == SPAWN_EVENT:
            if random.random() < 0.6:
                obstacles.append(Vehicle())

        if event.type == ZEBRA_SPAWN_EVENT:
            if random.random() < 0.7:
                obstacles.append(ZebraCrossing())

    elapsed = time.time() - start_time

    # ---------------- AUTONOMOUS DECISION LOGIC ----------------
    blocking_crossing = pedestrian_blocking_car()

    if blocking_crossing is not None:
        braking = True
        car_speed = 0
        if not was_stopped:
            log_event("Pedestrian crossing — STOPPING")
        was_stopped = True
    else:
        if was_stopped:
            log_event("Pedestrian cleared — resuming")
        was_stopped = False

        danger_current = get_danger_in_lane(current_lane)

        if danger_current >= 2:
            best_lane = current_lane
            best_danger = danger_current

            for lane_i in range(NUM_LANES):
                if lane_i == current_lane:
                    continue
                d = get_danger_in_lane(lane_i)
                if d < best_danger:
                    best_danger = d
                    best_lane = lane_i

            if best_lane != current_lane and lane_change_cooldown == 0:
                direction = "RIGHT" if best_lane > current_lane else "LEFT"
                current_lane = best_lane
                lane_change_cooldown = LANE_CHANGE_DELAY
                log_event(f"Auto-changed lane {direction} to avoid vehicle")
                braking = False
                car_speed = base_speed
            else:
                braking = True
                car_speed = 1
                if random.random() < 0.05:
                    log_event("Braking for vehicle ahead")
        else:
            braking = False
            car_speed = base_speed

    if lane_change_cooldown > 0:
        lane_change_cooldown -= 1

    target_x = LANE_CENTERS[current_lane]
    if car.centerx < target_x:
        car.centerx = min(car.centerx + 8, target_x)
    elif car.centerx > target_x:
        car.centerx = max(car.centerx - 8, target_x)

    # ---------------- UPDATE OBSTACLES ----------------
    for obs in obstacles:
        if isinstance(obs, Vehicle):
            obs.update(car_speed)
        elif isinstance(obs, ZebraCrossing):
            near = crossing_is_near(obs)
            obs.update(car_speed, near)

    still_active = []
    for obs in obstacles:
        off_screen = obs.rect.top > HEIGHT
        if off_screen:
            score += 10
        else:
            still_active.append(obs)
    obstacles = still_active

    # ---------------- COLLISION CHECK ----------------
    for obs in obstacles:
        if isinstance(obs, Vehicle):
            if car.colliderect(obs.rect):
                collisions += 1
                log_event(f"Collided with {obs.kind}!")
                obstacles.remove(obs)
                break
        elif isinstance(obs, ZebraCrossing):
            if obs.pedestrian_present and car.colliderect(obs.ped_rect):
                collisions += 1
                log_event("Hit a pedestrian!")
                obs.pedestrian_present = False
                break

    distance_m += car_speed / 10
    scroll_offset = (scroll_offset + car_speed) % 80

    # ---------------- DRAW ----------------
    screen.fill(GREEN)
    pygame.draw.rect(screen, GRAY, (ROAD_X, 0, ROAD_WIDTH, HEIGHT))

    for lane_i in range(1, NUM_LANES):
        x = ROAD_X + lane_i * LANE_WIDTH
        for y in range(-80, HEIGHT, 80):
            pygame.draw.rect(screen, LANE_LINE, (x - 2, y + scroll_offset, 4, 40))

    pygame.draw.rect(screen, WHITE, (ROAD_X - 5, 0, 5, HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_X + ROAD_WIDTH, 0, 5, HEIGHT))

    for obs in obstacles:
        obs.draw(screen)

    pygame.draw.rect(screen, BLUE, car, border_radius=8)
    pygame.draw.rect(screen, WHITE, (car.x + 8, car.y + 10, car.width - 16, 20))

    # ---------------- HUD ----------------
    status_label = "STOPPED (pedestrian)" if car_speed == 0 else ("BRAKING" if braking else "")
    hud_lines = [
        f"Speed: {car_speed * 10} km/h" + (f"  [{status_label}]" if status_label else ""),
        f"Distance: {distance_m:.1f} m",
        f"Score: {score}",
        f"Lane: {current_lane + 1} / {NUM_LANES}",
        f"Elapsed: {elapsed:.1f}s",
        f"Collisions: {collisions}",
    ]
    panel = pygame.Rect(10, 10, 230, 140)
    pygame.draw.rect(screen, WHITE, panel)
    pygame.draw.rect(screen, BLACK, panel, 2)
    for i, line in enumerate(hud_lines):
        screen.blit(small_font.render(line, True, BLACK), (18, 16 + i * 22))

    log_panel = pygame.Rect(WIDTH - 280, 10, 270, 110)
    pygame.draw.rect(screen, WHITE, log_panel)
    pygame.draw.rect(screen, BLACK, log_panel, 2)
    for i, line in enumerate(event_log):
        screen.blit(small_font.render(line, True, BLACK), (log_panel.x + 8, log_panel.y + 6 + i * 22))

    info_text = small_font.render("Fully autonomous mode — vehicle drives itself", True, BLACK)
    screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT - 30))

    pygame.display.flip()

pygame.quit()
sys.exit()