import pygame
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.puzzle import PuzzleGenerator
from game.control import PuzzleController
from game.ui import UIManager
from game.count import GameCounter


class GameState:
    START = 'start'
    PLAYING = 'playing'
    RESULT = 'result'


class PuzzleGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('滑动拼图游戏')

        self.grid_size = 6
        self.piece_size = 90
        self.grid_offset_x = 50
        self.grid_offset_y = 50

        self.screen_width = self.grid_offset_x * 2 + self.grid_size * self.piece_size + 250
        self.screen_height = self.grid_offset_y * 2 + self.grid_size * self.piece_size + 50

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        self.puzzle_gen = PuzzleGenerator(grid_size=self.grid_size, piece_size=self.piece_size)
        self.controller = PuzzleController(
            grid_size=self.grid_size,
            piece_size=self.piece_size,
            offset_x=self.grid_offset_x,
            offset_y=self.grid_offset_y
        )
        self.ui_manager = UIManager(self.screen_width, self.screen_height)
        self.counter = GameCounter()

        self.state = GameState.START
        self.pieces = []
        self.is_complete = False
        self.check_thread = None
        self._check_lock = threading.Lock()

        self.controller.move_callback = self.on_piece_moved

        self.start_button = None
        self.back_button = None
        self.restart_button = None
        self._init_all_buttons()

    def _init_all_buttons(self):
        from game.ui import Button

        button_width = 200
        button_height = 60
        button_x = (self.screen_width - button_width) // 2
        button_y = self.screen_height - 150
        self.start_button = Button(
            button_x, button_y, button_width, button_height,
            '开始游戏', self.ui_manager.fonts['button']
        )

        grid_width = self.grid_size * self.piece_size
        info_panel_x = self.grid_offset_x + grid_width + 30
        info_panel_y = self.grid_offset_y
        info_panel_width = 200
        info_panel_height = 200
        back_button_width = 120
        back_button_height = 45
        back_button_x = info_panel_x + (info_panel_width - back_button_width) // 2
        back_button_y = info_panel_y + info_panel_height + 20
        self.back_button = Button(
            back_button_x, back_button_y, back_button_width, back_button_height,
            '返回主页', self.ui_manager.fonts['small'],
            color=(128, 128, 128), hover_color=(169, 169, 169)
        )

        panel_width = 400
        panel_height = 350
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        restart_button_width = 180
        restart_button_height = 55
        restart_button_x = (self.screen_width - restart_button_width) // 2
        restart_button_y = panel_y + panel_height - 80
        self.restart_button = Button(
            restart_button_x, restart_button_y, restart_button_width, restart_button_height,
            '再来一局', self.ui_manager.fonts['button'],
            color=(34, 139, 34), hover_color=(50, 205, 50)
        )

    def init_game(self):
        self.puzzle_gen.generate_random_image()
        self.puzzle_gen.split_into_pieces()

        while not (self.puzzle_gen.validate_pieces_unique() and self.puzzle_gen.check_not_all_blank()):
            self.puzzle_gen.generate_random_image()
            self.puzzle_gen.split_into_pieces()

        self.pieces = self.puzzle_gen.shuffle_pieces()
        self.controller.set_pieces(self.pieces)
        self.counter.reset()
        self.counter.start()
        self.is_complete = False

    def on_piece_moved(self):
        self.counter.increment_move()
        self.check_completion_async()

    def check_completion_async(self):
        with self._check_lock:
            if self.check_thread and self.check_thread.is_alive():
                return

        self.check_thread = threading.Thread(target=self._check_completion_worker, daemon=True)
        self.check_thread.start()

    def _check_completion_worker(self):
        pieces_copy = [p.copy() for p in self.pieces]
        complete = self.puzzle_gen.is_complete(pieces_copy)
        if complete:
            self.is_complete = True

    def handle_start_screen(self, event):
        if self.start_button and self.start_button.handle_event(event):
            self.init_game()
            self.state = GameState.PLAYING
            return True
        return False

    def handle_game_screen(self, event):
        if self.back_button and self.back_button.handle_event(event):
            self.counter.stop()
            self.state = GameState.START
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.controller.is_busy():
                return self.controller.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            return self.controller.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            return self.controller.handle_mouse_up(event.pos)
        return False

    def handle_result_screen(self, event):
        if self.restart_button and self.restart_button.handle_event(event):
            self.init_game()
            self.state = GameState.PLAYING
            return True
        return False

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if self.state == GameState.START:
                    self.handle_start_screen(event)
                elif self.state == GameState.PLAYING:
                    self.handle_game_screen(event)
                elif self.state == GameState.RESULT:
                    self.handle_result_screen(event)

            if self.state == GameState.PLAYING:
                self.controller.update_animation()

                if self.is_complete and not self.controller.is_busy():
                    self.counter.stop()
                    self.state = GameState.RESULT

            self.draw()
            self.clock.tick(60)

        self.counter.stop()
        pygame.quit()
        sys.exit()

    def draw(self):
        if self.state == GameState.START:
            self.ui_manager.draw_start_screen(self.screen)
            self.start_button.draw(self.screen)
        elif self.state == GameState.PLAYING:
            self.ui_manager.draw_game_screen(
                self.screen, self.pieces, self.controller,
                self.puzzle_gen, self.counter,
                self.grid_offset_x, self.grid_offset_y
            )
            self.back_button.draw(self.screen)
        elif self.state == GameState.RESULT:
            self.ui_manager.draw_game_screen(
                self.screen, self.pieces, self.controller,
                self.puzzle_gen, self.counter,
                self.grid_offset_x, self.grid_offset_y
            )
            self.ui_manager.draw_result_screen(self.screen, self.counter)
            self.restart_button.draw(self.screen)

        pygame.display.flip()


def main():
    game = PuzzleGame()
    game.run()


if __name__ == '__main__':
    main()
