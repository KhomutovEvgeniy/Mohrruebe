class RTCBaseError(Exception):
    """Базовый класс ошибки для модулей
    Аттрибуты:
        expression -- выражение в котором произошла ошибка
        message -- объясниние ошибки"""

    def __init__(self, expr, msg):
        if msg is None:
            msg = "Произошла ошибка в %s" % expr
        super(RTCBaseError, self).__init__(msg)
        self.expression = expr
        self.message = msg


class RTCInternalError(RTCBaseError):
    """Исключение вызывается из-за внутренней ошибки программы"""

    def __init__(self, expr, msg):
        super(RTCInternalError, self).__init__(expr, "Внутренняя ошибка программы в " + expr + ", по причине: " + msg)


class RTCCodecError(RTCBaseError):
    """Исключение вызывается в случае ошибки кодека
    Аттрибуты:
        codec -- кодек из-за которого произошла ошибка
        остальное наследуется из базового класса"""

    def __init__(self, codec, msg):
        super(RTCCodecError, self).__init__(None, codec + ": " + msg)
        self.expression = None
        self.codec = codec
        self.message = msg


class RTCPipelineError(RTCBaseError):
    """Исключение вызывается в случае ошибки pipeline
    Аттрибуты:
        наследуются из базового класса"""

    def __init__(self, msg):
        super(RTCPipelineError, self).__init__(None, msg)
        self.expression = None


class RTCLinkError(RTCBaseError):
    """Исключение вызывается в случае ошибки линковки
    Аттрибуты:
        targetlink -- первый объект линковки
        linkto -- второй объект линковки"""

    def __init__(self, targetlink, linkto):
        super(RTCLinkError, self).__init__(None, "Не получается линковать объект " + targetlink + " с объектом " + linkto)
        self.expression = None
        self.targetlink = targetlink
        self.linkto = linkto


class RTCJoyCrashError(RTCBaseError):
    """Исключение вызывается в случае, когда крашнулся джойстик
    Аттрибуты:
        наследуются из базового класса"""

    def __init__(self, msg):
        super(RTCJoyCrashError, self).__init__(None, msg)
        self.expression = None


class RTCJoyNotFoundError(RTCBaseError):
    """Исключение вызывается в случае, когда указанный джойстик не найден
    Аттрибуты:
        jName -- имя ненайденного джойстика
        остальное наследуется из базового класса"""

    def __init__(self, jName, msg):
        super(RTCJoyNotFoundError, self).__init__(None, jName + ": " + msg)
        self.expression = None
        self.jName = jName
        self.message = msg


class RTCButtonError(RTCBaseError):
    """Исключение, которое вызывается, когда указанной кнопки на джойстике не существует
    Аттрибуты:
        bName -- имя несуществующей кнопки
        остальное наследуется из базового класса"""

    def __init__(self, bName, msg):
        super(RTCButtonError, self).__init__(None, bName + ": " + msg)
        self.expression = None
        self.bName = bName
        self.message = msg

"""
raise RTCInternalError("туть", "кривые руки")

try:
    raise RTCInternalError("туть", "кривые руки")
except InternalError as e:
    print(e.expression)
"""
