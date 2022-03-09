import numpy as np
import torch
import math
import pdb
from PIL import Image
from utils import Timer, save_to_image, generate_tile_image



tile_width = 32
tile_height = 32
pw = 128
ph = 128
sx = 10
device = 'cuda'

tile = generate_tile_image(tile_height, tile_width, device)
save_to_image(tile, 'tile')

image_width = tile_width + 2 * pw
image_height = tile_height + 2 * ph
image_pixels = torch.zeros((image_height, image_width, 3), device=device, dtype=float)


shift_x = (tile_width, 0)
shift_y = (sx, tile_height)

def coord_to_tile_pixel(x, y):
    """The origin is located at the lower left corner of the tile image.
    Assuming a point P with coordinates (x, y) lies in this tile, this function
    maps P's coordinates to its actual pixel location in the tile image.
    """
    return (tile_height - 1 - y, x)


def image_pixel_to_coord(x, y):
    """Map a pixel in the large image to its coordinates (x, y) relative to the origin.
    (which is the lower left corner of the tile image)
    """
    return (y - pw, image_height - 1 - x + ph)


def map_coord(x, y):
    """Assume (x, y) = (x0, y0) + shift_x * u + shift_y * v.
    This function finds P = (x0, y0) which is the corresponding point in the tile.
    """
    v = math.floor(y / tile_height)
    u = math.floor((x - v * shift_y[0]) / tile_width)
    return (x - u * shift_x[0] - v * shift_y[0], y - u * shift_x[1] - v * shift_y[1])


def map_pixel(x, y):
    x1, y1 = image_pixel_to_coord(x, y)
    x2, y2 = map_coord(x1, y1)
    return coord_to_tile_pixel(x2, y2)


with Timer():
    for row in range(image_height):
        for col in range(image_width):
            x, y = map_pixel(row, col)
            image_pixels[row, col] = tile[x, y]

save_to_image(image_pixels, 'torch')
