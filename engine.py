import pygame
from pgu import timer

from ai_runner import AIRunner
from gui import MainGui

from labyrinth_loader import load_labyrinth
from sprite import RobotSprite, ExitSprite, LeftSensor, RightSensor


class GraphicEngine(object):
    """
    Графический движок на базе pygame
    """
    def __init__(self, screen):
        self.steps = 30
        self.win_condition = False
        self.ai = AIRunner(self)
        self.display = screen
        self.app = MainGui(self.display)
        self.field_width = lambda: screen.get_width() - self.app.menu_area_width
        self.field_height = screen.get_height
        self.load_labyrinth('empty.txt')
        self.app.engine = self

    def get_sensor_info(self):
        return (self.left_sensor.get_distance(self.robot.robot, self.labyrinth.mask),
                self.right_sensor.get_distance(self.robot.robot, self.labyrinth.mask))

    def pause(self):
        self.clock.pause()

    def resume(self):
        self.clock.resume()

    def set_sprites(self, labyrinth, factor, robot_pos):
        self.ai.stop()
        self.win_condition = False
        self.robot_start = robot_pos
        self.factor = factor
        self.labyrinth = labyrinth
        self.lab_group = pygame.sprite.GroupSingle(labyrinth)
        self.robot = RobotSprite(factor, self.robot_start[0], self.robot_start[1], self.field_height())
        self.exit = ExitSprite(factor)
        self.left_sensor = LeftSensor(self.factor, self.field_height())
        self.right_sensor = RightSensor(self.factor, self.field_height())
        self.robot.add_sensor(self.left_sensor)
        self.robot.add_sensor(self.right_sensor)
        self.sprites = pygame.sprite.Group()
        self.sprites.add(self.robot)
        self.sprites.add(self.exit)
        self.sprites.add(self.left_sensor)
        self.sprites.add(self.right_sensor)

    def load_labyrinth(self, filename):
        """
        Загрузка лабиринта из файла
        :param filename:
        :return:
        """
        self.set_sprites(*load_labyrinth(filename, self.field_width(), self.field_height()))
        self.robot.transform(True)

    def render(self, dest, rect):
        dest.fill((255, 255, 255), rect)
        self.lab_group.draw(dest)
        self.sprites.draw(dest)
        return (rect,)

    def move_robot(self):
        self.robot.make_step(self.labyrinth, self.factor/self.steps)
        if pygame.sprite.collide_mask(self.robot, self.exit):
            self.win_condition = True
            self.app.open_win_dialog()
        return self.get_sensor_info()

    def run_ai(self):
        self.ai = AIRunner(self)
        self.ai.run()

    def run(self):
        """
        Цикл отрисовки
        :return:
        """
        self.app.update()
        pygame.display.flip()
        self.font = self.app.font
        self.clock = timer.Clock()
        done = False
        # self.ai.run()
        while not done:
            for ev in pygame.event.get():
                if (ev.type == pygame.QUIT or
                        ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    done = True
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    for _ in range(self.steps):
                        self.move_robot()
                else:
                    self.app.event(ev)
            rect = self.app.get_render_area()
            updates = []
            self.display.set_clip(rect)
            try:
                lst = self.render(self.display, rect)
            except pygame.error:
                lst = None
            if lst:
                updates += lst
            self.display.set_clip()

            self.clock.tick(30)

            lst = self.app.update()
            if lst:
                updates += lst
            pygame.display.update(updates)
            pygame.time.wait(10)
        self.ai.stop()
