import random

import math

import easygui


class Labyrinth:
    """
    Представление лабиринта при генерации
    """
    def __init__(self, width=0, height=0):
        self.width = width if width % 2 else width + 1
        self.height = height if height % 2 else height + 1
        self.matrix = []
        self.all_possible_walls()

    def all_possible_walls(self):
        """
        Создание начальной сетки
        :return:
        """
        for i in range(self.height):
            row = []
            self.matrix.append(row)
            for j in range(self.width):
                row.append(not ((i % 2 == 0) or (j % 2 == 0)))

    def string_matrix(self):
        """
        Отладочная печвть в строку
        :return:
        """
        def bool_ascii(symbol):
            return '□' if symbol else '■'
        new_matrix = [[bool_ascii(x) for x in row] for row in self.matrix]
        return '\n'.join(''.join(row) for row in new_matrix)

    def __getitem__(self, item):
        if (0 < item.real <= self.height) and (0 < item.imag <= self.width):
            return self.matrix[round(item.real)-1][round(item.imag)-1]
        return None

    def break_the_wall(self, cell):
        """
        Удаление участка стены
        :param cell:
        :return:
        """
        if (0 < cell.real <= self.height) and (0 < cell.imag <= self.width):
            self.matrix[round(cell.real) - 1][round(cell.imag) - 1] = True

    def neighbours(self, point):
        """
        Итерация по соседним клеткам
        :param point: координаты клетки
        :return: координаты соседей
        """
        directions = (2j, -2j, 2, -2)
        return (x + point for x in directions if self[x + point] is not None)

    def to_file(self, filename, space_factor=20, wall_factor=20):
        """
        Запись в файл в соответствии со спецификацией
        :param filename: выходной выйл
        :param space_factor: размер свободной клетки
        :param wall_factor: толщина стен
        """
        def bool_ascii(arg):
            index, symbol = arg
            factor = space_factor if index % 2 else wall_factor
            return '0' * factor if symbol else '1' * factor
        with open(filename, 'w') as file:
            size_x = self.width//2 * space_factor + (self.width//2 + 1) * wall_factor
            size_y = self.height//2 * space_factor + (self.height//2 + 1) * wall_factor
            file.write('{} {}\n'.format(size_x, size_y))
            for i, row in enumerate(reversed(self.matrix)):
                for x in range(space_factor if i % 2 == 1 else wall_factor):
                    file.write('{}\n'.format(''.join(map(bool_ascii, enumerate(row)))))


class LabyrinthGenerator:
    """
    Непосредственная генерация лабиринта
    """
    def __init__(self, width, height):
        self.labyrinth = Labyrinth(width, height)
        self.stack = []
        self.visited = [[False for _ in row] for row in self.labyrinth.matrix]
        self.active = 2 + 2j

    def __getitem__(self, item):
        if (0 < item.real <= self.labyrinth.height) and (0 < item.imag <= self.labyrinth.width):
            return self.visited[round(item.real)-1][round(item.imag)-1]
        return None

    def mark_as_visited(self, cell):
        self.visited[round(cell.real)-1][round(cell.imag)-1] = True

    def non_visited(self, cell):
        return self.labyrinth[cell] is not None and self[cell] is False

    def make_step(self):
        """
        Главный шаг DFS'а
        :return: True, если нужно продолжить генерацию
        """
        self.mark_as_visited(self.active)
        neighbours = [x for x in self.labyrinth.neighbours(self.active) if self.non_visited(x)]
        if len(neighbours) >= 1:
            if len(neighbours) == 1:
                next_cell = neighbours[0]
            else:
                self.stack.append(self.active)
                next_cell = random.choice(neighbours)
            middle = (next_cell + self.active) / 2
            self.labyrinth.break_the_wall(middle)
            self.mark_as_visited(middle)
            self.active = next_cell
        else:
            if len(self.stack) == 0:
                return False
            self.active = self.stack.pop()
        return True

    def generate(self):
        while self.make_step():
            pass
        return self.labyrinth


def create_labyrinth(filename, preferred_width, preferred_height, k):
    """
    Запуск генерации
    :param filename: выходной файл
    :param preferred_width: желаемая ширина
    :param preferred_height: желаемая высота
    :param k: соотношение размера стен и свободных клеток
    """
    space_factor = 20
    wall_factor = math.ceil(k * space_factor)
    height = round(2 * (preferred_height - wall_factor)/(space_factor + wall_factor)) + 1
    width = round(2 * (preferred_width - wall_factor)/(space_factor + wall_factor)) + 1
    LabyrinthGenerator(width, height).generate().to_file(
        filename, space_factor, int(wall_factor))


if __name__ == '__main__':
    filename = easygui.filesavebox('Куда сохранять?', 'Генератор лабиринтов')
    width = height = easygui.integerbox('Желаемые размеры', 'Генератор лабиринтов', lowerbound=100, upperbound=1000)
    factor = float(easygui.enterbox('Отношение толщины стен к ширине прохода (float)',  'Генератор лабиринтов'))
    create_labyrinth(filename, width, height, factor)
