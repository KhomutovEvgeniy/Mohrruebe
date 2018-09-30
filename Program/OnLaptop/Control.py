""" Модуль описывающий управление роботом """
import Robot
import threading
import time
from config import *


class Control (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.robot = Robot.Robot()
        self._joystick = None
        self._EXIT = False

    def setJoystick(self, joystick):  # устанавливаем джойстик, которым будем управлять
        self._joystick = joystick
        self.connectHandlers()

    def run(self):
        while not self._EXIT:
            try:
                # если клиент и джойстик созданы и нет разворота на месте
                if self.robot.online and (self._joystick is not None):
                    if self._joystick.Buttons.get(TURN_CLOCKWISE_BUTTON) == 0 and \
                            self._joystick.Buttons.get(TURN_COUNTERCLOCKWISE_BUTTON) == 0:

                        self.robot.turnForward(self._joystick.Axis.get(
                            TURN_FORWARD_STICK))  # поворот передней части робота

                        if self._joystick.Buttons.get(FORWARD_BUTTON) == 0 and \
                                self._joystick.Buttons.get(BACK_BUTTON) == 0:  # если нет движения вперед/назад

                            self.robot.move(self._joystick.Axis.get(MOVE_STICK))  # движение вперед/назад по стику
                        self.robot.rotateBase(
                            self._joystick.Axis.get(TURN_BASE_STICK))  # поворот основания манипулятора
                        self.robot.rotateCrank(
                            self._joystick.Axis.get(TURN_CRANK_STICK))  # поворот кривошипа манипулятора
            except:
                pass
            time.sleep(SEND_DELAY)

    def connectHandlers(self):  # привязка обработчиков кнопок
        def addSpeed():
            self.robot.motorSpeed += SPEED_CHANGE_STEP  # прибавляем скорость

        def subSpeed():
            self.robot.motorSpeed -= SPEED_CHANGE_STEP  # уменьшаем скорость

        def turnClockWise():
            self.robot.rotate(self.robot.motorSpeed)

        def turnCounterClockWise():
            self.robot.rotate(-self.robot.motorSpeed)

        def move(direction):
            self.robot.move(direction)

        """ управление манипулятором"""

        def defaultPosition():
            self.robot.defaultPosition()

        def rotateRod(direction):   # TODO: Возможно для шатуна и схвата шаг изменения угла записать в отдельную переменную
            self.robot.rodAngle += direction * self.robot._stepAngleSrv
            self.robot.rotateRod()

        def rotateGrasp(direction):
            self.robot.graspAngle += direction * self.robot._stepAngleSrv
            self.robot.rotateGrasp()

        self._joystick.connectButton(ADD_SPEED_BUTTON, addSpeed)
        self._joystick.connectButton(SUB_SPEED_BUTTON, subSpeed)
        self._joystick.connectButton(TURN_CLOCKWISE_BUTTON,
                                     turnClockWise())  # поворот на месте по часовой стрелке
        self._joystick.connectButton(TURN_COUNTERCLOCKWISE_BUTTON,
                                     turnCounterClockWise())  # поворот на месте против часовой стрелки
        self._joystick.connectButton(TURN_CLOCKWISE_BUTTON,
                                     turnClockWise())  # поворот на месте по часовой стрелке
        self._joystick.connectButton(FORWARD_BUTTON,
                                     move(MOVING_FORWARD))  # движение вперед
        self._joystick.connectButton(BACK_BUTTON,
                                     move(MOVING_BACK))  # движение назад

        """Привязка кнопок по управлению манипулятором"""
        self._joystick.connectButton(SET_MANIPULATOR_BUTTON, defaultPosition())
        self._joystick.connectButton(ROD_UP_BUTTON, rotateRod(TURN_UP_ROD))
        self._joystick.connectButton(ROD_DOWN_BUTTON, rotateRod(TURN_DOWN_ROD))
        self._joystick.connectButton(TONG_GRASP_BUTTON, rotateGrasp(TONG_GRASP))
        self._joystick.connectButton(UNCLASP_GRASP_BUTTON, rotateGrasp(UNCLASP_GRASP))

    def exit(self):
        self._EXIT = True
