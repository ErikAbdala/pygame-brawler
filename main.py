from fighter import Fighter
from pygame import mixer
import pygame
import json

mixer.init()
pygame.init()

# GAME WINDOW SETUP:
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
pygame.display.set_caption("Devil May Cry")
pygame.display.set_icon(pygame.image.load("assets/icons/logo.png"))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
FPS = 60

# DEFINING COLORS:
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Defining game variables:
intro_count = 4
last_count_update = pygame.time.get_ticks()
taunt_played = False  # Nova variável para controlar se o taunt já foi executado
score = [0, 0] # Player scores. [P1, P2]
round_over = False
ROUND_OVER_COOLDOWN = 2000
round_count = [0, 0]  # Track rounds won for P1 and P2
round_streak = [0, 0]  # Track streak of consecutive rounds won by a player
total_victories = [0, 0]  # Track total victories for P1 and P2

# Loading the background image:
background = pygame.image.load("assets/images/stages/miriam.jpg").convert_alpha()

# Defining the game's fonts:
count_font = pygame.font.Font("assets/fonts/DMC5Font.otf", 60)
score_font = pygame.font.Font("assets/fonts/DMC5Font.otf", 24)
name_font = pygame.font.Font("assets/fonts/DMC5Font.otf", 28)

NUM_FRAMES = 27  # ou o número de frames do seu GIF

def draw_bg():
    scaled_bg = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_health_bar(health, x, y, color, flip=False):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 554, 34))
    pygame.draw.rect(screen, BLACK, (x, y, 550, 30))
    
    if flip:
        # Desenha a barra da direita para a esquerda
        pygame.draw.rect(screen, color, (x + (550 * (1 - ratio)), y, 550 * ratio, 30))
    else:
        # Desenha a barra da esquerda para a direita (normal)
        pygame.draw.rect(screen, color, (x, y, 550 * ratio, 30))

def draw_round_balls(player_index, x, y, flip=False):
    """
    Desenha as bolinhas que representam os rounds vencidos para o jogador.
    A direção pode ser invertida (flip=True) para que cresçam da direita para a esquerda.
    """
    ball_colors = [WHITE, WHITE, WHITE]
    rounds_won = round_count[player_index]

    for i in range(3):
        if i < rounds_won:
            ball_colors[i] = YELLOW

    for i, color in enumerate(ball_colors):
        offset = i * 30
        if flip:
            # Desenha da direita para a esquerda
            pygame.draw.circle(screen, color, (x - offset, y), 10)
        else:
            # Desenha da esquerda para a direita (normal)
            pygame.draw.circle(screen, color, (x + offset, y), 10)

def load_animations(animation_data):
  
  animations = {}

  for action, data in animation_data.items():

    sheet_path = data["sheet"]
    sheet = pygame.image.load(sheet_path).convert_alpha()
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
        "interval": data.get("interval", 100),
        "rect_offset": data['rect_offset'],
        "flipped_rect_offset": data['flipped_rect_offset'],
        "rect_width": data['rect_width'],
        "rect_height": data['rect_height'],
        "flipped_offset": data['flipped_offset']
    }

  return animations

def load_character_data(character_name):
    with open(f"assets/data/{character_name}.json", "r") as file:
        return json.load(file)

# Carregando dados do personagem (por exemplo, Dante ou Vergil)
dante_data = load_character_data("dante")
vergil_data = load_character_data("vergil")

# Carregando as animações de Dante e Vergil
dante_animations = load_animations(dante_data)
vergil_animations = load_animations(vergil_data)

# Inicializando os objetos Fighter com suas animações
dante = Fighter(1, 155, 435, False, dante_animations)
vergil = Fighter(2, 1022, 435, True, vergil_animations)

