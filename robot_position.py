import math


class RobotPosition:
    speed_factor = math.pi/100  # 0.7
    """
    Расчёт координат и поворота в зависимости от мощности двигателей
    """
    def __init__(self, x=0, y=0, angle=0, pl=0, pr=0, half_axis=4):
        """
        :param x: :param y: координаты
        :param angle: угол
        :param pl: мощность левого двигателя
        :param pr: мощность правого двигателя
        :param half_axis: расстояние от центра оси до колеса
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.power_left = pl
        self.power_right = pr
        self.half_axis = half_axis

    def copy(self):
        return RobotPosition(self.x, self.y, self.angle, self.power_left, self.power_right, self.half_axis)

    def print(self):
        print(self.x, self.y, self.angle, self.power_left, self.power_right, self.half_axis)

    def go(self, step=1):
        """
        Расчёт следующего положения робота
        :param step: продолжительность перемещения
        :return: RobotPosition
        """
        angle = math.radians(self.angle)
        step *= self.speed_factor
        way_left = step * self.power_left
        way_right = step * self.power_right
        if self.power_left == self.power_right:
            x = self.x + 2 * way_left * math.cos(angle)
            y = self.y + 2 * way_left * math.sin(angle)
            return RobotPosition(x, y, self.angle, self.power_left, self.power_right, self.half_axis)

        r = (way_left + way_right) / (way_right - way_left) * self.half_axis
        da = (way_right - way_left) / self.half_axis
        dx_ = r * math.sin(da)
        dy_ = -(r - r * (math.cos(da)))
        cos = math.cos(angle + da)
        sin = math.sin(angle + da)
        dx = dx_*cos - dy_*sin
        dy = dx_*sin + dy_*cos
        new_angle = math.degrees(da) + self.angle % 360
        return RobotPosition(self.x+dx, self.y+dy, new_angle, self.power_left, self.power_right, self.half_axis)

