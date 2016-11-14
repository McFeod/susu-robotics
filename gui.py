import pygame
from pgu import gui

from menu import MenuMixin


class DrawingArea(gui.Widget):
    """
    Виджет для лабиринта
    """
    def __init__(self, width, height):
        gui.Widget.__init__(self, width=width, height=height)
        self.imageBuffer = pygame.Surface((width, height))

    def paint(self, surface):
        surface.blit(self.imageBuffer, (0, 0))

    def save_background(self):
        surface = pygame.display.get_surface()
        self.imageBuffer.blit(surface, self.get_abs_rect())


class MainGui(gui.Desktop, MenuMixin):
    """
    Окно программы
    """
    menu_area_width = 200
    drawing_area = None
    menu_area = None
    engine = None

    def __init__(self, display):
        gui.Desktop.__init__(self)
        self.font = pygame.font.SysFont("Ubuntu", 16)

        self.drawing_area = DrawingArea(display.get_width() - self.menu_area_width,
                                        display.get_height())
        self.menu_area = gui.Container(width=self.menu_area_width)
        tbl = gui.Table(height=display.get_height())
        tbl.tr()
        tbl.td(self.drawing_area)
        tbl.td(self.menu_area)
        self.setup_menu()
        self.init(tbl, display)
        self.targeting_robot = False
        self.targeting_exit = False

        def set_element(_event, _widget, _code):
            if self.targeting_robot:
                self.engine.robot.robot.x = _event.pos[0]
                self.engine.robot.robot.y = self.engine.field_height() - _event.pos[1]
                self.engine.robot.robot.angle = 0
                self.engine.robot.transform(True)
                if self.engine.robot.collides(self.engine.labyrinth):
                    self.engine.robot.robot.x = -1000
                    self.engine.robot.transform()
                else:
                    self.targeting_robot = False
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
            elif self.targeting_exit:
                self.engine.exit.rect.center = _event.pos
                if pygame.sprite.collide_mask(self.engine.exit, self.engine.labyrinth) is not None:
                    self.engine.exit.rect.center = (-1000, -1000)
                else:
                    self.targeting_exit = False
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
        self.drawing_area.connect(gui.CLICK, set_element)

    def load_file(self, filename):
        self.engine.load_labyrinth(filename)

    def change_engine_power(self, left, right):
        self.engine.robot.set_power(left, right)

    def move_robot(self):
        self.engine.move_robot()

    def open(self, dialog, position=None):
        """
        Открытие диалога и приостановка отрисовки лабиринта
        :param dialog:
        :param position:
        :return:
        """
        rect = self.drawing_area.get_abs_rect()
        dark = pygame.Surface(rect.size).convert_alpha()
        dark.fill((0, 0, 0, 150))
        pygame.display.get_surface().blit(dark, rect)
        self.drawing_area.save_background()
        running = not self.engine.clock.paused
        self.engine.pause()
        gui.Desktop.open(self, dialog, position)
        while dialog.is_open():
            for ev in pygame.event.get():
                self.event(ev)
            rects = self.update()
            if rects:
                pygame.display.update(rects)
        if running:
            self.engine.resume()

    def get_render_area(self):
        return self.drawing_area.get_abs_rect()

    def reset_robot(self):
        self.targeting_robot = True
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    def reset_exit(self):
        self.targeting_exit = True
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    def run_ai(self):
        self.engine.run_ai()

    def stop_ai(self):
        self.engine.ai.stop()

    def move_robot_to_start(self):
        self.engine.robot.robot.x, self.engine.robot.robot.y = \
            map(lambda x: x*self.engine.factor, self.engine.robot_start)
        self.engine.robot.robot.angle = 0
        self.engine.robot.transform(True)

    def open_win_dialog(self):
        dialog = gui.Dialog(gui.Label('Выход найден', font=self.font), gui.Image('bender.png'))
        gui.Desktop.open(self, dialog)
