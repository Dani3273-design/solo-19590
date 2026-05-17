import pygame
import threading
import queue


class PuzzleController:
    def __init__(self, grid_size=6, piece_size=100, offset_x=50, offset_y=50):
        self.grid_size = grid_size
        self.piece_size = piece_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.pieces = []
        self.empty_index = None
        self.is_animating = False
        self.animating_piece = None
        self.animation_start_pos = None
        self.animation_end_pos = None
        self.animation_progress = 0
        self.animation_duration = 200
        self.animation_thread = None
        self.animation_queue = queue.Queue()
        self.dragging_piece = None
        self.drag_offset = (0, 0)
        self.mouse_pos = (0, 0)
        self.is_dragging = False
        self.move_callback = None
        self._lock = threading.Lock()

    def set_pieces(self, pieces):
        self.pieces = pieces
        for idx, piece in enumerate(pieces):
            if piece['id'] == self.grid_size * self.grid_size - 1:
                self.empty_index = idx
                break

    def get_piece_at_pos(self, screen_pos):
        x, y = screen_pos
        col = (x - self.offset_x) // self.piece_size
        row = (y - self.offset_y) // self.piece_size

        if 0 <= col < self.grid_size and 0 <= row < self.grid_size:
            index = row * self.grid_size + col
            if index != self.empty_index:
                return index, row, col
        return None, None, None

    def is_adjacent_to_empty(self, row, col):
        empty_row = self.empty_index // self.grid_size
        empty_col = self.empty_index % self.grid_size

        row_diff = abs(row - empty_row)
        col_diff = abs(col - empty_col)

        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)

    def handle_mouse_down(self, pos):
        if self.is_animating:
            return False

        piece_idx, row, col = self.get_piece_at_pos(pos)
        if piece_idx is not None and self.is_adjacent_to_empty(row, col):
            self.dragging_piece = piece_idx
            self.is_dragging = True
            piece_x = self.offset_x + col * self.piece_size
            piece_y = self.offset_y + row * self.piece_size
            self.drag_offset = (pos[0] - piece_x, pos[1] - piece_y)
            self.mouse_pos = pos
            return True
        return False

    def handle_mouse_motion(self, pos):
        if self.is_dragging and self.dragging_piece is not None:
            self.mouse_pos = pos
            return True
        return False

    def handle_mouse_up(self, pos):
        if not self.is_dragging or self.dragging_piece is None:
            return False

        piece = self.pieces[self.dragging_piece]
        current_row = piece['current_row']
        current_col = piece['current_col']
        empty_row = self.empty_index // self.grid_size
        empty_col = self.empty_index % self.grid_size

        original_x = self.offset_x + current_col * self.piece_size
        original_y = self.offset_y + current_row * self.piece_size

        drag_x = pos[0] - self.drag_offset[0]
        drag_y = pos[1] - self.drag_offset[1]

        drag_delta_x = drag_x - original_x
        drag_delta_y = drag_y - original_y
        drag_distance = (drag_delta_x ** 2 + drag_delta_y ** 2) ** 0.5

        empty_direction_x = empty_col - current_col
        empty_direction_y = empty_row - current_row

        dot_product = drag_delta_x * empty_direction_x + drag_delta_y * empty_direction_y

        move_threshold = self.piece_size * 0.3

        if drag_distance > move_threshold and dot_product > 0:
            self.start_move_animation(self.dragging_piece, empty_row, empty_col)
        else:
            self.start_move_animation(self.dragging_piece, current_row, current_col)

        self.is_dragging = False
        self.dragging_piece = None
        return True

    def start_move_animation(self, piece_idx, target_row, target_col):
        piece = self.pieces[piece_idx]
        start_row = piece['current_row']
        start_col = piece['current_col']

        if start_row == target_row and start_col == target_col:
            return

        with self._lock:
            self.is_animating = True
            self.animating_piece = piece_idx
            self.animation_start_pos = (
                self.offset_x + start_col * self.piece_size,
                self.offset_y + start_row * self.piece_size
            )
            self.animation_end_pos = (
                self.offset_x + target_col * self.piece_size,
                self.offset_y + target_row * self.piece_size
            )
            self.animation_progress = 0
            self.animation_start_time = pygame.time.get_ticks()
            self.animation_start_row = start_row
            self.animation_start_col = start_col
            self.animation_target_row = target_row
            self.animation_target_col = target_col

    def update_animation(self):
        if not self.is_animating or self.animating_piece is None:
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.animation_start_time
        self.animation_progress = min(1.0, elapsed / self.animation_duration)

        if self.animation_progress >= 1.0:
            self._complete_animation()

    def _complete_animation(self):
        with self._lock:
            old_row = self.animation_start_row
            old_col = self.animation_start_col
            new_row = self.animation_target_row
            new_col = self.animation_target_col

            old_index = old_row * self.grid_size + old_col
            new_index = new_row * self.grid_size + new_col

            if new_index == self.empty_index:
                self.pieces[old_index]['current_row'] = new_row
                self.pieces[old_index]['current_col'] = new_col
                self.pieces[new_index]['current_row'] = old_row
                self.pieces[new_index]['current_col'] = old_col

                self.pieces[old_index], self.pieces[new_index] = self.pieces[new_index], self.pieces[old_index]
                self.empty_index = old_index

                if self.move_callback:
                    self.move_callback()

            self.is_animating = False
            self.animating_piece = None

    def get_piece_draw_pos(self, piece_idx):
        piece = self.pieces[piece_idx]

        if self.is_dragging and piece_idx == self.dragging_piece:
            x = self.mouse_pos[0] - self.drag_offset[0]
            y = self.mouse_pos[1] - self.drag_offset[1]
            return x, y

        if self.is_animating and piece_idx == self.animating_piece:
            t = self.animation_progress
            ease_t = t * t * (3 - 2 * t)
            start_x, start_y = self.animation_start_pos
            end_x, end_y = self.animation_end_pos
            x = start_x + (end_x - start_x) * ease_t
            y = start_y + (end_y - start_y) * ease_t
            return x, y

        x = self.offset_x + piece['current_col'] * self.piece_size
        y = self.offset_y + piece['current_row'] * self.piece_size
        return x, y

    def is_busy(self):
        return self.is_animating or self.is_dragging
