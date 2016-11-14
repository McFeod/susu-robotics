from time import time, sleep

import math
from pygame.threads import Thread

from robot_ai import RobotAI


class AIRunner:
    """
    Запуск AI в другом потоке
    """
    COORD_FACTOR = math.pi / 100
    POWER_FACTOR = 0.7
    SPEED_FACTOR = COORD_FACTOR / POWER_FACTOR

    def __init__(self, engine):
        self.engine = engine
        self.ai = RobotAI(self.engine.steps)
        self.thread = None
        self.stop_flag = False

    def run(self, time_measurement=1):
        def ai_loop():
            sensor_info = self.engine.get_sensor_info()
            default_sleep_time = time_measurement / self.engine.steps * self.SPEED_FACTOR
            while not (self.engine.win_condition or self.stop_flag):
                for i in range(self.engine.steps):
                    if self.engine.win_condition:
                        break
                    start = time()
                    self.engine.robot.set_power(*self.ai.get_next_power(
                        *sensor_info
                    ))
                    sensor_info = self.engine.move_robot()
                    sleep_time = default_sleep_time - (time() - start)
                    if sleep_time > 0:
                        sleep(sleep_time)

        self.thread = Thread(target=ai_loop)
        self.thread.start()

    def stop(self):
        self.stop_flag = True
