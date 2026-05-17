import pygame
import os
import sys


class Button:
    def __init__(self, x, y, width, height, text, font, color=(70, 130, 180), hover_color=(100, 149, 237), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1:
                return True
        return False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class UIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fonts = {}
        self._init_fonts()
        self.colors = {
            'bg': (240, 248, 255),
            'title': (25, 25, 112),
            'text': (47, 79, 79),
            'panel': (255, 255, 255),
            'grid_bg': (220, 220, 220),
            'highlight': (255, 215, 0)
        }

    def _init_fonts(self):
        font_paths = [
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/arphic/ukai.ttc',
            'C:/Windows/Fonts/msyh.ttc',
            'C:/Windows/Fonts/simhei.ttf',
        ]

        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break

        try:
            self.fonts['title'] = pygame.font.Font(font_path, 48) if font_path else pygame.font.SysFont('arial', 48)
            self.fonts['subtitle'] = pygame.font.Font(font_path, 28) if font_path else pygame.font.SysFont('arial', 28)
            self.fonts['button'] = pygame.font.Font(font_path, 24) if font_path else pygame.font.SysFont('arial', 24)
            self.fonts['normal'] = pygame.font.Font(font_path, 20) if font_path else pygame.font.SysFont('arial', 20)
            self.fonts['small'] = pygame.font.Font(font_path, 16) if font_path else pygame.font.SysFont('arial', 16)
        except Exception:
            self.fonts['title'] = pygame.font.SysFont('arial', 48)
            self.fonts['subtitle'] = pygame.font.SysFont('arial', 28)
            self.fonts['button'] = pygame.font.SysFont('arial', 24)
            self.fonts['normal'] = pygame.font.SysFont('arial', 20)
            self.fonts['small'] = pygame.font.SysFont('arial', 16)

    def draw_start_screen(self, surface):
        surface.fill(self.colors['bg'])

        title_text = self.fonts['title'].render('滑动拼图游戏', True, self.colors['title'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 120))
        surface.blit(title_text, title_rect)

        instructions = [
            '游戏说明：',
            '1. 使用鼠标拖动相邻空位的拼图块进行移动',
            '2. 将所有拼图块移动到正确的位置即可完成',
            '3. 每次只能移动与空位相邻的拼图块',
            '4. 尝试用最少的步数和时间完成挑战！'
        ]

        y_offset = 200
        for line in instructions:
            text = self.fonts['normal'].render(line, True, self.colors['text'])
            text_rect = text.get_rect(center=(self.screen_width // 2, y_offset))
            surface.blit(text, text_rect)
            y_offset += 35

    def draw_game_screen(self, surface, pieces, controller, puzzle_gen, counter, grid_offset_x, grid_offset_y, target_image=None):
        surface.fill(self.colors['bg'])

        grid_width = controller.grid_size * controller.piece_size
        grid_height = controller.grid_size * controller.piece_size

        pygame.draw.rect(
            surface, self.colors['grid_bg'],
            (grid_offset_x - 5, grid_offset_y - 5, grid_width + 10, grid_height + 10),
            border_radius=5
        )

        for idx, piece in enumerate(pieces):
            if idx == controller.empty_index:
                continue

            if idx == controller.dragging_piece:
                continue

            if idx == controller.animating_piece:
                continue

            x, y = controller.get_piece_draw_pos(idx)
            piece_surface = puzzle_gen.pil_to_pygame(piece['image'])
            surface.blit(piece_surface, (x, y))
            pygame.draw.rect(surface, (100, 100, 100), (x, y, controller.piece_size, controller.piece_size), 1)

        if controller.animating_piece is not None:
            x, y = controller.get_piece_draw_pos(controller.animating_piece)
            piece = pieces[controller.animating_piece]
            piece_surface = puzzle_gen.pil_to_pygame(piece['image'])
            surface.blit(piece_surface, (x, y))
            pygame.draw.rect(surface, (100, 100, 100), (x, y, controller.piece_size, controller.piece_size), 1)

        if controller.dragging_piece is not None:
            x, y = controller.get_piece_draw_pos(controller.dragging_piece)
            piece = pieces[controller.dragging_piece]
            piece_surface = puzzle_gen.pil_to_pygame(piece['image'])
            surface.blit(piece_surface, (x, y))
            pygame.draw.rect(surface, self.colors['highlight'], (x, y, controller.piece_size, controller.piece_size), 3)

        info_panel_x = grid_offset_x + grid_width + 30
        info_panel_y = grid_offset_y
        info_panel_width = 200
        info_panel_height = 200

        pygame.draw.rect(
            surface, self.colors['panel'],
            (info_panel_x, info_panel_y, info_panel_width, info_panel_height),
            border_radius=10
        )
        pygame.draw.rect(
            surface, (200, 200, 200),
            (info_panel_x, info_panel_y, info_panel_width, info_panel_height),
            2, border_radius=10
        )

        time_text = self.fonts['subtitle'].render('用时', True, self.colors['title'])
        time_rect = time_text.get_rect(center=(info_panel_x + info_panel_width // 2, info_panel_y + 35))
        surface.blit(time_text, time_rect)

        time_value = self.fonts['subtitle'].render(counter.get_formatted_time(), True, self.colors['text'])
        time_value_rect = time_value.get_rect(center=(info_panel_x + info_panel_width // 2, info_panel_y + 70))
        surface.blit(time_value, time_value_rect)

        moves_text = self.fonts['subtitle'].render('步数', True, self.colors['title'])
        moves_rect = moves_text.get_rect(center=(info_panel_x + info_panel_width // 2, info_panel_y + 115))
        surface.blit(moves_text, moves_rect)

        moves_value = self.fonts['subtitle'].render(str(counter.get_moves()), True, self.colors['text'])
        moves_value_rect = moves_value.get_rect(center=(info_panel_x + info_panel_width // 2, info_panel_y + 150))
        surface.blit(moves_value, moves_value_rect)

        if target_image is not None:
            preview_size = 120
            preview_x = info_panel_x + (info_panel_width - preview_size) // 2
            preview_y = info_panel_y + info_panel_height + 160
            preview_label = self.fonts['small'].render('目标图', True, self.colors['title'])
            preview_label_rect = preview_label.get_rect(center=(preview_x + preview_size // 2, preview_y - 20))
            surface.blit(preview_label, preview_label_rect)
            pygame.draw.rect(surface, (200, 200, 200), (preview_x - 2, preview_y - 2, preview_size + 4, preview_size + 4), 2)
            target_surface = puzzle_gen.pil_to_pygame(target_image.resize((preview_size, preview_size)))
            surface.blit(target_surface, (preview_x, preview_y))

    def draw_result_screen(self, surface, counter):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        panel_width = 400
        panel_height = 430
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2

        pygame.draw.rect(surface, self.colors['panel'], (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(surface, self.colors['title'], (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)

        title_text = self.fonts['title'].render('恭喜完成！', True, self.colors['title'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, panel_y + 60))
        surface.blit(title_text, title_rect)

        time_label = self.fonts['subtitle'].render('总用时', True, self.colors['text'])
        time_label_rect = time_label.get_rect(center=(self.screen_width // 2, panel_y + 130))
        surface.blit(time_label, time_label_rect)

        time_value = self.fonts['title'].render(counter.get_formatted_time(), True, (220, 20, 60))
        time_value_rect = time_value.get_rect(center=(self.screen_width // 2, panel_y + 180))
        surface.blit(time_value, time_value_rect)

        moves_label = self.fonts['subtitle'].render('总步数', True, self.colors['text'])
        moves_label_rect = moves_label.get_rect(center=(self.screen_width // 2, panel_y + 250))
        surface.blit(moves_label, moves_label_rect)

        moves_value = self.fonts['title'].render(str(counter.get_moves()), True, (220, 20, 60))
        moves_value_rect = moves_value.get_rect(center=(self.screen_width // 2, panel_y + 300))
        surface.blit(moves_value, moves_value_rect)
