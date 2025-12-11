"""Model classes for the Missionaries and Cannibals game."""

import math
import pygame
from constants import (
    BoatPosition, LEFT_BANK_X, RIGHT_BANK_X, BOAT_LEFT_X, BOAT_RIGHT_X,
    BOAT_Y, CHARACTER_Y_TOP, CHARACTER_Y_BOTTOM, CHARACTER_SIZE,
    BOAT_WIDTH, BOAT_HEIGHT, BOAT_SPEED, WOBBLE_SPEED, WOBBLE_AMOUNT,
    EATING_DURATION
)


class GameState:
    """Represents the current state of the puzzle."""

    def __init__(self, missionaries_left, cannibals_left, boat):
        """Initialize game state with counts and boat position."""
        self.missionaries_left = missionaries_left
        self.cannibals_left = cannibals_left
        self.boat = boat

    def missionaries_right(self):
        """Return number of missionaries on right bank."""
        return 3 - self.missionaries_left

    def cannibals_right(self):
        """Return number of cannibals on right bank."""
        return 3 - self.cannibals_left

    def is_valid(self):
        """Check if current state is valid (no one gets eaten)."""
        if not (0 <= self.missionaries_left <= 3):
            return False
        if not (0 <= self.cannibals_left <= 3):
            return False
        m_left = self.missionaries_left
        c_left = self.cannibals_left
        if m_left > 0 and c_left > m_left:
            return False
        m_right = self.missionaries_right
        c_right = self.cannibals_right
        if m_right > 0 and c_right > m_right:
            return False
        return True

    def is_goal(self):
        """Check if current state is the winning goal state."""
        return (self.missionaries_left == 0 and
                self.cannibals_left == 0 and
                self.boat == BoatPosition.RIGHT)


def build_state_graph():
    """Build complete state graph for the puzzle."""
    graph = {}
    possible_moves = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

    for m_left in range(4):
        for c_left in range(4):
            for boat in BoatPosition:
                state = GameState(m_left, c_left, boat)
                if not state.is_valid():
                    continue

                transitions = []
                for m_move, c_move in possible_moves:
                    if boat == BoatPosition.LEFT:
                        new_m = m_left - m_move
                        new_c = c_left - c_move
                        new_boat = BoatPosition.RIGHT
                        if m_move > m_left or c_move > c_left:
                            continue
                    else:
                        new_m = m_left + m_move
                        new_c = c_left + c_move
                        new_boat = BoatPosition.LEFT
                        m_right = 3 - m_left
                        c_right = 3 - c_left
                        if m_move > m_right or c_move > c_right:
                            continue

                    new_state = GameState(new_m, new_c, new_boat)
                    if new_state.is_valid():
                        transitions.append(((m_move, c_move), new_state))

                graph[state] = transitions

    return graph


class Character:
    """Represents a missionary or cannibal with sprite."""

    def __init__(self, char_type, index, side, image):
        """Initialize character with type, index, side and image."""
        self.char_type = char_type
        self.index = index
        self.side = side
        self.selected = False
        self.in_boat = False
        self.image = image
        self.wobble_offset = index * 2.0
        self.visible = True
        self.being_eaten = False
        self.eat_timer = 0.0
        self.eat_scale = 1.0
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.update_position()
        self.angle = 0.0
        self.is_moving = False

    def update_position(self):
        """Update target position based on current state."""
        if self.in_boat:
            return

        base_x = LEFT_BANK_X if self.side == 'left' else RIGHT_BANK_X

        if self.char_type == 'missionary':
            self.target_y = CHARACTER_Y_TOP
        else:
            self.target_y = CHARACTER_Y_BOTTOM

        offset = (self.index - 1) * 70
        self.target_x = base_x + offset

    def update(self, dt):
        """Update character animation and position."""
        if self.being_eaten:
            self.eat_timer += dt
            self.eat_scale = max(0, 1.0 - (self.eat_timer / EATING_DURATION))
            self.angle += 15
            if self.eat_timer >= EATING_DURATION:
                self.visible = False
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 2:
            self.is_moving = True
            speed = 5.0
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed
            self.wobble_offset += WOBBLE_SPEED
            self.angle = math.sin(self.wobble_offset * 10) * WOBBLE_AMOUNT
        else:
            self.is_moving = False
            self.x = self.target_x
            self.y = self.target_y
            time_val = pygame.time.get_ticks() * 0.002
            self.angle = math.sin(self.wobble_offset + time_val) * 2
            self.wobble_offset += 0.01

    def contains_point(self, pos):
        """Check if a point is within this character's clickable area."""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return abs(dx) < CHARACTER_SIZE // 2 and abs(dy) < CHARACTER_SIZE // 2


class Boat:
    """Represents the boat that carries characters across the river."""

    def __init__(self, image):
        """Initialize boat with image sprite."""
        self.x = float(BOAT_LEFT_X)
        self.y = float(BOAT_Y)
        self.target_x = float(BOAT_LEFT_X)
        self.is_moving = False
        self.passengers = []
        self.wave_offset = 0.0
        self.image = image
        self.angle = 0.0

    def move_to(self, position):
        """Set target position to move the boat."""
        self.target_x = BOAT_LEFT_X if position == BoatPosition.LEFT else BOAT_RIGHT_X
        self.is_moving = True

    def update(self, dt):
        """Update boat position and passenger positions."""
        dx = self.target_x - self.x

        if abs(dx) > 2:
            self.x += math.copysign(BOAT_SPEED, dx)
            self.is_moving = True
        else:
            self.x = self.target_x
            self.is_moving = False

        self.wave_offset += 0.05
        self.y = BOAT_Y + math.sin(self.wave_offset) * 3
        self.angle = math.sin(self.wave_offset * 0.8) * 3

        for i, passenger in enumerate(self.passengers):
            if len(self.passengers) == 1:
                offset = 0
            else:
                offset = -30 if i == 0 else 30
            passenger.target_x = self.x + offset
            passenger.target_y = self.y - 45

    def contains_point(self, pos):
        """Check if a point is within the boat's clickable area."""
        return (self.x - BOAT_WIDTH // 2 <= pos[0] <= self.x + BOAT_WIDTH // 2 and
                self.y - BOAT_HEIGHT // 2 <= pos[1] <= self.y + BOAT_HEIGHT // 2)
