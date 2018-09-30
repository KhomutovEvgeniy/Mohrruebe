""" Конфигурация робота """
# from RPiPWM import *

from OnBoardComputer.RPiPWM import *

"""
    F   - Front
    B   - Backside
    L   - Left
    R   - Right
    BOF -  Base of manipulator
    COF -  Crank of manipulator
    ROF -  Rod of manipulator
    GOF -  Grasp of manipulator
"""
IP = '173.1.0.78'  # IP адрес куда отправляем видео
RPCServerPort = 8000  # порт RPC сервера

chanSvrCAM = 5  # канал для сервы с камерой
chanSvrFR = 8  # канал для передней правой сервы
chanSrvFL = 9  # канал для передней левой сервы
chanSrvBR = 10  # канал для задней правой сервы
chanSrvBL = 11  # канал для задней левой сервы

chanSrvBOF =   # канал для сервы основания манипулятора
chanSrvCOF =  # канал для сервы кривошипа манипулятора
chanSrvROF =   # канал для сервы шатуна манипулятор
chanSrvGOF =   # канал для сервы схвата манипулятора
#   TODO: указать каналы для серв манипулятора
chanRevMotorsLB = 14  # канал драйвера левого борта моторов
chanRevMotorsRB = 15  # канал драйвера правого борта моторов

servoResolutionDeg = -90, 90    # разрешение с центром в нуле
servoResolutionMcs = 800, 2200
# TODO: определить экспериментально угол, задающийся ниже
rotateAngle =      # угол в градусах, на который надо повернуть сервы, чтобы робот крутился на месте
# для квадратных роботов это 45 градусов

defaultBaseAngle = 0 # углы в градусах, соответствующие начальным положениям серв манипулятора в сложенном виде
defaultCrankAngle = 0 # TODO: Проверить углы серв (что все ок и ничто никуда не упирается), соответствующие манипулятору в сложенном виде
defaultRodAngle = 0
defaultGraspAngle = 0

# TODO: спросить у Вити, поч можно создать серву270, хотя диапазон опр-ся как 180
SvrFL = Servo270(chanSrvFL)  # передняя левая
SvrFR = Servo270(chanSvrFR)  # передняя правая
SvrBL = Servo270(chanSrvBL)  # задняя левая
SvrBR = Servo270(chanSrvBR)  # задняя правая

SvrBOF = Servo270(chanSrvBOF)  # основание манипулятора
SvrCOF = Servo270(chanSrvCOF)  # кривошип манипулятора
SvrROF = Servo270(chanSrvROF)  # шатун манипулятор
SvrGOF = Servo270(chanSrvGOF)  # схват манипулятора

MotorLB = ReverseMotor(chanRevMotorsLB)  # моторы, индексы аналогичные
MotorRB = ReverseMotor(chanRevMotorsRB)


def servoScale(value):  # рескейлим серву, как нам нужно
    degRange = (servoResolutionDeg[1] - servoResolutionDeg[0])
    mskRange = (servoResolutionMcs[1] - servoResolutionMcs[0])
    result = ((value - servoResolutionDeg[0])/degRange) * mskRange + servoResolutionMcs[0]
    if result > servoResolutionMcs[1]:
        return servoResolutionMcs[1]
    elif result < servoResolutionMcs[0]:
        return servoResolutionMcs[0]
    else:
        return int(result)


def turnServo(servo, scale):
    """ поворот заданной сервы """
    result = servoScale(scale)
    servo.SetMcs(result)
    return True


def turnAllSrv():
    """ поворот всех серв на один угол для разворота на месте"""
    turnServo(SvrFL, rotateAngle)
    turnServo(SvrFR, -rotateAngle)
    turnServo(SvrBL, -rotateAngle)
    turnServo(SvrBR, rotateAngle)
    return True


def rotate(speed):
    """ поворот на месте по(против) часовой стрелке(и), speed - скорость поворота """
    turnAllSrv()
    MotorRB.SetValue(speed)
    MotorLB.SetValue(speed)
    return True


def turnForward(scale):
    """ поворот передней части робота """
    turnServo(SvrFL, scale * 90)
    turnServo(SvrFR, scale * 90)
    return True
# TODO: turnBack пока не используется


def turnBackside(scale):
    """ поворот задней части робота """
    turnServo(SvrBL, scale * 90)
    turnServo(SvrBR, scale * 90)
    return True


def move(speed):
    """ движение вперед/назад """
    MotorLB.SetValue(-speed)
    MotorRB.SetValue(speed)
    return True


""" управление манипулятором"""
def defaultPosition():
    """ установка манипулятора в сложенное состояние(компактное) """
    turnServo(SvrBOF, defaultBaseAngle)
    turnServo(SvrBOF, defaultCrankAngle)
    turnServo(SvrBOF, defaultRodAngle)
    turnServo(SvrBOF, defaultGraspAngle)
    return True


def rotateBase(scale):
    """ поворот основания манипулятора"""
    turnServo(SvrBOF, scale)
    return  True


def rotateCrank(scale):
    """ поворот кривошипа манипулятора"""
    turnServo(SvrCOF, scale)
    return  True


def rotateRod(scale):
    """ поворот шатуна манипулятора"""
    turnServo(SvrCOF, scale)
    return  True
