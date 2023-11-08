import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, screen, scale, fps=120, facing_left=False):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        self.screen = screen
        self.scale = scale
        self.fps = fps
        self.ground = round(self.screen.get_height() * 0.78)

        # sprites
        self.sprite = pygame.image.load("sprites/blue_player.png").convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, self.scale((50, 50)))
        self.rect = self.sprite.get_rect()

        self.sword_sprite = pygame.image.load("sprites/sword.png").convert_alpha()
        self.sword_sprite = pygame.transform.scale(
            self.sword_sprite, self.scale((75, 30))
        )
        self.sword_rect = self.sword_sprite.get_rect()

        self.downstrike_sprite = pygame.transform.rotate(self.sword_sprite, -90)
        self.downstrike_rect = self.downstrike_sprite.get_rect()

        self.shield_sprite = pygame.image.load("sprites/shield.png").convert_alpha()
        self.shield_sprite = pygame.transform.scale(
            self.shield_sprite, self.scale((5, 50))
        )
        self.shield_rect = self.shield_sprite.get_rect()

        # positioning
        self.rect.left = self.scale(100)
        self.rect.bottom = self.ground
        self.X_change = 0
        self.Y_change = 0
        self.speed = self.scale(8)

        # jumping
        self.jumping = False
        self.jump_speed = self.scale(
            [0, 0, -20, -50, -50, -30, -15, -5, -5, -2, -2, 0, 0, 0, 0]
        )
        self.jump_fps_time = len(self.jump_speed)
        self.jump_counter = self.jump_fps_time

        # falling
        self.falling = False
        self.fall_ticker = 0
        self.initial_fall_speed = self.scale(3)
        self.on_top = False

        # dashing
        self.most_recent_press = False
        self.press_state = 0
        self.press_time = 0.1
        self.press_timer = 0
        self.dashing = False
        self.dash_mod = -1
        self.dash_speed = self.scale([0, -30, -30, -30, -30, -30, -30])
        self.dash_fps_time = len(self.dash_speed)
        self.dash_counter = self.dash_fps_time

        # knockback
        self.knockback = False
        self.knockback_time = 0.125
        self.knockback_counter = self.knockback_time * self.fps
        self.knockback_speed = self.scale(15)

        # striking
        self.sword_hurtbox = False
        self.striking = False

        self.sword_time = 0.2
        self.sword_fps_time = self.sword_time * self.fps
        self.sword_come_out_time = self.sword_fps_time - 0.02 * self.fps
        self.sword_come_in_time = 0.08 * self.fps

        self.sword_offsetx = self.scale(50)
        self.sword_offsety = self.scale(-10)
        self.sword_rect.x = self.rect.x + self.sword_offsetx
        self.sword_rect.y = self.rect.y - self.sword_offsety

        # downstrike
        self.downstriking = False
        self.downstrike_offsetx = self.scale(10)
        self.downstrike_offsety = self.scale(-30)
        self.downstrike_rect.x = self.rect.x + self.downstrike_offsetx
        self.downstrike_rect.y = self.rect.y - self.downstrike_offsety
        self.land_downstrike_stun_time_long = 30
        self.land_downstrike_stun_time_short = 5
        self.land_downstrike_stun = False

        # shield
        self.shield_offsetx = self.scale(50)
        self.shield_offsety = 0
        self.shield_rect.x = self.rect.x + self.shield_offsetx
        self.shield_rect.y = self.rect.y - self.shield_offsety
        self.shielding = False
        self.shield_block = False
        self.shield_time = 0.24
        self.shield_fps_time = self.shield_time * self.fps

        # stamina
        self.max_stamina = 5
        self.stamina = 5
        self.stamina_reload_time = 0.4
        self.stamina_reload_counter = self.stamina_reload_time * self.fps

        # other attributes
        self.life = 5
        self.invinsible = False
        self.i_frames = 60
        self.i_frames_invinsible = True

        # sounds
        self.shield_sound = pygame.mixer.Sound("sprites/sounds/shield.mp3")
        self.sword_swoosh_sound = pygame.mixer.Sound("sprites/sounds/sword_swoosh.wav")
        self.sword_hit_ground_sound = pygame.mixer.Sound(
            "sprites/sounds/sword_hit_ground.wav"
        )
        self.jump_sound = pygame.mixer.Sound("sprites/sounds/jump.mp3")
        self.land_sound = pygame.mixer.Sound("sprites/sounds/land.mp3")
        self.dash_sound = pygame.mixer.Sound("sprites/sounds/dash.mp3")

        # input keys
        self.input_dict = {
            "jump": pygame.K_w,
            "left": pygame.K_a,
            "right": pygame.K_d,
            "down": pygame.K_s,
            "sword": pygame.K_f,
            "shield": pygame.K_g,
        }

        self.facing_left = facing_left
        if self.facing_left is True:
            self.sprite = pygame.image.load("sprites/red_player.png").convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, self.scale((50, 50)))
            self.flip_player()
            self.rect.right = self.screen.get_width() - self.scale(100)
            self.input_dict = {
                "jump": pygame.K_UP,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "down": pygame.K_DOWN,
                "sword": pygame.K_k,
                "shield": pygame.K_l,
            }

    def show(self):
        """Show character sprite."""

        self.screen.blit(self.sprite, (self.rect.x, self.rect.y))

    def update(self):
        """Handle events that must take place every frame."""

        self.continue_knockback()
        self.continue_dash()
        self.continue_jump()
        self.check_fall()
        self.continue_fall()
        self.stamina_update()
        self.continue_strike()
        self.continue_downstrike()
        self.continue_land_downstrike()
        self.continue_shield()
        self.continue_iframes()
        self.iterate_dash_timer()

    def movement(self):
        """Handle sprite movements."""

        self.rect.move_ip(self.X_change, self.Y_change)

        if self.rect.x <= 0:
            self.rect.x = 0
        elif self.rect.right >= self.screen.get_width():
            self.rect.right = self.screen.get_width()

        if self.rect.bottom > self.ground:
            self.rect.bottom = self.ground

    def flip_player(self):
        self.sprite = pygame.transform.flip(self.sprite, True, False)
        self.sword_sprite = pygame.transform.flip(self.sword_sprite, True, False)
        self.shield_sprite = pygame.transform.flip(self.shield_sprite, True, False)
        self.sword_offsetx = (self.sword_offsetx + self.scale(25)) * -1
        self.shield_offsetx = (self.shield_offsetx - self.scale(45)) * -1
        self.dash_mod *= -1

    def check_fall(self):
        if (
            (self.rect.bottom < self.ground)
            & (self.jumping is False)
            & (self.on_top is False)
        ):
            self.deploy_fall()

    def deploy_fall(self):
        if self.falling is False:
            self.falling = True
            self.fall_ticker = 1

    def continue_fall(self):
        if (self.rect.bottom == self.ground) or (self.on_top is True):
            self.falling = False
            if self.Y_change >= 0:
                self.Y_change = 0

        if self.falling is True:
            if self.fall_ticker < 10:
                self.fall_ticker += 1
            self.Y_change = self.initial_fall_speed * self.fall_ticker

    def deploy_jump(self):
        if (self.jumping is False) & (self.falling is False):
            self.jumping = True
            self.jump_counter = self.jump_fps_time
            self.jump_sound.play()

    def continue_jump(self):
        if self.jumping is True:
            if self.jump_counter <= 0:
                self.jumping = False
            else:
                timer = int(self.jump_fps_time - self.jump_counter)
                self.Y_change = self.jump_speed[timer]
                self.jump_counter -= 1

    def deploy_knockback(self):
        if self.knockback is False:
            self.knockback = True
            self.X_change = self.knockback_speed
            self.knockback_counter = self.knockback_time * self.fps

    def continue_knockback(self):
        if self.knockback is True:
            self.knockback_counter -= 1

            if self.knockback_counter <= 0:
                self.knockback = False
                self.X_change = 0
            else:
                self.X_change = self.knockback_speed

    def check_dash(self, press=None):
        # if something is pressed
        if press is not None:
            # if ready
            if self.press_state == 0:
                # get ready to look for upkey
                self.press_state += 1
                # start timer
                self.press_timer = self.press_time * self.fps
                # set press id
                self.most_recent_press = press
            # if down up down within timer
            if self.press_state == 2:
                # if within timer window
                if self.press_timer > 0:
                    # if press equals first press
                    if self.most_recent_press == press:
                        self.deploy_dash()
                # always restart after stage 2
                self.press_state = 0
        # if nothing is pressed and press_state is ready for upkey
        if (press is None) & (self.press_state == 1):
            self.press_state += 1
        # if timer is up, return to state 0
        if self.press_timer == 0:
            self.press_state = 0

    def iterate_dash_timer(self):
        if self.press_timer > 0:
            self.press_timer -= 1

    def deploy_dash(self):
        if (self.is_acting() is False) & (self.stamina > 0):
            self.X_change = self.dash_speed[0] * self.dash_mod
            self.dash_counter = self.dash_fps_time
            self.dashing = True
            self.dash_sound.play()

            self.stamina -= 1
            self.stamina_reload_counter = self.stamina_reload_time * self.fps

    def continue_dash(self):
        if self.dashing is True:
            if self.dash_counter <= 0:
                self.dashing = False
                self.X_change = 0
            else:
                timer = int(self.dash_fps_time - self.dash_counter)
                self.X_change = self.dash_speed[timer] * self.dash_mod
                self.dash_counter -= 1

    def stamina_update(self):
        if (self.stamina < self.max_stamina) & (self.jumping is False):
            self.stamina_reload_counter -= 1
            if self.stamina_reload_counter <= 0:
                self.stamina += 1
                self.stamina_reload_counter = self.stamina_reload_time * self.fps

    def deploy_strike(self):
        """Deploys sword strike and starts timer."""

        if (self.is_acting() is False) & (self.stamina > 0):
            self.sword_swoosh_sound.play()
            self.striking = True
            self.striking_counter = self.sword_fps_time

            self.stamina -= 1
            self.stamina_reload_counter = self.stamina_reload_time * self.fps

    def continue_strike(self):
        """Handles sword strike including sprite, frozen frames, and timer countdown"""

        if self.striking is True:
            self.striking_counter -= 1

            if (
                self.sword_come_in_time
                < self.striking_counter
                < self.sword_come_out_time
            ):
                self.screen.blit(
                    self.sword_sprite,
                    (
                        self.rect.x + self.sword_offsetx,
                        self.rect.y - self.sword_offsety,
                    ),
                )
                self.sword_rect.x = self.rect.x + self.sword_offsetx
                self.sword_rect.y = self.rect.y - self.sword_offsety
                self.sword_hurtbox = True
            else:
                self.sword_hurtbox = False

            if self.striking_counter <= 0:
                self.striking = False

    def deploy_downstrike(self):
        if (self.is_acting() is False) & (self.stamina > 0):
            if (self.jumping) or (self.falling):
                self.X_change = 0
                self.jumping = False
                self.sword_swoosh_sound.play()
                self.downstriking = True

                self.stamina -= 1
                self.stamina_reload_counter = self.stamina_reload_time * self.fps

    def continue_downstrike(self):
        if self.downstriking is True:
            if self.falling is True:
                self.X_change = 0
                self.screen.blit(
                    self.downstrike_sprite,
                    (
                        self.rect.x + self.downstrike_offsetx,
                        self.rect.y - self.downstrike_offsety,
                    ),
                )
                self.downstrike_rect.x = self.rect.x + self.downstrike_offsetx
                self.downstrike_rect.y = self.rect.y - self.downstrike_offsety

            else:
                self.downstriking = False

                if self.on_top is True:
                    self.deploy_land_downstrike(self.land_downstrike_stun_time_short)
                else:
                    self.deploy_land_downstrike(self.land_downstrike_stun_time_long)

    def deploy_land_downstrike(self, timer):
        self.sword_hit_ground_sound.play()
        self.land_downstrike_stun = True
        self.land_downstrike_timer = timer
        self.X_change = 0

    def continue_land_downstrike(self):
        if self.land_downstrike_stun is True:
            if self.land_downstrike_timer > 0:
                self.land_downstrike_timer -= 1
            else:
                self.land_downstrike_stun = False

    def deploy_shield(self):
        if (self.is_acting() is False) & (self.stamina > 0):
            self.shield_sound.play()
            self.shielding = True
            self.shield_counter = self.shield_fps_time

            self.stamina -= 1
            self.stamina_reload_counter = self.stamina_reload_time * self.fps

            self.X_change = 0

    def continue_shield(self):
        if self.shielding is True:
            self.shield_counter -= 1
            self.screen.blit(
                self.shield_sprite,
                (self.rect.x + self.shield_offsetx, self.rect.y - self.shield_offsety),
            )
            self.shield_rect.x = self.rect.x + self.shield_offsetx
            self.shield_rect.y = self.rect.y - self.shield_offsety
            self.shield_block = True

            if self.shield_counter <= 0:
                self.shielding = False
                self.shield_block = False

    def deploy_iframes(self):
        self.invinsible = True
        self.i_frames_invinsible = True
        self.i_frames = 60

    def continue_iframes(self):
        """Handles counting down invinsibility frames."""

        if self.i_frames_invinsible is True:
            self.i_frames -= 1
            if self.i_frames <= 0:
                self.invinsible = False
                self.i_frames_invinsible = False
                self.i_frames = 60

    def take_hit(self, knockback=True):
        self.life -= 1
        if knockback is True:
            self.deploy_knockback()
        self.deploy_iframes()

    def is_ready(self):
        """Returns True if player is ready for new inputs."""
        if (self.knockback is False) & (self.land_downstrike_stun is False):
            return True
        return False

    def is_acting(self):
        if (
            (self.striking is True)
            or (self.downstriking is True)
            or (self.shielding is True)
            or (self.dashing is True)
        ):
            return True
        return False
