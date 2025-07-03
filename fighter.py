import pygame

# DEBUG = True

class Fighter():

    def __init__(self, player, x, y, flip, animations):
        
        self.player = player
        self.flip = flip
        self.animations = animations
        self.action = "idle"
        self.frame_index = 0
        self.image = self.animations[self.action]["frames"][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(x, y, 110, 175)  # hitbox pode ser ajustada se quiser
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = None
        self.attack_cooldown = 0
        # self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True

        self.blocking = False
        self.walking = False

    def move(self, screen_width, screen_height, surface, target, round_over):

        SPEED = 5
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.walking = False
        self.attack_type = None

        key = pygame.key.get_pressed()

        if self.attacking is False and self.alive and round_over is False:

            if self.player == 1:

                if key[pygame.K_SPACE]:
                    self.blocking = True
                else:
                    self.blocking = False

                if self.blocking == False:

                    if key[pygame.K_a]:
                        dx = -SPEED - 4
                        self.running = True

                    if key[pygame.K_d]:
                        dx = SPEED + 4
                        self.running = True

                    if key[pygame.K_a] & key[pygame.K_s]:
                        dx = -SPEED
                        self.walking = True

                    if key[pygame.K_d] & key[pygame.K_s]:
                        dx = SPEED
                        self.walking = True

                    if key[pygame.K_w] and self.jump is False:
                        self.vel_y = -30
                        self.jump = True

                    if key[pygame.K_r]:
                        self.attack(target, "attack1")
                        self.attack_type = 1
                        # print(1)

                    if key[pygame.K_t]:
                        self.attack(target, "attack2")
                        self.attack_type = 2
                        # print(2)

            else:

                if key[pygame.K_KP0]:
                    self.blocking = True
                else:
                    self.blocking = False

                if self.blocking == False:

                    if key[pygame.K_LEFT]:
                        dx = -SPEED - 4
                        self.running = True

                    if key[pygame.K_RIGHT]:
                        dx = SPEED + 4
                        self.running = True

                    if key[pygame.K_LEFT] & key[pygame.K_DOWN]:
                        dx = -SPEED
                        self.walking = True

                    if key[pygame.K_RIGHT] & key[pygame.K_DOWN]:
                        dx = SPEED
                        self.walking = True

                    if key[pygame.K_UP] and self.jump is False:
                        self.vel_y = -30
                        self.jump = True

                    if key[pygame.K_KP1]:
                        self.attack(target, "attack1")
                        self.attack_type = 1

                    if key[pygame.K_KP2]:
                        self.attack(target, "attack2")
                        self.attack_type = 2

                    # if key[pygame.K_KP3]:
                    #     self.attack(target, "attack3")
                    #     self.attack_type = 3

        # aplicar gravidade
        self.vel_y += GRAVITY
        dy += self.vel_y

        # limitar à tela
        if self.rect.left + dx < 0:
            dx = -self.rect.left

        if self.rect.right + dx > screen_width - 80:
            dx = screen_width - self.rect.right - 80
            
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        # # virar para o oponente
        # self.flip = target.rect.centerx < self.rect.centerx

        if self.running or self.walking:
            # Flip só se estiver indo para a esquerda
            if self.player == 1:
                self.flip = pygame.key.get_pressed()[pygame.K_a]
            else:
                self.flip = pygame.key.get_pressed()[pygame.K_LEFT]
        elif self.alive == False:
            self.flip = False
        else:
            # Quando parado, encara o oponente
            self.flip = target.rect.centerx < self.rect.centerx

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        # if (self.attacking != False):
            # print(self.attacking)
            # print('attack type:', self.attack_type)
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action("death")
        elif self.blocking:
            self.update_action("block")
        elif self.hit:
            self.update_action("hit")
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action("attack1")
            elif self.attack_type == 2:
                self.update_action("attack2")
            elif self.attack_type == 3:
                self.update_action("attack3")
        elif self.jump:
            self.update_action("jump")
        elif self.walking:
            self.update_action("walk")
        elif self.running:
            self.update_action("run")
        # elif self.blocking:
        #     self.update_action("block")
        else:
            self.update_action("idle")

        # Atualiza a imagem
        # animation_cooldown = 50
        animation_cooldown = self.animations[self.action]["speed"]
        self.image = self.animations[self.action]["frames"][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        if self.frame_index >= len(self.animations[self.action]["frames"]):
            if self.action == "death" or self.action == "block":
                self.frame_index = len(self.animations[self.action]["frames"]) - 1  # trava na última frame
            else:
                self.frame_index = 0
                if self.action in ["attack1", "attack2", "attack3"]:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == "hit":
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20


    def attack(self, target, attack_type):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_type = attack_type
            # self.attack_sound.play()
            # attack_range = pygame.Rect(
            #     self.rect.centerx - (2 * self.rect.width if not self.flip else 0),
            #     self.rect.y,
            #     2 * self.rect.width,
            #     self.rect.height
            # )
            # Definir a área de ataque como a *hurtbox* do atacante
            attack_range = self.hurtbox
            if attack_range.colliderect(target.rect):
                # target.health -= 10
                # target.hit = True
                if target.blocking:
                    target.health -= 0
                else:
                    target.health -= 20
                    target.hit = True

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
        # Ajustar a hurtbox dependendo da animação
        if self.action == "idle":
            self.hurtbox = pygame.Rect(self.rect.x, self.rect.y, 110, 175)  # Hurtbox padrão para idle
        elif self.action == "walk":
            self.hurtbox = pygame.Rect(self.rect.x, self.rect.y, 130, 175)  # Hurtbox um pouco mais larga durante a caminhada
        elif self.action == "run":
            self.hurtbox = pygame.Rect(self.rect.x, self.rect.y, 150, 175)  # Hurtbox mais larga durante a corrida
        elif self.action == "attack1":
            self.hurtbox = pygame.Rect(self.rect.x - 50, self.rect.y, 200, 175)  # Hurtbox expandida para o ataque 1
        elif self.action == "attack2":
            self.hurtbox = pygame.Rect(self.rect.x - 60, self.rect.y, 220, 175)  # Hurtbox expandida para o ataque 2
        elif self.action == "attack3":
            self.hurtbox = pygame.Rect(self.rect.x - 70, self.rect.y, 240, 175)  # Hurtbox expandida para o ataque 3
        elif self.action == "jump":
            self.hurtbox = pygame.Rect(self.rect.x, self.rect.y, 110, 175)  # Hurtbox padrão para pulo
        elif self.action == "hit":
            self.hurtbox = pygame.Rect(self.rect.x, self.rect.y, 110, 175)  # Hurtbox igual à do "idle" quando atingido
        elif self.action == "block":
            self.hurtbox = pygame.Rect(self.rect.x, self.rect.y, 110, 175)  # Hurtbox igual à do "idle" quando bloqueando

    def draw(self, surface):
        anim_data = self.animations[self.action]
        offset = anim_data["offset"]
        scale = anim_data["scale"]
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (offset[0] * scale), self.rect.y - (offset[1] * scale)))
        # surface.blit(img, (self.rect.x - (offset[0] * scale), 450))

        # Desenho da hurtbox (opcional para depuração)
        pygame.draw.rect(surface, (255, 0, 0), self.hurtbox, 2)  # Cor vermelha com borda de 2px

