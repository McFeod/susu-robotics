import pygame
import math

from sprite import ImageSprite


def load_labyrinth(filename, field_width, field_height):
    """
    Загрузка лабиринта из файла
    :param field_width: ширина поля
    :param field_height: высота поля
    :param filename: имя файла
    :return: спрайт с лабиринтом, масштаб
    """
    with open(filename) as file:
        line = file.readline()
        width, height = map(int, line.split(' '))
        factor = min(field_width / width, field_height / height)
        surface, robot_pos = render_labyrinth((field_width, field_height), file, factor, height)
        labyrinth = ImageSprite(surface)
        labyrinth.rect.topleft = (0, 0)
        return labyrinth, factor, robot_pos


def render_labyrinth(screen_size, matrix, factor, height):
    """
    Отрисовка лабиринта после загрузки
    :param height: высота поля в клетках
    :param screen_size: размеры изображения
    :param matrix: матрица клеток
    :param factor: масштаб
    :return: Surface
    """

    def get_color(elem):
        table = {'1': (0, 127, 0),
                 '0': (255, 255, 255)}
        return table[elem]
    surface = pygame.Surface(screen_size).convert_alpha()
    bottom_left = None
    for dy, row in enumerate(matrix):
        row_found = False
        for dx, color in enumerate(row):
            try:
                pygame.draw.rect(surface, get_color(color), pygame.Rect(
                    round(dx * factor), round(dy * factor), math.ceil(factor), math.ceil(factor)
                ))
                if not row_found:
                    if color == '0':
                        row_found = True
                        bottom_left = dx + 10, height - dy + 9
            except KeyError:
                pass
    return surface, bottom_left
