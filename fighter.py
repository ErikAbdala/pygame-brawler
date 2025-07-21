import pygame

class Fighter():

    def __init__(self, player, x, y, flip, animations):
        
        self.player = player
        self.flip = flip
        self.animations = animations
        self.action = "idle"
        self.frame_index = 0
        self.image = self.animations[self.action]["frames"][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(x, y, 110, 175)
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = None
        self.attack_cooldown = 0
        self.hit = False
        self.health = 100
        self.alive = True
        self.blocking = False
        self.walking = False
        self.taunting = False
        self.taunt_finished = False
        self.victory = False
        self.manual_flip = None

    def move(self, screen_width, screen_height, surface, target, round_over):

        """Handles all movement logic, gravity, jumping, input processing, collision boundaries, and attack triggering.
        
        Also determines character orientation (flip) based on enemy position or manual input.
        """

        SPEED = 5
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.walking = False
        self.attack_type = None

        key = pygame.key.get_pressed()

        if self.attacking is False and self.alive and round_over is False and not self.victory:

            if self.player == 1:

                if key[pygame.K_SPACE]:
                    self.blocking = True
                else:
                    self.blocking = False

                if self.blocking == False:

                    if key[pygame.K_a]:
                        dx = -SPEED - 4
                        self.running = True
                        self.manual_flip = True

                    if key[pygame.K_d]:
                        dx = SPEED + 4
                        self.running = True
                        self.manual_flip = False

                    if key[pygame.K_a] & key[pygame.K_s]:
                        dx = -SPEED
                        self.walking = True
                        self.manual_flip = True

                    if key[pygame.K_d] & key[pygame.K_s]:
                        dx = SPEED
                        self.walking = True
                        self.manual_flip = False

                    if key[pygame.K_w] and self.jump is False:
                        self.vel_y = -30
                        self.jump = True

                    if key[pygame.K_t]:
                        self.flip = target.rect.centerx < self.rect.centerx
                        self.manual_flip = None
                        self.attack(target, "attack1")
                        self.attack_type = 1

                    if key[pygame.K_y]:
                        self.flip = target.rect.centerx < self.rect.centerx
                        self.manual_flip = None
                        self.attack(target, "attack2")
                        self.attack_type = 2

            else:

                if key[pygame.K_KP0]:
                    self.blocking = True
                else:
                    self.blocking = False

                if self.blocking == False:

                    if key[pygame.K_LEFT]:
                        dx = -SPEED - 4
                        self.running = True
                        self.manual_flip = True

                    if key[pygame.K_RIGHT]:
                        dx = SPEED + 4
                        self.running = True
                        self.manual_flip = False

                    if key[pygame.K_LEFT] & key[pygame.K_DOWN]:
                        dx = -SPEED
                        self.walking = True
                        self.manual_flip = True

                    if key[pygame.K_RIGHT] & key[pygame.K_DOWN]:
                        dx = SPEED
                        self.walking = True
                        self.manual_flip = False

                    if key[pygame.K_UP] and self.jump is False:
                        self.vel_y = -30
                        self.jump = True

                    if key[pygame.K_KP1]:
                        self.attack(target, "attack1")
                        self.attack_type = 1

                    if key[pygame.K_KP2]:
                        self.attack(target, "attack2")
                        self.attack_type = 2

        if self.running or self.walking:
            self.flip = self.manual_flip if self.manual_flip is not None else self.flip
        else:
            self.flip = target.rect.centerx < self.rect.centerx
            self.manual_flip = None

        # APPLYING GRAVITY:
        self.vel_y += GRAVITY
        dy += self.vel_y

        # LIMITING THE SCREEN:
        if self.rect.left + dx < 0:
            dx = -self.rect.left

        if self.rect.right + dx > screen_width - 80:
            dx = screen_width - self.rect.right - 80
            
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy

    def update(self):

        """Updates the fighter's current action, animation frame, and physics (falling or attacking).
    
        Handles state changes like death, victory, taunting, blocking, and taking damage.
        """

        if self.health <= 0:

            self.health = 0
            self.alive = False
            self.forces_gravity()
            self.update_action("death")

        elif self.victory:
            self.forces_gravity()
            self.update_action("victory")

        elif self.taunting:
            self.update_action("taunt")
            
        elif self.blocking:
            self.hit = False 
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

        else:
            self.update_action("idle")

        animation_cooldown = self.animations[self.action]["interval"]
        self.image = self.animations[self.action]["frames"][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        if self.frame_index >= len(self.animations[self.action]["frames"]):

            if self.action == "death" or self.action == "block":
                self.frame_index = len(self.animations[self.action]["frames"]) - 1

            else:

                self.frame_index = 0

                if self.action in ["attack1", "attack2", "attack3"]:
                    self.attacking = False
                    self.attack_cooldown = 20

                elif self.action == "taunt":
                    self.taunting = False
                    self.taunt_finished = True

                if self.action == "hit":
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target, attack_type):

        """Performs an attack if not on cooldown and checks for collision with the opponent's hurtbox.
    
        Applies damage if the target is not blocking.
        """

        if self.attack_cooldown == 0:

            self.attacking = True
            self.attack_type = attack_type
            self.update_action(attack_type)
            attack_range = self.hurtbox

            if attack_range.colliderect(target.rect):

                if target.blocking:
                    target.hit = False 
                    target.health -= 0

                else:
                    target.health -= 20
                    target.hit = True

    def update_action(self, new_action):

        """Changes the current animation/action and updates the associated hurtbox.
    
        Hurtbox is adjusted based on the direction (flip) and action type.
        """

        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

        rect_width = self.animations[self.action]['rect_width']
        rect_height = self.animations[self.action]['rect_height']
        rect_x_offset = self.animations[self.action]['rect_offset'][0]
        rect_y_offset = self.animations[self.action]['rect_offset'][1]
        flipped_rect_x_offset = self.animations[self.action]['flipped_rect_offset'][0]
        flipped_rect_y_offset = self.animations[self.action]['flipped_rect_offset'][1]

        if self.flip == False:
            self.hurtbox = pygame.Rect(self.rect.x - rect_x_offset, self.rect.y - rect_y_offset, rect_width, rect_height)
        else:
            self.hurtbox = pygame.Rect(self.rect.x - flipped_rect_x_offset, self.rect.y - flipped_rect_y_offset, rect_width, rect_height)

    def draw(self, surface):

        """Draws the character sprite and its hurtbox on the screen.
    
        Applies horizontal flip if needed and adjusts position using offset and scale.
        """

        anim_data = self.animations[self.action]
        offset = anim_data["offset"]

        if self.flip:
            offset = anim_data["flipped_offset"]

        scale = anim_data["scale"]
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (offset[0] * scale), self.rect.y - (offset[1] * scale)))

        pygame.draw.rect(surface, (255, 0, 0), self.hurtbox, 2)

    def start_taunt(self):

        """Initiates the taunt animation if it hasn't already been performed."""

        if not self.taunting and not self.taunt_finished:
            self.taunting = True
            self.update_action("taunt")

    def start_victory(self):

        """Triggers the victory animation and resets the fighter's combat state."""

        if "victory" in self.animations:
            self.victory = True
            self.attacking = False
            self.attack_type = None
            self.hit = False
            self.blocking = False
            self.running = False
            self.walking = False
            self.taunting = False
            self.update_action("victory")
            self.frame_index = 0

    def forces_gravity(self):

        """Applies gravity to force the fighter down until they reach the floor.

        Ensures the character falls naturally when airborne and snaps to the ground when reaching the screen bottom.
        """

        screen_bottom = 720 - 110
        if self.rect.bottom < screen_bottom:
            self.vel_y += 2
            self.rect.y += self.vel_y
        else:
            self.rect.bottom = screen_bottom
            self.vel_y = 0