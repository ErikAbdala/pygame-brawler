from fighter import Fighter
from pygame import mixer
import pygame

mixer.init()
pygame.init()

# Game window setup:
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
pygame.display.set_caption("Devil May Cry")
pygame.display.set_icon(pygame.image.load("assets/icons/logo.png"))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# Defining colors:
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

#define game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]#player scores. [P1, P2]
round_over = False
ROUND_OVER_COOLDOWN = 2000
round_count = [0, 0]  # Track rounds won for P1 and P2
round_streak = [0, 0]  # Track streak of consecutive rounds won by a player
total_victories = [0, 0]  # Track total victories for P1 and P2

# Loading the background image:
background = pygame.image.load("assets/background/background.jpg").convert_alpha()

#load vicory image
victory_img = pygame.image.load("assets/icons/victory.png").convert_alpha()

#define font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

def draw_bg():
    scaled_bg = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 554, 34))
    pygame.draw.rect(screen, RED, (x, y, 550, 30))
    pygame.draw.rect(screen, BLUE, (x, y, 550 * ratio, 30))

def draw_round_balls(player_index, x, y):
    """
    Desenha as bolinhas que representam os rounds vencidos para o jogador.
    A cor das bolinhas muda conforme os rounds são vencidos.
    """
    # Definir as cores para as bolinhas
    ball_colors = [WHITE, WHITE, WHITE]  # Inicialmente todas brancas
    
    # Verifica o número de rounds vencidos pelo jogador
    rounds_won = round_count[player_index]
    
    # Se o jogador venceu 1 round, muda a primeira bolinha para verde
    if rounds_won > 0:
        ball_colors[0] = YELLOW
    # Se o jogador venceu 2 rounds, muda a segunda bolinha para verde
    if rounds_won > 1:
        ball_colors[1] = YELLOW
    # Se o jogador venceu 3 rounds, muda a terceira bolinha para verde
    if rounds_won > 2:
        ball_colors[2] = YELLOW
    
    # Desenha as bolinhas
    for i, color in enumerate(ball_colors):
        pygame.draw.circle(screen, color, (x + i * 30, y), 10)  # A distância entre as bolinhas é 30 pixels

def load_animations(animation_data):
  
  animations = {}

  for action, data in animation_data.items():

    sheet = data["sheet"]
    frame_width = data["frame_width"]
    frame_height = data["frame_height"]
    scale = data["scale"]
    num_frames = data["frames"]

    frames = []

    for i in range(num_frames):

        frame = sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
        scaled_frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
        frames.append(scaled_frame)

    animations[action] = {
        "frames": frames,
        "offset": data["offset"],
        "scale": scale,
        "speed": data.get("speed", 100) 
    }

  return animations

# Carregando as sheets do Vergil:
dante_data = {
    "idle": {
        "sheet": pygame.image.load("assets/sprites/dante/idle-sheet.png").convert_alpha(),
        "frame_width": 57, "frame_height": 104,
        "scale": 1.8, "offset": [0, 0],
        "frames": 6, "speed": 250
    },
    "walk": {
        "sheet": pygame.image.load("assets/sprites/dante/walking-sheet.png").convert_alpha(),
        "frame_width": 69, "frame_height": 102,
        "scale": 1.8, "offset": [0, 0],
        "frames": 8, "speed": 125
    },
    # "jump": {
    #     "sheet": pygame.image.load("assets/sprites/dante/walking-sheet.png").convert_alpha(),
    #     "frame_width": 80, "frame_height": 124,
    #     "scale": 1.6, "offset": [15, 0],
    #     "frames": 16, "speed": 250
    # },
    "hit": {
        "sheet": pygame.image.load("assets/sprites/dante/idle-sheet.png").convert_alpha(),
        "frame_width": 57, "frame_height": 104,
        "scale": 1.8, "offset": [0, 0],
        "frames": 6, "speed": 250
    },
    # "death": {
    #     "sheet": pygame.image.load("assets/sprites/vergil/death.png").convert_alpha(),
    #     "frame_width": 111, "frame_height": 85,
    #     "scale": 1.7, "offset": [10, 0],
    #     "frames": 2, "speed": 500
    # },
}

