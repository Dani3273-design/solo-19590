import random
from PIL import Image, ImageDraw, ImageFilter
import io
import pygame


class PuzzleGenerator:
    def __init__(self, grid_size=3, piece_size=100):
        self.grid_size = grid_size
        self.piece_size = piece_size
        self.total_pieces = grid_size * grid_size
        self.image = None
        self.pieces = []
        self.piece_hashes = set()

    def generate_random_image(self):
        width = self.grid_size * self.piece_size
        height = self.grid_size * self.piece_size
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        for _ in range(50):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(50, 200)
            y2 = y1 + random.randint(50, 200)
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            shape_type = random.choice(['rect', 'ellipse', 'circle'])
            if shape_type == 'rect':
                draw.rectangle([x1, y1, x2, y2], fill=color, outline=None)
            elif shape_type == 'ellipse':
                draw.ellipse([x1, y1, x2, y2], fill=color, outline=None)
            elif shape_type == 'circle':
                r = random.randint(30, 100)
                draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=color, outline=None)

        for _ in range(20):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(20, 150)
            y2 = y1 + random.randint(20, 150)
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(2, 8))

        for _ in range(100):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            color = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            for dx in range(random.randint(1, 5)):
                for dy in range(random.randint(1, 5)):
                    if 0 <= x + dx < width and 0 <= y + dy < height:
                        draw.point((x + dx, y + dy), fill=color)

        image = image.filter(ImageFilter.SMOOTH)
        self.image = image
        return image

    def split_into_pieces(self):
        self.pieces = []
        self.piece_hashes.clear()
        width, height = self.image.size

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                left = col * self.piece_size
                top = row * self.piece_size
                right = left + self.piece_size
                bottom = top + self.piece_size
                piece = self.image.crop((left, top, right, bottom))

                piece_hash = self._hash_piece(piece)
                while piece_hash in self.piece_hashes:
                    self._modify_piece(piece)
                    piece_hash = self._hash_piece(piece)
                self.piece_hashes.add(piece_hash)

                self.pieces.append({
                    'image': piece,
                    'correct_row': row,
                    'correct_col': col,
                    'id': row * self.grid_size + col
                })

        return self.pieces

    def _modify_piece(self, piece):
        draw = ImageDraw.Draw(piece)
        x = random.randint(0, self.piece_size - 5)
        y = random.randint(0, self.piece_size - 5)
        color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        for dx in range(3):
            for dy in range(3):
                if 0 <= x + dx < self.piece_size and 0 <= y + dy < self.piece_size:
                    draw.point((x + dx, y + dy), fill=color)

    def _hash_piece(self, piece):
        buf = io.BytesIO()
        piece.save(buf, format='PNG')
        return hash(buf.getvalue())

    def validate_pieces_unique(self):
        hashes = set()
        for piece in self.pieces:
            piece_hash = self._hash_piece(piece['image'])
            if piece_hash in hashes:
                return False
            hashes.add(piece_hash)
        return True

    def check_not_all_blank(self):
        for piece in self.pieces:
            extrema = piece['image'].convert('L').getextrema()
            if extrema[0] == extrema[1] == 255:
                return False
        return True

    def shuffle_pieces(self):
        pieces_copy = self.pieces[:-1].copy()
        empty_piece = self.pieces[-1]

        while True:
            random.shuffle(pieces_copy)
            if self._is_solvable(pieces_copy):
                break

        pieces_copy.append(empty_piece)
        shuffled = []
        for idx, piece in enumerate(pieces_copy):
            shuffled.append({
                'image': piece['image'],
                'correct_row': piece['correct_row'],
                'correct_col': piece['correct_col'],
                'id': piece['id'],
                'current_row': idx // self.grid_size,
                'current_col': idx % self.grid_size
            })

        return shuffled

    def _is_solvable(self, pieces):
        ids = [p['id'] for p in pieces]
        inversions = 0
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                if ids[i] > ids[j]:
                    inversions += 1

        if self.grid_size % 2 == 1:
            return inversions % 2 == 0
        else:
            empty_row_from_bottom = self.grid_size
            return (inversions + empty_row_from_bottom) % 2 == 1

    def is_complete(self, pieces):
        for piece in pieces:
            if piece['id'] != piece['current_row'] * self.grid_size + piece['current_col']:
                return False
        return True

    @staticmethod
    def pil_to_pygame(image):
        mode = image.mode
        size = image.size
        data = image.tobytes()
        return pygame.image.fromstring(data, size, mode)
