import os

from dama.board import Board

import pyglet

SPRITE_SIZE = 128
BOARD_SIZE_COEFF = 0.9
spritesheet = pyglet.image.load('dama/resources/spritesheet.png')


def get_region(x, y):
    image = spritesheet.get_region(x=x*(SPRITE_SIZE+1), y=y*(SPRITE_SIZE+1),
                                   width=SPRITE_SIZE, height=SPRITE_SIZE)
    image.anchor_x = SPRITE_SIZE // 2
    image.anchor_y = SPRITE_SIZE // 2
    return image


bg_light = get_region(0, 0)
bg_dark = get_region(1, 0)
img_empty = get_region(2, 0)
img_shine = get_region(2, 1)
img_x = get_region(2, 2)
piece_images = {
    'w': get_region(0, 1),
    'b': get_region(1, 1),
    'W': get_region(0, 2),
    'B': get_region(1, 2),
    None: img_empty,
}


def make_window(board=None):
    window_style = getattr(
        pyglet.window.Window,
        'WINDOW_STYLE_' + os.environ.get('GAME_WINDOW_STYLE', 'DEFAULT'),
    )

    board = board or Board()
    ideal_size = int(SPRITE_SIZE * board.size * BOARD_SIZE_COEFF)
    window = pyglet.window.Window(width=ideal_size, height=ideal_size,
                                  style=window_style)
    window.set_minimum_size(ideal_size//2, ideal_size//2)

    move = []

    hovered_tile = None

    bg_batch = pyglet.graphics.Batch()
    bg_sprites = {}
    piece_batch = pyglet.graphics.Batch()
    piece_sprites = {}
    shine_batch = pyglet.graphics.Batch()
    shine_sprites = {}
    for x in range(board.size):
        for y in range(board.size):
            bg_sprites[x, y] = pyglet.sprite.Sprite(
                bg_dark if (x, y) in board.valid_coords else bg_light,
                batch=bg_batch)
            piece_sprites[x, y] = pyglet.sprite.Sprite(
                piece_images[board.pieces.get((x, y))],
                batch=piece_batch)
            shine_sprites[x, y] = pyglet.sprite.Sprite(
                img_shine,
                batch=shine_batch)

    def _size_vars():
        size = min(window.width, window.height) * BOARD_SIZE_COEFF
        tile_size = size / board.size
        start_x = (window.width - size + tile_size) / 2
        start_y = (window.height - size + tile_size) / 2
        return size, tile_size, start_x, start_y

    def mouse_to_logical(x, y):
        size, tile_size, start_x, start_y = _size_vars()
        return ((x - start_x) / tile_size + 1/2,
                (y - start_y) / tile_size + 1/2)

    def logical_to_mouse(x, y):
        size, tile_size, start_x, start_y = _size_vars()
        return ((x - 1/2) * tile_size + start_x,
                (y - 1/2) * tile_size + start_y)

    def reset_piece_sprites():
        for (x, y), sprite in piece_sprites.items():
            sprite.image = piece_images[board.pieces.get((x, y))]

    def shine():
        possible_moves = board.possible_moves(move)
        jumped = set(board.get_jumped(move))
        for pos, sprite in shine_sprites.items():
            if pos in possible_moves:
                if pos == hovered_tile:
                    sprite.color = 255, 255, 255
                    sprite.opacity = 255
                    sprite.scale = 1.3
                else:
                    sprite.color = 255, 255, 255
                    sprite.opacity = 200
                    sprite.scale = 1
            elif pos in move:
                sprite.color = 255, 231, 107
                sprite.opacity = 255
                sprite.scale = 1
            elif pos in jumped:
                sprite.color = 255, 100, 100
                sprite.opacity = 200
                sprite.scale = 0.8
            else:
                sprite.opacity = 0
                sprite.scale = 0
    shine()

    @window.event
    def on_draw():
        window.clear()
        bg_batch.draw()
        shine_batch.draw()
        piece_batch.draw()

    @window.event
    def on_resize(w, h):
        size, tile_size, start_x, start_y = _size_vars()
        for sprites in bg_sprites, shine_sprites, piece_sprites:
            for (x, y), sprite in sprites.items():
                sprite.x = start_x + x * tile_size
                sprite.y = start_y + y * tile_size
                sprite.scale = tile_size / sprite.image.width

    @window.event
    def on_mouse_motion(mx, my, dx, dy):
        nonlocal hovered_tile
        x, y = mouse_to_logical(mx, my)
        hovered_tile = int(x), int(y)
        shine()

    @window.event
    def on_mouse_press(mx, my, btn, mod):
        nonlocal hovered_tile
        x, y = mouse_to_logical(mx, my)
        pos = int(x), int(y)
        if pos in board.possible_moves(move):
            move.append(pos)
        elif pos in move:
            while pos in move:
                move.pop()
        else:
            print('nope')
        if move and not board.possible_moves(move):
            board.make_move(move)
            move.clear()
            print(board.dump())
            reset_piece_sprites()
        shine()


def run(board=None):
    make_window(board=board)
    pyglet.app.run()


if __name__ == '__main__':
    run()
