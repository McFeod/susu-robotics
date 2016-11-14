import pygame
from pgu import gui


class MenuMixin:
    """
    Разметка меню, установка коллбэков
    """
    font = None

    def setup_menu(self, panel_width=200):

        tbl = gui.Table(vpadding=5, hpadding=2)

        tbl.tr()
        container = gui.Container()
        button = gui.Button('~', font=self.font, width=20, height=40)
        button.connect(gui.CLICK, self.move_robot_to_start)
        container.add(button, 0, 0)
        button = gui.Button('Поставить робота', font=self.font, width=100, height=40)
        button.connect(gui.CLICK, self.reset_robot)
        container.add(button, 40, 0)
        tbl.td(container)

        tbl.tr()
        tbl.td(gui.Spacer(0, 20))


        tbl.tr()
        button = gui.Button('Задать выход', font=self.font, width=100, height=40)
        tbl.td(button)
        button.connect(gui.CLICK, self.reset_exit)

        tbl.tr()
        tbl.td(gui.Spacer(0, 20))


        tbl.tr()
        tbl.td(self.setup_file_dialog(panel_width), valign=-1)

        tbl.tr()
        tbl.td(self.setup_sliders(), align=-1)

        tbl.tr()
        button = gui.Button('Шаг', font=self.font, width=100, height=40)
        tbl.td(button)

        button.connect(gui.CLICK, self.move_robot)

        tbl.tr()
        tbl.td(gui.Spacer(height=20, width=panel_width))

        tbl.tr()
        button = gui.Button('Запуск AI', font=self.font, width=100, height=40)
        tbl.td(button)

        button.connect(gui.CLICK, self.run_ai)

        tbl.tr()
        tbl.td(gui.Spacer(height=20, width=panel_width))

        tbl.tr()
        button = gui.Button('Остановка AI', font=self.font, width=100, height=40)
        tbl.td(button)

        button.connect(gui.CLICK, self.stop_ai)

        self.menu_area.add(tbl, 0, 0)

    def setup_file_dialog(self, panel_width):

        def open_file_browser(arg):
            dialog = gui.FileDialog()
            dialog.connect(gui.CHANGE, handle_file_browser_closed, dialog)
            self.open(dialog)

        def handle_file_browser_closed(dlg):
            if dlg.value:
                input_file.value = dlg.value
                self.load_file(dlg.value)

        table = gui.Table()
        table.tr()
        table.td(gui.Label('Лабиринт:', font=self.font), align=-1)
        input_file = gui.Input(font=self.font)
        table.tr()
        table.td(input_file)
        button = gui.Button('Файл...', font=self.font)
        table.tr()
        table.td(button, align=1)
        table.tr()
        table.td(gui.Spacer(height=20, width=panel_width))
        button.connect(gui.CLICK, open_file_browser, None)
        return table

    def setup_sliders(self):
        table = gui.Table()
        table.tr()
        table.td(gui.Label('Двигатели:', font=self.font), align=-1)
        self.left_engine_slider = gui.VSlider(value=0, min=-100, max=100, size=10, width=16, height=200)
        self.right_engine_slider = gui.VSlider(value=0, min=-100, max=100, size=10, width=16, height=200)

        table.tr()
        container = gui.Container()
        table.td(container)

        left_input = gui.Input('0', font=self.font, size=4)
        right_input = gui.Input('0', font=self.font, size=4)

        def sliders_changed():
            left_input.value = str(-self.left_engine_slider.value)
            right_input.value = str(-self.right_engine_slider.value)
            self.change_engine_power(
                -self.left_engine_slider.value,
                -self.right_engine_slider.value
            )

        def inputs_changed():
            try:
                left = int(left_input.value)
                right = int(right_input.value)
                if abs(left) <= 100 and abs(right) <=100:
                    self.left_engine_slider.value = -left
                    self.right_engine_slider.value = -right
                    self.change_engine_power(left, right)
            except:
                pass

        self.left_engine_slider.connect(gui.CHANGE, sliders_changed)
        self.right_engine_slider.connect(gui.CHANGE, sliders_changed)
        left_input.connect(gui.KEYDOWN, inputs_changed)
        right_input.connect(gui.KEYDOWN, inputs_changed)

        lt = gui.Table(width=35)
        lt.tr()
        lt.td(left_input, align=1)
        gt = gui.Table()
        gt.tr()
        gt.td(right_input, align=-1)
        container.add(left_input, 20, 90)
        container.add(self.left_engine_slider, 70, 0)
        container.add(self.right_engine_slider, 120, 0)
        container.add(right_input, 140, 90)

        table.tr()
        table.td(gui.Spacer(height=20, width=0))
        return table
