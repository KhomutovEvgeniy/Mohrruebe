import xmlrpc.client


def angleLimit(angle, value):  # устанавливаем максимально возможный угол на серве, который дальше будет
        #  изменяться в некотором диапазоне
        if value >= 90:
            angle = 90
        elif value <= - 90:
            angle = -90
        else:
            angle = value


class Robot:  # класс, переносящий ф-ии с робота на пульт
    def __init__(self):
        self._ip = None
        self._port = None
        self._proxy = None
        self._client = None
        self._motorSpeed = 0    # скорость, которую мы подаем на моторы

        self._camAngle = 0  # угол поворота сервы камеры
        self._stepAngleSrv = 10 # шаг изменения угла серв основания и кривошипа манипулятора
        self._baseAngle = 0     # углы поворота звеньев маипулятора
        self._crankAngle = 0
        self._rodAngle = 0
        self._graspAngle = 0
        self._movingReverse = -1

    def connect(self, ip, port):
        self._ip = ip
        self._port = port
        self._proxy = "http://" + ip + ':' + port
        self._client = xmlrpc.client.ServerProxy(self._proxy)

    def rotate(self, scale):  # scale - значение из диапазона (-1, 1) # поворачиваемся со скоростью
        # MotorSpeed*коэффициент scale
        self._client.rotate(int(scale * self._motorSpeed))

    def turnForward(self, scale):  # scale - значение из диапазона (-1, 1)
        # поворачиваем сервы передней части робота в зависимости от значения со стика
        self._client.turnForward(scale)

    def move(self, scale):  # scale - значение из диапазона (-1, 1) # движемся вперед со скоростью
        # MotorSpeed*коэффициент scale * (-1) - для реверса стика
        self._client.move(int(scale * self._motorSpeed) * self._movingReverse)

    def turnCam(self):
        self._client.turnCam(self._camAngle)    # self._camAngle - угол из диапазона (-90, 90)

    @property
    def online(self):  # создан ли клиент
        return bool(self._client)

    @property
    def motorSpeed(self):
        return self._motorSpeed

    @property
    def camAngle(self):
        return self._camAngle

    @motorSpeed.setter
    def motorSpeed(self, value):  # устанавливаем максимально возможную скорость движения,
        #  которая дальше будет изменяться в некотором диапазоне
        if value >= 100:
            self._motorSpeed = 100
        elif value <= - 100:
            self._motorSpeed = -100
        else:
            self._motorSpeed = value

    @camAngle.setter
    def camAngle(self, value):
        if value >= 90:
            self._camAngle = 90
        elif value <= -90:
            self._camAngle = -90
        else:
            self._camAngle = value


    """ управление манипулятором"""
    def defaultPosition(self):
        self._client.defaultPosition()

    def rotateBase(self, scale):  # scale - значение из диапазона (-1, 1) # изменение угла сервы на
        # шаг изменения угла * коэффициент scale
        self._baseAngle += int(self._stepAngleSrv * scale)
        self._client.rotateBase(self._baseAngle)

    def rotateCrank(self, scale):  # scale - значение из диапазона (-1, 1) # изменение угла сервы на
        # шаг изменения угла * коэффициент scale
        self._crankAngle += int(self._stepAngleSrv * scale)
        self._client.rotateCrank(self._crankAngle)

    def rotateRod(self):  # scale - угол из диапазона (-90, 90)
        self._client.rotateRod(self._rodAngle)  # self._rodAngle - угол из диапазона (-90, 90)

    def rotateGrasp(self):
        self._client.rotateGrasp(self._graspAngle)  # self._graspAngle - угол из диапазона (-90, 90)

    @property
    def baseAngle(self):
        return self._baseAngle

    @property
    def crankAngle(self):
        return self._crankAngle

    @property
    def rodAngle(self):
        return self._rodAngle

    @property
    def graspAngle(self):
        return self._graspAngle

    @baseAngle.setter
    def baseAngle(self, value):
        angleLimit(self._baseAngle, value)

    @crankAngle.setter
    def crankAngle(self, value):
        angleLimit(self._crankAngle, value)

    @rodAngle.setter
    def rodAngle(self, value):
        angleLimit(self._rodAngle, value)

    @graspAngle.setter
    def graspAngle(self, value):
        angleLimit(self._graspAngle, value)
