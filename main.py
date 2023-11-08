import pygame
import math

from src.player import Player
from src.ai_enemy import AIEnemy


class Game:
    def __init__(self) -> None:
        """Initializes game."""

        pygame.init()
        self.running = True
        self.game_over = False
        self.fps = 60
        self.fps_clock = pygame.time.Clock()
        self.menu = True
        self.main_menu = True
        self.screen_ratio = (16, 9)
        self.ai = False

        self._setup_screen()
        self._setup_elements()
        self._setup_audio()
        self._setup_fonts()
        self._setup_menu()

    def scale(self, val: int) -> int:
        """Scales values to screen size.

        Args:
            val (int): value to be scaled

        Returns:
            int: scaled value
        """

        if isinstance(val, (int, float)):
            return math.floor((val / 60) * self.scale_factor)
        if isinstance(val, (list, tuple)):
            return [math.floor((i / 60) * self.scale_factor) for i in val]

    def _setup_screen(self) -> None:
        """Creates pygame screen and draws background."""

        monitor_size = (
            pygame.display.Info().current_w,
            pygame.display.Info().current_h,
        )
        # monitor_size = (1000,700)

        horiz = monitor_size[0] / self.screen_ratio[0]
        vert = monitor_size[1] / self.screen_ratio[1]
        self.scale_factor = min(horiz, vert)
        self.screen_size = (
            math.floor(self.scale_factor * self.screen_ratio[0]),
            math.floor(self.scale_factor * self.screen_ratio[1]),
        )

        self.screen = pygame.display.set_mode(self.screen_size)

        # title and icon
        pygame.display.set_caption("Battle")

        self.blue_heart_sprite = pygame.image.load(
            "sprites/blue_heart.png"
        ).convert_alpha()
        self.blue_heart_sprite = pygame.transform.scale(
            self.blue_heart_sprite, self.scale((30, 30))
        )
        self.red_heart_sprite = pygame.image.load(
            "sprites/red_heart.png"
        ).convert_alpha()
        self.red_heart_sprite = pygame.transform.scale(
            self.red_heart_sprite, self.scale((30, 30))
        )
        self.stamina_sprite = pygame.image.load("sprites/stamina.png").convert_alpha()
        self.stamina_sprite = pygame.transform.scale(
            self.stamina_sprite, self.scale((60, 60))
        )

    def _setup_menu(self) -> None:
        """Creates menu variables."""

        self.menu_dict = {"main": True, "start_fight": False}
        self.pointer = 0

    def _setup_audio(self) -> None:
        """Creates audio variables."""

        self.sword_hit_sound = pygame.mixer.Sound("sprites/sounds/sword_hit.mp3")
        self.sword_hit_shield_sound = pygame.mixer.Sound(
            "sprites/sounds/sword_hit_shield.wav"
        )
        self.sword_hit_shield_sound.set_volume(0.3)

    def update_display(self) -> None:
        """Updates display."""

        pygame.display.update()
        self.fps_clock.tick(self.fps)

    def show_background(self) -> None:
        """Draws background."""

        self.screen.fill((0, 0, 0))
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            (0, self.screen_size[1] * 0.78, self.screen_size[0], self.scale(10)),
        )

    def _setup_elements(self) -> None:
        """Creates character and environment elements."""

        self.player1 = Player(self.screen, self.scale, facing_left=False)
        self.player2 = Player(self.screen, self.scale, facing_left=True)
        self._setup_ai()

    def _setup_ai(self) -> None:
        """Creates AI enemy."""

        if self.ai is True:
            self.ai_enemy = AIEnemy(
                self.player2.input_dict,
                self.player1,
                self.player2,
                ai_scheme="heuristic",
            )

    def _setup_fonts(self) -> None:
        """Creates fonts for various texts."""

        self.score_font = pygame.font.Font("freesansbold.ttf", self.scale(32))
        self.over_font = pygame.font.Font("freesansbold.ttf", self.scale(48))

    def handle_menu(self) -> None:
        """Handles menu events."""

        if self.main_menu is True:
            if self.menu_dict["main"] == True:
                self._show_main_menu()
            if self.menu_dict["start_fight"] == True:
                self._show_start_fight_menu()

    def _show_main_menu(self) -> None:
        keys = pygame.event.get(pygame.KEYDOWN)
        if len(keys) > 0:
            if (keys[0].key == self.player1.input_dict["down"]) or (
                keys[0].key == self.player2.input_dict["down"]
            ):
                if self.pointer == 0:
                    self.pointer += 1
            if (keys[0].key == self.player1.input_dict["jump"]) or (
                keys[0].key == self.player2.input_dict["jump"]
            ):
                if self.pointer == 1:
                    self.pointer -= 1
            if (
                (keys[0].key == pygame.K_SPACE)
                or (keys[0].key == self.player1.input_dict["sword"])
                or (keys[0].key == self.player2.input_dict["sword"])
            ):
                if self.pointer == 0:
                    self.ai = True
                    self._setup_ai()
                else:
                    self.ai = False

                self.menu_dict["main"] = False
                self.menu_dict["start_fight"] = True
            if keys[0].key == pygame.K_ESCAPE:
                self.running = False

        self._show_text("BOX SHADOW", font=self.over_font)
        texts = ["1 Player", "2 Player"]
        self._show_text(texts, text_y=225, pointer=self.pointer)

    def _show_start_fight_menu(self) -> None:
        self._show_text("Press SPACE to start fight", 150)

        keys = pygame.event.get(pygame.KEYDOWN)
        if len(keys) > 0:
            if keys[0].key == pygame.K_BACKSPACE:
                self.menu_dict["main"] = True
                self.menu_dict["start_fight"] = False

            if keys[0].key == pygame.K_SPACE:
                self.menu = False

            if keys[0].key == pygame.K_ESCAPE:
                self.running = False

    def _show_text(self, text, text_y=150, pointer=None, font=None) -> None:
        if not isinstance(text, list):
            text = [text]
        if font is None:
            font = self.score_font

        center_width = self.screen_size[0] / 2
        text_y = self.scale(text_y)

        for i, t in enumerate(text):
            render_text = font.render(t, True, (255, 255, 255))
            render_text_rect = render_text.get_rect(midtop=(center_width, text_y))
            self.screen.blit(render_text, render_text_rect)
            if (pointer is not None) & (i == pointer):
                self.player1.sword_rect.midright = (
                    render_text_rect.left - self.scale(2),
                    render_text_rect.centery - self.scale(4),
                )
                self.screen.blit(self.player1.sword_sprite, self.player1.sword_rect)

            text_y = render_text_rect.bottom + self.scale(1)

    def show_data(self):
        self._show_lives()
        self._show_stamina()

    def _show_lives(self):
        self.screen.blit(self.blue_heart_sprite, self.scale((15, 23)))
        self.screen.blit(self.red_heart_sprite, self.scale((925, 23)))

        y = self.scale(23)
        size = self.scale(30)

        for i in range(self.player1.life):
            x = self.scale(60) + self.scale(30) * i
            pygame.draw.rect(self.screen, (99, 155, 255), [x, y, size, size])
        for i in range(self.player2.life):
            x = self.screen_size[0] - self.scale(80) - self.scale(30) * i
            pygame.draw.rect(self.screen, (217, 87, 99), [x, y, size, size])

    def _show_stamina(self):
        y = self.scale(70)
        size = self.scale(30)

        for i in range(self.player1.stamina):
            x = self.scale(60) + self.scale(30) * i
            pygame.draw.rect(self.screen, (255, 255, 255), [x, y, size, size])
        for i in range(self.player2.stamina):
            x = self.screen_size[0] - self.scale(80) - self.scale(30) * i
            pygame.draw.rect(self.screen, (255, 255, 255), [x, y, size, size])

        self.screen.blit(self.stamina_sprite, self.scale((0, 50)))
        self.screen.blit(self.stamina_sprite, self.scale((905, 50)))

    def handle_events(self):
        """Quits game if exit is pressed."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                self.player1.ground = round(self.screen.get_height() * 0.78)
                self.player2.ground = round(self.screen.get_height() * 0.78)
                over_font_size = round(
                    min(self.screen.get_width() * 0.08, self.screen.get_height() * 0.08)
                )
                self.over_font = pygame.font.Font("freesansbold.ttf", over_font_size)

    def handle_gameover(self):
        self._check_game_over()
        self._handle_reset()

    def _check_game_over(self):
        texts = ["Press SPACE to restart", "Press BACK to return to main menu"]

        if (self.player1.life <= 0) & (self.player2.life >= 1):
            self._show_text("Player 2 wins", font=self.over_font)
            self._show_text(texts, 225)
            self.player1.rect.y = -2000
            self.player1.knockback = True
            self.game_over = True

        elif (self.player2.life <= 0) & (self.player1.life >= 1):
            self._show_text("Player 1 wins", font=self.over_font)
            self._show_text(texts, 225)
            self.player2.rect.y = -2000
            self.player2.knockback = True
            self.game_over = True

        elif (self.player2.life <= 0) & (self.player1.life <= 0):
            self._show_text("Draw", font=self.over_font)
            self._show_text(texts, 225)
            self.player1.rect.y, self.player2.rect.y = -2000, -2000
            self.player1.knockback, self.player2.knockback = True, True
            self.game_over = True

    def _handle_reset(self):
        if self.game_over is True:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.game_over = False
                max_stamina1 = self.player1.max_stamina
                max_stamina2 = self.player2.max_stamina

                self._setup_elements()
                self.player1.max_stamina, self.player1.stamina, self.player1.life = (
                    max_stamina1,
                    max_stamina1,
                    10 - max_stamina1,
                )
                self.player2.max_stamina, self.player2.stamina, self.player2.life = (
                    max_stamina2,
                    max_stamina2,
                    10 - max_stamina2,
                )

            if keys[pygame.K_BACKSPACE]:
                self.game_over = False
                self.menu = True
                self.menu_dict["main"] = True
                self.menu_dict["start_fight"] = False
                self._setup_elements()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self._player_movement(self.player1, keys)

        if self.ai is True:
            ai_input = self.ai_enemy.get_input()
            if ai_input is not None:
                keys = ai_input

        self._player_movement(self.player2, keys)

    def _player_movement(self, player, keys):
        if player.is_ready():
            # left movement
            if keys[player.input_dict["left"]]:
                if player.facing_left is False:
                    player.facing_left = True
                    player.flip_player()

                player.X_change = -player.speed
                player.check_dash("Left")

            # right movement
            if keys[player.input_dict["right"]]:
                if player.facing_left is True:
                    player.facing_left = False
                    player.flip_player()

                player.X_change = player.speed
                player.check_dash("Right")

            # jumping
            if keys[player.input_dict["jump"]]:
                player.deploy_jump()

            # downstrike
            if keys[player.input_dict["down"]]:
                player.deploy_downstrike()

            # sword
            if keys[player.input_dict["sword"]]:
                player.deploy_strike()

            # shield
            if keys[player.input_dict["shield"]]:
                player.deploy_shield()

            # stopping
            if keys[player.input_dict["right"]] and keys[player.input_dict["left"]]:
                player.X_change = 0
            if (
                not keys[player.input_dict["right"]]
                and not keys[player.input_dict["left"]]
            ):
                player.X_change = 0
                player.check_dash()

    def handle_collisions(self):
        """Handles collisions from both players and swords."""

        self._handle_sword_collisions()
        self._handle_player_collisions()
        self._handle_downstrike_collisions()

    def _handle_player_collisions(self):
        """Handles player collisions."""

        # check collision between 2 players
        collide = bool(self.player1.rect.colliderect(self.player2.rect))

        if collide is True:
            self._calc_player_collision(self.player1, self.player2)
            self._calc_player_collision(self.player2, self.player1)
        else:
            self.player1.on_top = False
            self.player2.on_top = False

    def _calc_player_collision(self, playera, playerb):
        playera.on_top = self._edge_detection(playera.rect.bottom, playerb.rect.top)

        if (playera.on_top is False) & (playerb.on_top is False):
            if playera.rect.x < playerb.rect.x:
                if playera.X_change > 0:
                    playera.X_change = 0
                if playerb.X_change < 0:
                    playerb.X_change = 0

        # if player a is above player b
        if playera.rect.y < playerb.rect.y:
            # player a can't fall, player b can't jump
            if playera.Y_change > 0:
                playera.Y_change = 0
            if playerb.Y_change < 0:
                playerb.Y_change = 0

        if playera.on_top is True:
            playera.rect.bottom = playerb.rect.top + 1
            self._edge_detection(playera.rect.bottom, playerb.rect.top)

    def _edge_detection(self, edgea, edgeb, margin=30):
        return abs(edgea - edgeb) < self.scale(margin)

    def _handle_sword_collisions(self):
        self._calc_sword_collisions(self.player1, self.player2)
        self._calc_sword_collisions(self.player2, self.player1)

    def _calc_sword_collisions(self, playera, playerb):
        # if sword is deployed
        if playera.sword_hurtbox is True:
            # check collisions
            playerb_collide = bool(playera.sword_rect.colliderect(playerb.rect))

            if playerb.shielding is True:
                shieldb_collide = bool(
                    playera.sword_rect.colliderect(playerb.shield_rect)
                )
            else:
                shieldb_collide = False

            # calc left/right for knockback
            if playera.rect.centerx < playerb.rect.centerx:
                playerb.knockback_speed = abs(playerb.knockback_speed)
                playera.knockback_speed = -abs(playerb.knockback_speed)
            else:
                playerb.knockback_speed = -abs(playerb.knockback_speed)
                playera.knockback_speed = abs(playerb.knockback_speed)

            # hit shield and not player
            if shieldb_collide and not playerb_collide:
                self.do_shield_hit(playera)

            # hit player
            if playerb_collide:
                if playera.rect.centerx < playerb.rect.centerx:
                    if (playerb.facing_left) and (playerb.shield_block):
                        self.do_shield_hit(playera)
                    else:
                        self.do_hit(playerb)

                if playera.rect.centerx > playerb.rect.centerx:
                    if (not playerb.facing_left) and (playerb.shield_block):
                        self.do_shield_hit(playera)
                    else:
                        self.do_hit(playerb)

    def _handle_downstrike_collisions(self):
        self._calc_downstrike_collisions(self.player1, self.player2)
        self._calc_downstrike_collisions(self.player2, self.player1)

    def _calc_downstrike_collisions(self, playera, playerb):
        # if sword is deployed
        if playera.downstriking is True:
            # check collisions
            playerb_collide = bool(playera.downstrike_rect.colliderect(playerb.rect))

            # hit player
            if playerb_collide:
                self.do_hit(playerb, knockback=False)

    def do_hit(self, player, knockback=True):
        if player.invinsible is False:
            player.take_hit(knockback)
            self.sword_hit_sound.play()

    def do_shield_hit(self, player):
        if player.knockback is False:
            player.stamina = 0
            self.sword_hit_shield_sound.play()
            player.deploy_knockback()


if __name__ == "__main__":
    game = Game()

    while game.running is True:
        game.show_background()

        if game.menu is True:
            game.handle_menu()

        else:
            game.handle_gameover()
            game.handle_input()

            game.player1.update()
            game.player2.update()

            game.handle_collisions()

            game.player1.movement()
            game.player2.movement()

        game.player1.show()
        game.player2.show()

        game.show_data()
        game.handle_events()
        game.update_display()
