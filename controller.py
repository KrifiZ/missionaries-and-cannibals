"""Controller class for the Missionaries and Cannibals game."""

import pygame
import sys
import os
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CHARACTER_SIZE,
    BOAT_WIDTH, BOAT_HEIGHT, EATING_DURATION,
    MISSIONARY_IMAGE, CANNIBAL_IMAGE, BACKGROUND_IMAGE, BOAT_IMAGE,
    BoatPosition, GameScreen
)
from model import GameState, Character, Boat, build_state_graph
from view import GameView


class GameController:
    """Main game controller handling logic and events."""

    def __init__(self):
        """Initialize pygame, load resources and set up the game."""
        pygame.init()
        pygame.display.set_caption("Missionaries and Cannibals")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        fonts = {
            'large': pygame.font.Font(None, 64),
            'medium': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }

        self.state_graph = build_state_graph()
        self.images = self.load_images()

        self.view = GameView(self.screen, fonts, self.images)

        self.reset_game()
        self.current_screen = GameScreen.WELCOME
        self.eating_timer = 0.0

    def load_images(self):
        """Load all image assets from disk."""
        script_dir = os.path.dirname(os.path.abspath(__file__))

        missionary_path = os.path.join(script_dir, MISSIONARY_IMAGE)
        cannibal_path = os.path.join(script_dir, CANNIBAL_IMAGE)
        background_path = os.path.join(script_dir, BACKGROUND_IMAGE)
        boat_path = os.path.join(script_dir, BOAT_IMAGE)

        missing = []
        if not os.path.exists(missionary_path):
            missing.append(MISSIONARY_IMAGE)
        if not os.path.exists(cannibal_path):
            missing.append(CANNIBAL_IMAGE)
        if not os.path.exists(background_path):
            missing.append(BACKGROUND_IMAGE)
        if not os.path.exists(boat_path):
            missing.append(BOAT_IMAGE)

        if missing:
            pygame.quit()
            print("ERROR: Missing image files!")
            print("Please place the following files in the game directory:")
            for f in missing:
                print(f"  - {f}")
            print(f"\nGame directory: {script_dir}")
            sys.exit(1)

        missionary_img = pygame.image.load(missionary_path).convert_alpha()
        missionary_img = pygame.transform.scale(missionary_img, (CHARACTER_SIZE, CHARACTER_SIZE))

        cannibal_img = pygame.image.load(cannibal_path).convert_alpha()
        cannibal_img = pygame.transform.scale(cannibal_img, (CHARACTER_SIZE, CHARACTER_SIZE))

        background_img = pygame.image.load(background_path).convert()
        background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        boat_img = pygame.image.load(boat_path).convert_alpha()
        boat_img = pygame.transform.scale(boat_img, (BOAT_WIDTH, BOAT_HEIGHT))

        return {
            'missionary': missionary_img,
            'cannibal': cannibal_img,
            'background': background_img,
            'boat': boat_img
        }

    def reset_game(self):
        """Reset game to initial state."""
        self.state = GameState(3, 3, BoatPosition.LEFT)
        self.move_count = 0
        self.current_screen = GameScreen.PLAYING
        self.eating_timer = 0.0

        self.missionaries = []
        self.cannibals = []

        for i in range(3):
            m = Character('missionary', i, 'left', self.images['missionary'])
            m.x = m.target_x
            m.y = m.target_y
            self.missionaries.append(m)

            c = Character('cannibal', i, 'left', self.images['cannibal'])
            c.x = c.target_x
            c.y = c.target_y
            self.cannibals.append(c)

        self.boat = Boat(self.images['boat'])
        self.selected_characters = []

    def get_all_characters(self):
        """Return list of all character objects."""
        return self.missionaries + self.cannibals

    def handle_character_click(self, char):
        """Handle clicking on a character to board or leave boat."""
        if self.boat.is_moving:
            return

        boat_side = 'left' if self.state.boat == BoatPosition.LEFT else 'right'

        if char.in_boat:
            char.selected = False
            char.in_boat = False
            char.side = boat_side
            char.update_position()
            self.boat.passengers.remove(char)
            self.selected_characters.remove(char)
        elif char.side == boat_side and len(self.boat.passengers) < 2:
            char.selected = True
            char.in_boat = True
            self.boat.passengers.append(char)
            self.selected_characters.append(char)

    def try_cross_river(self):
        """Attempt to cross the river with current passengers."""
        if self.boat.is_moving or len(self.boat.passengers) == 0:
            return

        m_count = sum(1 for c in self.boat.passengers if c.char_type == 'missionary')
        c_count = sum(1 for c in self.boat.passengers if c.char_type == 'cannibal')

        if self.state.boat == BoatPosition.LEFT:
            new_m = self.state.missionaries_left - m_count
            new_c = self.state.cannibals_left - c_count
            new_boat = BoatPosition.RIGHT
        else:
            new_m = self.state.missionaries_left + m_count
            new_c = self.state.cannibals_left + c_count
            new_boat = BoatPosition.LEFT

        self.state = GameState(new_m, new_c, new_boat)
        self.move_count += 1

        new_side = 'left' if self.state.boat == BoatPosition.LEFT else 'right'
        self.boat.move_to(self.state.boat)

        for char in self.boat.passengers:
            char.side = new_side

    def start_eating_animation(self):
        """Start the eating animation for missionaries on the losing side."""
        self.current_screen = GameScreen.EATING
        self.eating_timer = 0.0

        m_left = self.state.missionaries_left
        c_left = self.state.cannibals_left
        m_right = self.state.missionaries_right()
        c_right = self.state.cannibals_right()

        losing_side = None
        if m_left > 0 and c_left > m_left:
            losing_side = 'left'
        if m_right > 0 and c_right > m_right:
            losing_side = 'right'

        for m in self.missionaries:
            if m.side == losing_side:
                m.being_eaten = True

    def finish_crossing(self):
        """Complete the river crossing and check win/lose conditions."""
        for char in list(self.boat.passengers):
            char.in_boat = False
            char.selected = False
            char.update_position()

        self.boat.passengers.clear()
        self.selected_characters.clear()

        if self.state.is_goal():
            self.current_screen = GameScreen.WON
        elif not self.state.is_valid():
            self.start_eating_animation()

    def update(self, dt):
        """Update game state each frame."""
        if self.current_screen == GameScreen.EATING:
            self.eating_timer += dt
            for char in self.get_all_characters():
                char.update(dt)

            if self.eating_timer >= EATING_DURATION + 0.5:
                self.current_screen = GameScreen.LOST
            return

        if self.current_screen != GameScreen.PLAYING:
            return

        was_moving = self.boat.is_moving
        self.boat.update(dt)

        if was_moving and not self.boat.is_moving:
            self.finish_crossing()

        for char in self.get_all_characters():
            char.update(dt)

    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                return False

            if event.key == pygame.K_r:
                self.reset_game()
                return True

            if self.current_screen == GameScreen.WELCOME:
                if event.key == pygame.K_SPACE:
                    self.reset_game()
            elif self.current_screen == GameScreen.PLAYING:
                if event.key == pygame.K_SPACE:
                    self.try_cross_river()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.current_screen == GameScreen.WELCOME:
                self.reset_game()
            elif self.current_screen == GameScreen.PLAYING:
                pos = event.pos

                if self.boat.contains_point(pos):
                    self.try_cross_river()
                    return True

                for char in self.get_all_characters():
                    if char.contains_point(pos):
                        self.handle_character_click(char)
                        break

        return True

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False

            self.update(dt)
            self.view.draw(self)

        pygame.quit()
        sys.exit()
