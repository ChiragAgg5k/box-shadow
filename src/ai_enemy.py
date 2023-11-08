import random


class AIEnemy:
    def __init__(self, input_dict, playera, playerb, ai_scheme="heuristic"):
        self.ai_scheme = ai_scheme
        self.playera = playera
        self.playerb = playerb

        self.input_dict = input_dict
        self.ai_key_dict = {
            self.input_dict["jump"]: 0,
            self.input_dict["left"]: 0,
            self.input_dict["right"]: 0,
            self.input_dict["down"]: 0,
            self.input_dict["sword"]: 0,
            self.input_dict["shield"]: 0,
        }

        if ai_scheme != "random_input":
            self.walk_left = [self.input_dict["left"]] * 10
            self.walk_right = [self.input_dict["right"]] * 10
            self.sword = [self.input_dict["sword"]]
            self.shield = [self.input_dict["shield"]]
            self.dash_left = (
                [self.input_dict["left"]] * 3
                + [None] * 3
                + [self.input_dict["left"]] * 5
                + self.sword
            )
            self.dash_right = (
                [self.input_dict["right"]] * 3
                + [None] * 3
                + [self.input_dict["right"]] * 5
                + self.sword
            )
            self.jump_left = [
                [self.input_dict["jump"], self.input_dict["left"]]
            ] + self.walk_left
            self.jump_right = [
                [self.input_dict["jump"], self.input_dict["right"]]
            ] + self.walk_right
            self.jump_left_downstrike = (
                self.jump_left + self.walk_left * 2 + [self.input_dict["down"]]
            )
            self.jump_right_downstrike = (
                self.jump_right + self.walk_right * 2 + [self.input_dict["down"]]
            )
            self.down_strike = [self.input_dict["jump"]] * 5 + [self.input_dict["down"]]

            self.sequence_index = 0
            self.sequence_list = [
                self.walk_left,
                self.walk_right,
                self.dash_left,
                self.dash_right,
                self.sword,
                self.sword,
                self.sword,
                self.shield,
                self.shield,
                self.shield,
                self.jump_left_downstrike,
                self.jump_right_downstrike,
                self.down_strike,
            ]
            self.sequence = self.walk_left
            self.sequence_break = False
            self.avoiding = False

    def get_input(self):
        if self.ai_scheme == "random_input":
            return self._random_input()
        elif self.ai_scheme == "random_sequence":
            return self._random_sequence()
        elif self.ai_scheme == "heuristic":
            return self._heuristics()

    def _random_input(self):
        ai_key_dict_copy = self.ai_key_dict.copy()
        ai_key_dict_copy[random.sample(self.ai_key_dict.keys(), 1)[0]] = 1

        return ai_key_dict_copy

    def _random_sequence(self):
        if self.sequence_index == len(self.sequence) - 1:
            self.sequence = random.sample(self.sequence_list, 1)[0]
            self.sequence_index = 0
        else:
            self.sequence_index += 1

        input = self.sequence[self.sequence_index]

        ai_key_dict_copy = self.ai_key_dict.copy()
        ai_key_dict_copy[input] = 1

        return ai_key_dict_copy

    def _heuristics(self):
        self._check_sequence_break()

        if self.sequence_index >= len(self.sequence) - 1:
            self.sequence = self._choose_heuristic()
            if self.sequence_break is True:
                self.sequence_break = False
            self.sequence_index = 0
        else:
            self.sequence_index += 1

        input = self.sequence[self.sequence_index]
        ai_key_dict_copy = self.ai_key_dict.copy()

        if not isinstance(input, list):
            input = [input]
        for i in input:
            ai_key_dict_copy[i] = 1

        return ai_key_dict_copy

    def _choose_heuristic(self):
        """Choose the heuristic to follow based on the current game state

        Returns:
            list: list of inputs to be executed
        """

        sequence = [None]

        # no stamina, avoid
        if not self._has_stamina():
            sequence = self._avoid()

        # is over or under
        elif self._is_on_top():
            possible_sequences = [self.down_strike, self.walk_right, self.walk_left]
            sequence = random.sample(possible_sequences, 1)[0]

        elif self._is_under():
            if self._has_stamina(3):
                possible_sequences = [
                    self.dash_left,
                    self.dash_right,
                    self.walk_left * 2,
                    self.walk_right * 2,
                ]
                sequence = random.sample(possible_sequences, 1)[0]
            else:
                possible_sequences = [self.walk_left * 2, self.walk_right * 2]
                sequence = random.sample(possible_sequences, 1)[0]
        # far away
        elif self._is_far():
            if self._is_left():
                sequence = self.walk_left
            else:
                sequence = self.walk_right
        # close
        elif self._is_close():
            if self.playera.striking:
                sequence = self.shield
            else:
                if self._is_left():
                    sequence = [[self.input_dict["left"], self.input_dict["sword"]]]
                else:
                    sequence = [[self.input_dict["right"], self.input_dict["sword"]]]
            if self.playerb.striking:
                if self._is_left:
                    sequence = self.walk_left
                if self._is_right:
                    sequence = self.walk_right

        # medium distance
        elif self._is_left() & self._is_medium():
            if self._has_stamina(2):
                possible_sequences = [
                    self.jump_left_downstrike,
                    self.dash_left,
                    self.walk_left,
                ]
                sequence = random.sample(possible_sequences, 1)[0]
            else:
                possible_sequences = [self.jump_left_downstrike, self.walk_left]
                sequence = random.sample(possible_sequences, 1)[0]
        elif self._is_right() & self._is_medium():
            if self._has_stamina(2):
                possible_sequences = [
                    self.jump_right_downstrike,
                    self.dash_right,
                    self.walk_right,
                ]
                sequence = random.sample(possible_sequences, 1)[0]
            else:
                possible_sequences = [self.jump_right_downstrike, self.walk_right]
                sequence = random.sample(possible_sequences, 1)[0]
        # enemy in stun
        elif self._is_left() & (self.playera.land_downstrike_stun is True):
            if self._is_far() & self._has_stamina(3):
                possible_sequences = [self.walk_left, self.dash_left]
                sequence = random.sample(possible_sequences, 1)[0]
            if (self._is_medium() or self._is_close()) & self._has_stamina(1):
                sequence = self.walk_left + self.sword
        elif self._is_right() & (self.playera.land_downstrike_stun is True):
            if self._is_far() & self._has_stamina(3):
                possible_sequences = [self.walk_right, self.dash_right]
                sequence = random.sample(possible_sequences, 1)[0]
            if (self._is_medium() or self._is_close()) & self._has_stamina(1):
                sequence = self.walk_right + self.sword

        return sequence

    def _check_sequence_break(self):
        if self.sequence_break is False:
            if self._is_close() & self._has_stamina() & self.playera.striking:
                self._do_sequence_break(self.shield)

    def _do_sequence_break(self, sequence):
        self.sequence_index = 0
        self.sequence_break = True
        self.sequence = sequence

    def _avoid(self):
        self.sequence_index = 0
        self.sequence_break = True
        self.avoiding = True
        if self.playerb.stamina >= 2:
            self.avoiding = False

        if self._is_left():
            if self._near_right_edge():
                possible_sequences = [self.walk_left * 3, self.jump_left]
                sequence = random.sample(possible_sequences, 1)[0]
                return sequence
            else:
                self.walk_left
        if self._is_right():
            if self._near_left_edge():
                possible_sequences = [self.walk_right * 3, self.jump_right]
                sequence = random.sample(possible_sequences, 1)[0]
                return sequence
            else:
                self.walk_right
        return [None]

    def _is_left(self):
        return self.playera.rect.centerx < self.playerb.rect.centerx

    def _is_right(self):
        return self.playera.rect.centerx > self.playerb.rect.centerx

    def _is_far(self, distance=160):
        return abs(
            self.playera.rect.centerx - self.playerb.rect.centerx
        ) > self.playera.scale(distance)

    def _is_medium(self, low_distance=100, high_distance=160):
        return (not self._is_far(high_distance)) & (not self._is_close(low_distance))

    def _is_close(self, distance=100):
        return abs(
            self.playera.rect.centerx - self.playerb.rect.centerx
        ) < self.playera.scale(distance)

    def _is_on_top(self):
        return (self.playerb.rect.centery < self.playera.rect.centery) & self._is_close(
            20
        )

    def _is_under(self):
        return (self.playerb.rect.centery > self.playera.rect.centery) & self._is_close(
            50
        )

    def _near_right_edge(self):
        return abs(
            self.playerb.rect.x - self.playerb.screen.get_width()
        ) < self.playera.scale(100)

    def _near_left_edge(self):
        return abs(self.playerb.rect.x - 0) < self.playera.scale(100)

    def _has_stamina(self, min=1):
        return self.playerb.stamina >= min
