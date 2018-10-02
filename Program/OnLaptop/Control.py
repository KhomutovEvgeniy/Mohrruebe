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
                    if self._joystick.Axis.get(ROTATE_STICK) * 100 == 0
                        self.robot.turnForward(self._joystick.Axis.get(
                            TURN_FORWARD_STICK))  # поворот передней части робота

                        self.robot.move(self._joystick.Axis.get(
                            MOVE_STICK_CROSS))  # движение вперед/назад по стику-кресту
                        self.robot.move(self._joystick.Axis.get(MOVE_STICK))  # движение вперед/назад по стику
                        self.robot.rotateBase(
                            self._joystick.Axis.get(TURN_BASE_STICK))  # поворот основания манипулятора
                        self.robot.rotateCrank(
                            self._joystick.Axis.get(TURN_CRANK_STICK))  # поворот кривошипа манипулятора
                    else
                        self.robot.rotate(ROTATE_STICK)
            except:
                pass
            time.sleep(SEND_DELAY)

    def connectHandlers(self):  # привязка обработчиков кнопок
        def addSpeed():
            self.robot.motorSpeed += SPEED_CHANGE_STEP  # прибавляем скорость

        def subSpeed():
            self.robot.motorSpeed -= SPEED_CHANGE_STEP  # уменьшаем скорость

        def turnUpCam(move):
            self.robot.camAngle += move * self.robot._stepAngleSrv
            self.robot.camAngle()

        """ управление манипулятором"""
        def defaultPosition():
            self.robot.defaultPosition()

        def rotateRod(move):   # TODO: Возможно для шатуна и схвата шаг изменения угла записать в отдельную переменную
            self.robot.rodAngle += move * self.robot._stepAngleSrv
            self.robot.rotateRod()

        def rotateGrasp(move):
            self.robot.graspAngle += move * self.robot._stepAngleSrv
            self.robot.rotateGrasp()


        self._joystick.connectButton(CAM_UP_BUTTON, turnUpCam(CAM_UP))
        self._joystick.connectButton(CAM_DOWN_BUTTON, turnUpCam(CAM_DOWN))
        self._joystick.connectButton(ADD_SPEED_BUTTON, addSpeed)
        self._joystick.connectButton(SUB_SPEED_BUTTON, subSpeed)
        # TODO: Добавить функцию для включения автономки
        self._joystick.connectButton(SET_AUTO_BUTTON, setAutoButton())

        """Привязка кнопок по управлению манипулятором"""
        self._joystick.connectButton(SET_MANIPULATOR_BUTTON, defaultPosition())
        self._joystick.connectButton(ROD_UP_BUTTON, rotateRod(ROD_UP))
        self._joystick.connectButton(ROD_DOWN_BUTTON, rotateRod(ROD_DOWN))
        self._joystick.connectButton(TONG_GRASP_BUTTON, rotateGrasp(TONG_GRASP))
        self._joystick.connectButton(UNCLASP_GRASP_BUTTON, rotateGrasp(UNCLASP_GRASP))

    def exit(self):
        self._EXIT = True
