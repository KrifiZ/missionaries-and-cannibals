"""View class for rendering the Missionaries and Cannibals game."""

import math
import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE, COLOR_BLACK, COLOR_RED,
    COLOR_GREEN, COLOR_SELECTED, CHARACTER_SIZE, GameScreen
)


class GameView:
    """Handles all rendering for the game."""

    def __init__(self, screen, fonts, images):
        """Initialize view with screen, fonts and images."""
        self.screen = screen
        self.font_large = fonts['large']
        self.font_medium = fonts['medium']
        self.font_small = fonts['small']
        self.missionary_img = images['missionary']
        self.cannibal_img = images['cannibal']
        self.background_img = images['background']
        self.boat_img = images['boat']

    def draw_character(self, char):
        """Draw a character sprite with rotation and selection highlight."""
        if not char.visible:
            return

        if char.being_eaten:
            size = int(CHARACTER_SIZE * char.eat_scale)
            if size < 1:
                return
            scaled = pygame.transform.scale(char.image, (size, size))
            rotated = pygame.transform.rotate(scaled, char.angle)
        else:
            rotated = pygame.transform.rotate(char.image, char.angle)

        rect = rotated.get_rect(center=(int(char.x), int(char.y)))

        if char.selected and not char.being_eaten:
            highlight_rect = rect.inflate(10, 10)
            pygame.draw.rect(self.screen, COLOR_SELECTED, highlight_rect, 4, border_radius=8)

        self.screen.blit(rotated, rect)

    def draw_boat(self, boat):
        """Draw the boat sprite with rotation."""
        rotated = pygame.transform.rotate(boat.image, boat.angle)
        rect = rotated.get_rect(center=(int(boat.x), int(boat.y)))
        self.screen.blit(rotated, rect)

    def draw_text_with_bg(self, text, font, pos, color=COLOR_BLACK):
        """Draw text with a semi-transparent background."""
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(topleft=pos)

        bg_rect = text_rect.inflate(10, 6)
        bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surf.fill((255, 255, 255, 180))
        self.screen.blit(bg_surf, bg_rect.topleft)
        self.screen.blit(text_surf, text_rect)

    def draw_ui(self, state, move_count, boat_is_moving, passengers_count):
        """Draw the game UI elements."""
        self.draw_text_with_bg(f"Moves: {move_count}", self.font_medium, (10, 10))

        state_str = (f"Left: {state.missionaries_left}M "
                     f"{state.cannibals_left}C | "
                     f"Right: {state.missionaries_right()}M "
                     f"{state.cannibals_right()}C")
        self.draw_text_with_bg(state_str, self.font_small, (10, 50))

        if not boat_is_moving:
            if passengers_count == 0:
                hint = "Click characters to board the boat"
            else:
                hint = "Press SPACE or click boat to cross"
            hint_surf = self.font_small.render(hint, True, COLOR_BLACK)
            hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))

            bg_rect = hint_rect.inflate(20, 10)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((255, 255, 255, 180))
            self.screen.blit(bg_surf, bg_rect.topleft)
            self.screen.blit(hint_surf, hint_rect)

        self.draw_text_with_bg("R: Restart | ESC: Quit", self.font_small,
                               (SCREEN_WIDTH - 190, 10))

    def draw_welcome_screen(self):
        """Draw the welcome screen with rules."""
        self.screen.blit(self.background_img, (0, 0))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("Missionaries and Cannibals", True, COLOR_BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        m_rect = self.missionary_img.get_rect(center=(350, 140))
        c_rect = self.cannibal_img.get_rect(center=(650, 140))
        self.screen.blit(self.missionary_img, m_rect)
        self.screen.blit(self.cannibal_img, c_rect)

        rules = [
            "GOAL: Get all 3 missionaries and 3 cannibals across the river.",
            "",
            "RULES:",
            "  - The boat can carry 1 or 2 people",
            "  - Cannibals must never outnumber missionaries on either bank",
            "",
            "CONTROLS:",
            "  - Click on characters to select them for the boat",
            "  - Press SPACE or click the boat to cross",
            "  - Press R to restart, ESC to quit",
        ]

        y = 200
        for line in rules:
            text = self.font_small.render(line, True, COLOR_BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 28

        alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
        start_text = self.font_medium.render("Press SPACE to Start", True, COLOR_GREEN)
        start_surf = start_text.copy()
        start_surf.set_alpha(alpha)
        start_rect = start_surf.get_rect(center=(SCREEN_WIDTH // 2, 480))
        self.screen.blit(start_surf, start_rect)

    def draw_end_screen(self, won, move_count):
        """Draw the win or lose end screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLOR_GREEN if won else COLOR_RED)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        if won:
            title = "CONGRATULATIONS!"
            message = f"You saved everyone in {move_count} moves!"
        else:
            title = "GAME OVER"
            message = "The missionaries were eaten!"

        title_text = self.font_large.render(title, True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(title_text, title_rect)

        msg_text = self.font_medium.render(message, True, COLOR_WHITE)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(msg_text, msg_rect)

        restart_text = self.font_medium.render("Press R to Play Again", True, COLOR_WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 340))
        self.screen.blit(restart_text, restart_rect)

        quit_text = self.font_medium.render("Press ESC to Quit", True, COLOR_WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 390))
        self.screen.blit(quit_text, quit_rect)

    def draw_eating_text(self, eating_timer):
        """Draw the eating animation text."""
        chomp_text = self.font_large.render("CHOMP CHOMP!", True, COLOR_RED)
        chomp_rect = chomp_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        scale = 1.0 + 0.1 * math.sin(eating_timer * 10)
        scaled = pygame.transform.scale(
            chomp_text,
            (int(chomp_rect.width * scale), int(chomp_rect.height * scale))
        )
        scaled_rect = scaled.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(scaled, scaled_rect)

    def draw(self, game_model):
        """Draw the current game state."""
        if game_model.current_screen == GameScreen.WELCOME:
            self.draw_welcome_screen()
        else:
            self.screen.blit(self.background_img, (0, 0))

            self.draw_boat(game_model.boat)

            for char in game_model.get_all_characters():
                if not char.in_boat:
                    self.draw_character(char)

            for char in game_model.boat.passengers:
                self.draw_character(char)

            if game_model.current_screen == GameScreen.EATING:
                self.draw_eating_text(game_model.eating_timer)

            self.draw_ui(game_model.state, game_model.move_count,
                         game_model.boat.is_moving, len(game_model.boat.passengers))

            if game_model.current_screen == GameScreen.WON:
                self.draw_end_screen(True, game_model.move_count)
            elif game_model.current_screen == GameScreen.LOST:
                self.draw_end_screen(False, game_model.move_count)

        pygame.display.flip()
