import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and colors for retro style
WIDTH, HEIGHT = 800, 600
FPS = 60

# Color definitions
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
RED        = (255, 0, 0)
GREEN      = (0, 255, 0)
BLUE       = (0, 0, 255)
YELLOW     = (255, 255, 0)
BG_COLOR   = (20, 20, 40)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Math Platformer")
clock = pygame.time.Clock()

# Fonts for text (pixelated look!)
font_small = pygame.font.SysFont("couriernew", 20)
font_medium = pygame.font.SysFont("couriernew", 28)
font_large = pygame.font.SysFont("couriernew", 36)

# Define gravity and player properties
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_SPEED = 15

# Define questions for the 5 topics
# Each question has a prompt, a list of 4 options, and a correct answer index (0-based)
questions = [
    {
        "prompt": "Cross-Sections: What is the typical shape when slicing a sphere?",
        "options": ["Circle", "Triangle", "Square", "Ellipse"],
        "answer": 0
    },
    {
        "prompt": "Composite Area: A figure has a rectangle (20) and triangle (10). Total area is?",
        "options": ["30", "20", "10", "40"],
        "answer": 0
    },
    {
        "prompt": "Surface Area: Cylinder lateral area 50 and 2 bases of 12 each gives total area?",
        "options": ["74", "50", "100", "62"],
        "answer": 0
    },
    {
        "prompt": "Volume: What is the volume of a cube with side length 3?",
        "options": ["9", "27", "18", "81"],
        "answer": 1
    },
    {
        "prompt": "Circle Eq: Equation of a circle with center (1,1) and radius 3?",
        "options": ["(x-1)^2+(y-1)^2=9", "(x-1)^2+(y-1)^2=6", "(x+1)^2+(y+1)^2=9", "(x-1)^2+(y-1)^2=3"],
        "answer": 0
    },    
]

# ----------------------------------------------------------------
# Define sprite classes

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 40))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        # Left/right movement
        if keys[pygame.K_LEFT]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx = PLAYER_SPEED
        
        # Apply gravity
        self.vel_y += GRAVITY
        dy = self.vel_y

        # Move horizontally and check collision with platforms
        self.rect.x += dx
        self.collide(dx, 0, platforms)

        # Move vertically and check collision with platforms
        self.rect.y += dy
        self.on_ground = False
        self.collide(0, dy, platforms)

    def jump(self, platforms):
        # Only jump if on the ground
        if self.on_ground:
            self.vel_y = -JUMP_SPEED

    def collide(self, dx, dy, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if dx > 0:
                    self.rect.right = plat.rect.left
                if dx < 0:
                    self.rect.left = plat.rect.right
                if dy > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x, y))

class ChallengeZone(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, q_index):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.q_index = q_index  # Which question this zone triggers
        self.solved = False

# ----------------------------------------------------------------
# Create level layout

# Group for all sprites
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
challenges = pygame.sprite.Group()

# Create ground platform
ground = Platform(0, HEIGHT - 40, WIDTH * 3, 40)
platforms.add(ground)
all_sprites.add(ground)

# Create some platforms (for retro feel, these are simple rectangles)
platform_list = [
    (200, HEIGHT - 140, 150, 20),
    (400, HEIGHT - 240, 150, 20),
    (650, HEIGHT - 180, 150, 20),
    (900, HEIGHT - 260, 150, 20),
    (1150, HEIGHT - 200, 150, 20)
]

for x, y, w, h in platform_list:
    plat = Platform(x, y, w, h)
    platforms.add(plat)
    all_sprites.add(plat)

# Create five challenge zones – place one near each platform for demonstration
challenge_positions = [
    (250, HEIGHT - 180, 50, 40),   # for topic 1
    (450, HEIGHT - 280, 50, 40),   # for topic 2
    (700, HEIGHT - 220, 50, 40),   # for topic 3
    (950, HEIGHT - 300, 50, 40),   # for topic 4
    (1200, HEIGHT - 240, 50, 40)   # for topic 5
]