def show_start_screen():

    start_font = pygame.font.Font("assets/fonts/DMC5Font.otf", 40)
    frame_paths = [f"assets/images/menu/logo_{i:02}.png" for i in range(1, NUM_FRAMES + 1)]

    # Carrega e redimensiona todos os frames
    frames = [pygame.image.load(path).convert() for path in frame_paths]
    # frames = [pygame.transform.scale(f, (SCREEN_WIDTH, SCREEN_HEIGHT)) for f in frames]

    clock = pygame.time.Clock()
    frame_index = 0
    frame_timer = pygame.time.get_ticks()
    blink_timer = pygame.time.get_ticks()
    show_text = True

    waiting = True
    while waiting:
        now = pygame.time.get_ticks()

        # Tempo para pular para o próximo frame (com delay maior no último)
        frame_duration = 40
        if frame_index == len(frames) - 1:
            frame_duration = 2500  # Último frame dura 800ms

        if now - frame_timer > frame_duration:
            frame_index = (frame_index + 1) % len(frames)
            frame_timer = now

        # Alterna visibilidade do texto a cada 500ms
        if now - blink_timer > 500:
            show_text = not show_text
            blink_timer = now

        # Desenha fundo (frame atual)
        screen.blit(frames[frame_index], (0, 0))

        # Texto piscando
        if show_text:
            start_text = start_font.render("PRESS ANY BUTTON TO START", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
            screen.blit(start_text, start_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

        clock.tick(FPS)

def show_controls_screen():
    controls_img = pygame.image.load("assets/images/controls/controls.png").convert()
    controls_img = pygame.transform.scale(controls_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    ready_p1 = False
    ready_p2 = False

    radius = 20
    outline_color = WHITE
    fill_color = GREEN

    font = pygame.font.Font("assets/fonts/DMC5Font.otf", 32)

    while not (ready_p1 and ready_p2):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                # Por exemplo: A tecla 'a' indica que o P1 está pronto, e 'l' indica que o P2 está pronto
                if event.key == pygame.K_t:
                    ready_p1 = True
                if event.key == pygame.K_KP1:
                    ready_p2 = True

        # Desenhar a imagem dos controles
        screen.blit(controls_img, (0, 0))

        # Desenhar bolinhas de confirmação
        # Bolinha do P1 (esquerda)
        # pygame.draw.circle(screen, outline_color, (135, SCREEN_HEIGHT - 70), radius + 5)  # borda
        if ready_p1:
            pygame.draw.circle(screen, outline_color, (245, SCREEN_HEIGHT - 70), radius + 5)  # borda
            pygame.draw.circle(screen, fill_color, (245, SCREEN_HEIGHT - 70), radius)  # preenchida
            draw_text("P1: READY!", font, WHITE, 285, SCREEN_HEIGHT - 90)
        else:
            pygame.draw.circle(screen, outline_color, (147, SCREEN_HEIGHT - 70), radius + 5)  # borda
            pygame.draw.circle(screen, BLACK, (147, SCREEN_HEIGHT - 70), radius)
            draw_text("P1: PRESS 'T' TO GET READY", font, WHITE, 187, SCREEN_HEIGHT - 90)

        # Bolinha do P2 (direita)
        # pygame.draw.circle(screen, outline_color, (SCREEN_WIDTH - 490, SCREEN_HEIGHT - 70), radius + 5)
        if ready_p2:
            pygame.draw.circle(screen, outline_color, (SCREEN_WIDTH - 388, SCREEN_HEIGHT - 70), radius + 5)
            pygame.draw.circle(screen, fill_color, (SCREEN_WIDTH - 388, SCREEN_HEIGHT - 70), radius)
            draw_text("P2: READY!", font, WHITE, SCREEN_WIDTH - 348, SCREEN_HEIGHT - 90)
        else:
            pygame.draw.circle(screen, outline_color, (SCREEN_WIDTH - 500, SCREEN_HEIGHT - 70), radius + 5)
            pygame.draw.circle(screen, BLACK, (SCREEN_WIDTH - 500, SCREEN_HEIGHT - 70), radius)
            draw_text("P2: PRESS 'NP 1' TO GET READY", font, WHITE, SCREEN_WIDTH - 460, SCREEN_HEIGHT - 90)

        # Texto informativo
        # draw_text("P1: Press 'A' to get ready", font, WHITE, 40, SCREEN_HEIGHT - 60)
        # draw_text("P2: Press 'L' to get ready", font, WHITE, SCREEN_WIDTH - 290, SCREEN_HEIGHT - 60)

        pygame.display.update()
        clock.tick(FPS)

#show_start_screen()
#show_controls_screen()
#pygame.time.delay(1000)
running = True
while running:

    clock.tick(FPS)

    draw_bg()

    draw_health_bar(dante.health, ((SCREEN_WIDTH // 2) - 550 - 70 // 2), 20, RED, flip=False)
    draw_health_bar(vergil.health, ((SCREEN_WIDTH // 2) + 70 // 2), 20, BLUE, flip=True)

    # Posição dos nomes dos personagens
    draw_text("DANTE", name_font, WHITE, ((SCREEN_WIDTH // 2) - 550 - 65 // 2), 17)
    draw_text("VERGIL", name_font, WHITE, ((SCREEN_WIDTH // 2) + 550 - 85 // 2), 17)

    dante_score_x = 502 if total_victories[0] < 10 else 494
    draw_text(str(total_victories[0]), score_font, GREEN, dante_score_x, 52)
    draw_text(str(total_victories[1]), score_font, GREEN, 768, 52)

    # Desenha as bolinhas de rounds vencidos
    draw_round_balls(0, 537, 68, flip=False)  # Para Dante (P1), bolinhas abaixo e à direita da barra de vida
    draw_round_balls(1, 744, 68, flip=True)  # Para Vergil (P2), bolinhas abaixo e à esquerda da barra de vida

    # #update countdown
    # if intro_count <= 0 & round_over == False:
    #     dante.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, vergil, False)
    #     vergil.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, dante, False)
    # else:
    #     x_count_spacing = 10 if intro_count == 1 else 15
    #     draw_text(str(intro_count), count_font, YELLOW, (SCREEN_WIDTH // 2) - x_count_spacing, (SCREEN_HEIGHT // 2) - 90)
    #     if (pygame.time.get_ticks() - last_count_update) >= 1000:
    #         intro_count -= 1
    #         last_count_update = pygame.time.get_ticks()

    # if intro_count <= 0 and round_over == False:
    #     dante.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, vergil, round_over)
    #     vergil.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, dante, round_over)
    # else:
    #     x_count_spacing = 10 if intro_count == 1 else 15
    #     draw_text(str(intro_count), count_font, YELLOW, (SCREEN_WIDTH // 2) - x_count_spacing, (SCREEN_HEIGHT // 2) - 90)
        
    #     # Executar taunt apenas uma vez no início da contagem
    #     if not taunt_played and intro_count == 4:
    #         dante.start_taunt()
    #         vergil.start_taunt()
    #         taunt_played = True
        
    #     if (pygame.time.get_ticks() - last_count_update) >= 1000:
    #         intro_count -= 1
    #         last_count_update = pygame.time.get_ticks()

    # Atualização do countdown - VERSÃO CORRIGIDA
    if intro_count <= 0 and round_over == False:
        dante.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, vergil, round_over)
        vergil.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, dante, round_over)
    elif not round_over:  # Só decrementa o contador se NÃO estiver em round_over
        x_count_spacing = 10 if intro_count == 1 else 15
        draw_text(str(intro_count), count_font, YELLOW, (SCREEN_WIDTH // 2) - x_count_spacing, (SCREEN_HEIGHT // 2) - 90)
        
        # Executar taunt apenas uma vez no início da contagem
        if not taunt_played and intro_count == 4:
            dante.start_taunt()
            vergil.start_taunt()
            taunt_played = True
        
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    # # CORREÇÃO: Durante round over, força os personagens para idle se não estiverem mortos
    # if round_over:
    #     if dante.alive and dante.action not in ["death"]:
    #         dante.update_action("idle")
    #     if vergil.alive and vergil.action not in ["death"]:
    #         vergil.update_action("idle")

    # CORREÇÃO: Durante round over, aplica animações apropriadas
    if round_over:
        if dante.alive and dante.action not in ["death", "victory"]:
            # Inicia animação de vitória se disponível
            if "victory" in dante.animations:
                dante.start_victory()
            else:
                # Reset completo do estado do personagem para idle
                dante.attacking = False
                dante.attack_type = None
                dante.hit = False
                dante.blocking = False
                dante.running = False
                dante.walking = False
                dante.taunting = False
                dante.update_action("idle")
                dante.frame_index = 0
        elif not dante.alive and dante.action not in ["death"]:
            # Personagem derrotado vai para death
            dante.update_action("death")
            dante.frame_index = 0
            
        if vergil.alive and vergil.action not in ["death", "victory"]:
            # Inicia animação de vitória se disponível
            if "victory" in vergil.animations:
                vergil.start_victory()
            else:
                # Reset completo do estado do personagem para idle
                vergil.attacking = False
                vergil.attack_type = None
                vergil.hit = False
                vergil.blocking = False
                vergil.running = False
                vergil.walking = False
                vergil.taunting = False
                vergil.update_action("idle")
                vergil.frame_index = 0
        elif not vergil.alive and vergil.action not in ["death"]:
            # Personagem derrotado vai para death
            vergil.update_action("death")
            vergil.frame_index = 0

    dante.update()
    vergil.update()

    dante.draw(screen)
    vergil.draw(screen)

    #check for player defeat
    if not round_over:
        if dante.alive == False:
            round_count[1] += 1
            # round_streak[1] += 1
            # round_streak[0] = 0
            round_over = True
            if round_count[1] == 3:
                total_victories[1] += 1
                round_count = [0, 0]
                # round_streak = [0, 0]
            round_over_time = pygame.time.get_ticks()
        elif vergil.alive == False:
            round_count[0] += 1
            # round_streak[0] += 1
            # round_streak[1] = 0
            round_over = True
            if round_count[0] == 3:
                total_victories[0] += 1
                round_count = [0, 0]
                # round_streak = [0, 0]
            round_over_time = pygame.time.get_ticks()
    else:
        # Display victory image
        # screen.blit(victory_img, (640, 360))
        winner = 'DANTE' if dante.alive else 'VERGIL'
        x_win_spacing = 152 if dante.alive else 160
        draw_text(f'{winner} WINS!', count_font, YELLOW, (SCREEN_WIDTH // 2) - x_win_spacing, (SCREEN_HEIGHT // 2) - 90)
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            taunt_played = False
            round_over = False
            intro_count = 4
            dante = Fighter(1, 155, 435, False, load_animations(dante_data))
            vergil = Fighter(2, 1022, 435, True, load_animations(vergil_data))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()