import pygame
import math

import pytweening

from robot_position import RobotPosition


class ImageSprite(pygame.sprite.Sprite):
    """
    Создание спрайта из изображения
    """
    def __init__(self, surface):
        super().__init__()
        self.image = surface.convert()
        self.image.set_colorkey((255, 255, 255))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)


class DistanceSensorSpite(pygame.sprite.Sprite):
    """
    Сенсор расстояния
    """
    def __init__(self, start, end, factor, height):
        super().__init__()
        self.start_func = get_rotate_around_robot_function(factor, height, start)
        self.end_func = get_rotate_around_robot_function(factor, height, end)
        self.image = pygame.Surface((int(round(factor)), int(round(factor))),
                                    pygame.SRCALPHA, 32).convert_alpha()
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.distance_func = DistanceSensorSpite.get_distance_function(factor)

    def transform(self, robot):
        # self.rect.center = self.end_func(robot)
        self.rect.center = self.end_func(robot)

    @staticmethod
    def get_distance_function(factor):
        def func(point, x, y):
            return math.hypot(x - point[0], y - point[1]) / factor
        return func

    def get_distance(self, robot, mask):
        """
        Расчёт расстояния до препятствия
        :param robot: позиция робота
        :param mask: маска лабиринта
        :return: число от 0 до 6
        """
        start_x, start_y = self.start_func(robot)
        end_x, end_y = self.end_func(robot)
        for point in pytweening.getLine(start_x, start_y, end_x, end_y):
            try:
                if mask.get_at(point):
                    return self.distance_func(point, start_x, start_y)
            except IndexError:
                return 0
        return 6


class LeftSensor(DistanceSensorSpite):
    def __init__(self, factor, height):
        super().__init__((6.5, 4), (12.5, 4), factor, height)


class RightSensor(DistanceSensorSpite):
    def __init__(self, factor, height):
        super().__init__((6.5, -4), (12.5, -4), factor, height)


class RobotSprite(pygame.sprite.Sprite):
    """
    Отрисовка робота
    """
    @staticmethod
    def generate_surface(factor):
        """
        Создание картинки
        :param factor: масштаб
        :return: Surface
        """
        width = int(round(13 * factor))
        height = int(round(10 * factor))
        surf = pygame.Surface((width, height), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.rect(surf, (0, 0, 127), pygame.Rect(math.ceil(5 * factor), 0, math.ceil(8 * factor), height))
        pygame.draw.rect(surf, (32, 32, 32), pygame.Rect(math.ceil(5 * factor), 0, math.ceil(3 * factor), math.ceil(2 * factor)))
        pygame.draw.rect(surf, (32, 32, 32), pygame.Rect(math.ceil(5 * factor), math.ceil(8 * factor), math.ceil(3 * factor), math.ceil(2 * factor)))
        return surf

    def __init__(self, factor, x, y, height):
        super().__init__()
        self.image = RobotSprite.generate_surface(factor)
        self.robot = RobotPosition(x=x*factor, y=y*factor, half_axis=factor*4)
        self.original_image = self.image.copy()
        self.image_backup = None
        self.backup = None
        self.rect = self.image.get_rect()
        self.turn = False
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_backup = self.mask
        self.field_height = height
        self.sensors = []
        self.transform()

    def setup_coords(self):
        self.rect.centerx = self.robot.x
        self.rect.centery = self.field_height - self.robot.y

    def transform(self, force_rotate=False):
        """
        Выполнение поворота и переноса координат
        :return:
        """
        self.setup_coords()
        self.mask_backup = self.mask
        self.image_backup = self.image
        self.rotation(force_rotate)
        self.setup_coords()
        for sensor in self.sensors:
            sensor.transform(self.robot)
        self.mask = pygame.mask.from_surface(self.image)

    def rotation(self, force):
        """
        Выполнение поворота при необходимости
        :return:
        """
        if not force and self.backup is not None and self.robot.angle == self.backup.angle:
            return self.image
        self.image = pygame.transform.rotate(
            self.original_image, self.robot.angle)
        self.change_rect()

    def change_rect(self):
        """
        Изменение размеров спрайта
        :return:
        """
        r = self.image.get_rect()
        r.center = self.rect.center
        self.rect = r

    def restore_from_backup(self):
        """
        Откат при столкновении
        :return:
        """
        self.backup.power_right = self.robot.power_right
        self.backup.power_left = self.robot.power_left
        self.robot = self.backup
        self.rect = self.image_backup.get_rect()
        self.image = self.image_backup
        self.mask = self.mask_backup
        self.setup_coords()
        for sensor in self.sensors:
            sensor.transform(self.robot)

    def collides(self, sprite):
        """
        Проверка столкновения
        :param sprite: другой спрайт (лабиринт)
        :return: координаты столкновения / None
        """
        return pygame.sprite.collide_mask(self, sprite) is not None and not self.turn

    def make_step(self, sprite, step=1.0):
        """
        Передвижение робота
        :param sprite: спрайт для проверки столкновений
        :param step: продолжительность движения
        :return: None
        """
        self.backup = self.robot
        self.robot = self.robot.go(step)
        self.transform()
        if self.collides(sprite):
            self.restore_from_backup()

    def set_power(self, left, right, auto=False):
        self.robot.power_left = left
        self.robot.power_right = right
        self.turn = auto

    def add_sensor(self, sensor):
        self.sensors.append(sensor)


class ExitSprite(pygame.sprite.Sprite):
    """
    Спрайт выхода из лабиринта
    """
    def __init__(self, factor):
        super().__init__()
        self.image = ExitSprite.draw_exit(factor)
        self.rect = self.image.get_rect()
        self.rect.x = 100500

    @staticmethod
    def draw_exit(factor):
        width = int(round(20 * factor))
        height = int(round(20 * factor))
        surf = pygame.Surface((width, height), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.circle(
            surf, (127, 127, 0), (math.ceil(10*factor), math.ceil(10*factor)), math.ceil(8*factor))
        return surf


def rotate_around(origin, point, angle):
    """
    Поворот вокруг точки
    :param origin: центр вращения
    :param point: старые координаты
    :param angle: угол поворота
    :return: новые координаты
    """
    ox, oy = origin
    px, py = point
    angle = math.radians(angle)
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def get_rotate_around_robot_function(factor, field_height, point):
    """
    Возвращает функцию, вращающую сенсоры при повороте робота
    :param factor: масштаб
    :param field_height: высота поля (для инверсии координат)
    :param point: координаты сенсора относительно центра робота
    :return: функция поворота
    """
    dx = factor * point[0]
    dy = factor * point[1]

    def func(robot):
        x, y = rotate_around((robot.x, robot.y), (robot.x + dx, robot.y + dy), robot.angle)
        y = field_height - y
        return x, y

    return func