for i, pos in enumerate(challenge_positions):
    x, y, w, h = pos
    zone = ChallengeZone(x, y, w, h, i)
    challenges.add(zone)
    all_sprites.add(zone)

# Create the player
player = Player(50, HEIGHT - 100)
all_sprites.add(player)

# Camera offset for scrolling the level
camera_x = 0

# Game states: "playing" and "challenge"
game_state = "playing"
current_question = None
message = ""  # To display feedback

# ----------------------------------------------------------------
# Helper functions for drawing text

def draw_text(surface, text, font, color, pos):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_centered_text(surface, text, font, color, ypos):
    text_surface = font.render(text, True, color)
    x = (WIDTH - text_surface.get_width()) // 2
    surface.blit(text_surface, (x, ypos))

def draw_text_wrapped(surface, text, pos, font, color, max_width, line_spacing=5):
    """ Draws wrapped text on the surface. 
    - surface: the pygame surface to draw on.
    - text: the complete text string.
    - pos: a tuple (x, y) where text drawing starts.
    - font: the pygame.font.Font object.
    - color: text color.
    - max_width: maximum width (in pixels) before wrapping.
    - line_spacing: extra pixels between lines.
    """
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    if current_line:
        lines.append(current_line)
    
    x, y = pos
    for line in lines:
        rendered_line = font.render(line.strip(), True, color)
        surface.blit(rendered_line, (x, y))
        y += rendered_line.get_height() + line_spacing

# ----------------------------------------------------------------
# Main game loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check for jump
        if event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if event.key == pygame.K_SPACE:
                    player.jump(platforms)
            elif game_state == "challenge":
                # In challenge mode, allow answering with 1-4 keys
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    answer = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3}[event.key]
                    correct = questions[current_question]["answer"]
                    if answer == correct:
                        message = "Correct! Continue your journey."
                        # Mark challenge as solved (remove its collision)
                        for ch in challenges:
                            if ch.q_index == current_question:
                                ch.solved = True
                                all_sprites.remove(ch)
                        game_state = "playing"
                    else:
                        message = "Incorrect! Try again. (Press 1-4 to answer)"
    
    # Only update game objects when not in challenge mode
    if game_state == "playing":
        player.update(platforms)

        # Check for collision with any challenge zone that isn't solved
        hit_zones = pygame.sprite.spritecollide(player, challenges, False)
        for zone in hit_zones:
            if not zone.solved:
                current_question = zone.q_index
                game_state = "challenge"
                message = ""
                break

        # Update camera offset (scrolling to right as player moves)
        camera_x = player.rect.x - 100

    # Draw background
    screen.fill(BG_COLOR)

    # Draw all sprites with camera offset
    for sprite in all_sprites:
        offset_rect = sprite.rect.copy()
        offset_rect.x -= camera_x
        screen.blit(sprite.image, offset_rect)

    # Display game state messages
    if game_state == "challenge" and current_question is not None:
        # Draw a translucent overlay for challenge mode
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Get the question details
        q = questions[current_question]
        draw_centered_text(screen, "Math Challenge!", font_large, YELLOW, 80)
        # Wrap the prompt text so it doesn't go off screen
        draw_text_wrapped(screen, q["prompt"], (50, 140), font_medium, WHITE, max_width=WIDTH-100)

        # List the options (these are short so centered text works fine)
        for i, option in enumerate(q["options"]):
            opt_text = f"{i+1}. {option}"
            draw_centered_text(screen, opt_text, font_medium, WHITE, 220 + i * 40)
        
        if message:
            draw_centered_text(screen, message, font_small, GREEN, 400)
        draw_centered_text(screen, "Press 1-4 to answer.", font_small, WHITE, 450)
    
    # Draw HUD (e.g. instructions for jump)
    if game_state == "playing":
        draw_text(screen, "Arrow keys to move, Space to jump", font_small, WHITE, (10, 10))
        draw_text(screen, "Reach red zones to answer math questions.", font_small, WHITE, (10, 30))
    
    pygame.display.update()

pygame.quit()
sys.exit()