# Carregando as sheets do Vergil:
vergil_data = {
    "alt-idle": {
        "sheet": pygame.image.load("assets/sprites/vergil/alt-idle-sheet.png").convert_alpha(),
        "frame_width": 147, "frame_height": 185,
        "scale": 1, "offset": [0, -5],
        "frames": 6, "speed": 250
    },
    "taunt": {
        "sheet": pygame.image.load("assets/sprites/vergil/taunt-sheet.png").convert_alpha(),
        "frame_width": 86, "frame_height": 113,
        "scale": 1.75, "offset": [0, 4],
        "frames": 8, "speed": 175
    },
    "idle": {
        "sheet": pygame.image.load("assets/sprites/vergil/idle-sheet.png").convert_alpha(),
        "frame_width": 84, "frame_height": 110,
        "scale": 1.7, "offset": [10, 0],
        "frames": 6, "speed": 250
    },
    "hit": {
        "sheet": pygame.image.load("assets/sprites/vergil/hit-sheet.png").convert_alpha(),
        "frame_width": 90, "frame_height": 106,
        "scale": 1.8, "offset": [0, 0],
        "frames": 2, "speed": 250
    },
    "death": {
        "sheet": pygame.image.load("assets/sprites/vergil/death-sheet.png").convert_alpha(),
        "frame_width": 111, "frame_height": 85,
        "scale": 1.7, "offset": [60, -41],
        "frames": 2, "speed": 500
    },
    # "victory": {
    #     "sheet": pygame.image.load("assets/sprites/vergil/victory-sheet.png").convert_alpha(),
    #     "frame_width": 75, "frame_height": 103,
    #     "scale": 1.7, "offset": [10, 0],
    #     "frames": 1, "speed": 500
    # },
    "walk": {
        "sheet": pygame.image.load("assets/sprites/vergil/walk-sheet.png").convert_alpha(),
        "frame_width": 93, "frame_height": 106,
        "scale": 1.7, "offset": [10, 0],
        "frames": 8, "speed": 125
    },
    "run": {
        "sheet": pygame.image.load("assets/sprites/vergil/run-sheet.png").convert_alpha(),
        "frame_width": 229, "frame_height": 166,
        "scale": 1.1, "offset": [50, 0],
        "frames": 12, "speed": 75
    },
    "jump": {
        "sheet": pygame.image.load("assets/sprites/vergil/jump-sheet.png").convert_alpha(),
        "frame_width": 127, "frame_height": 126,
        "scale": 1.7, "offset": [0, 0],
        "frames": 4, "speed": 150
    },
    "block": {
        "sheet": pygame.image.load("assets/sprites/vergil/block-sheet.png").convert_alpha(),
        "frame_width": 114, "frame_height": 113,
        "scale": 1.7, "offset": [50, 0],
        "frames": 2, "speed": 80
    },
    "attack1": {
        "sheet": pygame.image.load("assets/sprites/vergil/attack1-sheet.png").convert_alpha(),
        "frame_width": 176, "frame_height": 145,
        "scale": 1.7, "offset": [70, 30],
        "frames": 28, "speed": 30
    },
    "attack2": {
        "sheet": pygame.image.load("assets/sprites/vergil/attack2-sheet.png").convert_alpha(),
        "frame_width": 361, "frame_height": 170,
        "scale": 1.7, "offset": [140, 25],
        "frames": 26, "speed": 30
    },
    "attack3": {
        "sheet": pygame.image.load("assets/sprites/vergil/attack3-sheet.png").convert_alpha(),
        "frame_width": 360, "frame_height": 130,
        "scale": 1.7, "offset": [210, 10],
        "frames": 38, "speed": 20
    }
}

dante = Fighter(1, 155, 435, False, load_animations(vergil_data))
vergil = Fighter(2, 1022, 435, True, load_animations(vergil_data))

running = True
while running:

    clock.tick(FPS)

    draw_bg()

    draw_health_bar(dante.health, ((SCREEN_WIDTH // 2) - 550 - 70 // 2), 20)
    draw_health_bar(vergil.health, ((SCREEN_WIDTH // 2) + 70 // 2), 20)

    dante_score_x = 500 if total_victories[0] < 10 else 490
    draw_text(str(total_victories[0]), score_font, GREEN, dante_score_x, 49)
    draw_text(str(total_victories[1]), score_font, GREEN, 768, 49)

    # Desenha as bolinhas de rounds vencidos
    draw_round_balls(0, 537, 68)  # Para Dante (P1), bolinhas abaixo e à direita da barra de vida
    draw_round_balls(1, 683, 68)  # Para Vergil (P2), bolinhas abaixo e à esquerda da barra de vida

    #update countdown
    if intro_count <= 0 & round_over == False:
        #move fighters
        dante.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, vergil, False)
        vergil.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, dante, False)
    else:
        #display count timer
        # draw_text(str(intro_count), count_font, YELLOW, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
        # Desenha o contador de intro centralizado
        draw_text(str(intro_count), count_font, YELLOW, (SCREEN_WIDTH // 2) - 13, (SCREEN_HEIGHT // 2) - 80)
        #update count timer
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    # dante.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, vergil, False)
    # vergil.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, dante, False)

    # pygame.draw.rect(screen, (255, 0, 0), dante.rect)
    # pygame.draw.rect(screen, (0, 0, 255), vergil.rect)

    dante.update()
    vergil.update()

    dante.draw(screen)
    vergil.draw(screen)

    #check for player defeat
    if not round_over:
        if dante.alive == False:
            round_count[1] += 1
            round_streak[1] += 1
            round_streak[0] = 0
            round_over = True
            if round_count[1] == 3:
                total_victories[1] += 1
                round_count = [0, 0]
                round_streak = [0, 0]
            round_over_time = pygame.time.get_ticks()
        elif vergil.alive == False:
            round_count[0] += 1
            round_streak[0] += 1
            round_streak[1] = 0
            round_over = True
            if round_count[0] == 3:
                total_victories[0] += 1
                round_count = [0, 0]
                round_streak = [0, 0]
            round_over_time = pygame.time.get_ticks()
    else:
        # Display victory image
        # screen.blit(victory_img, (640, 360))
        winner = 'Dante' if dante.alive else 'Vergil'
        draw_text(f'{winner} wins!', count_font, YELLOW, (SCREEN_WIDTH // 2) - 200, (SCREEN_HEIGHT // 2) - 80)
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            dante = Fighter(1, 155, 435, False, load_animations(vergil_data))
            vergil = Fighter(2, 1022, 435, True, load_animations(vergil_data))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()