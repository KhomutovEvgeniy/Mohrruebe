import gi
import sys
import numpy
from RTCException import *

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject


class CVGstreamer:
    def __init__(self, IP='127.0.0.1', RTP_RECV_PORT=5000, RTCP_RECV_PORT=5001, RTCP_SEND_PORT=5005,
                 codec="JPEG", toAVS=False):  # ip и порты по умолчанию + кодек jpeg и h264
        self.cvImage = None  # Изображение, полученное из openCV
        Gst.init(sys.argv)  # Инициализация компонентов
        GObject.threads_init()
        self.codec = codec  # используемый кодек

        if self.codec == "JPEG":
            self.VIDEO_CAPS = 'application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)JPEG,' \
                              'payload=(int)26,ssrc=(uint)1006979985,clock-base=(uint)312170047,seqnum-base=(uint)3174'
            # caps приема
        elif self.codec == "H264":
            self.VIDEO_CAPS = "application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(" \
                              "string)H264,payload=(int)96"  # caps приема
        else:
            raise RTCCodecError(self.codec, "такого кодека нет")

        self.IP = IP  # ip приема
        self.RTP_RECV_PORT0 = RTP_RECV_PORT  # Порты приема
        self.RTCP_RECV_PORT0 = RTCP_RECV_PORT  #
        self.RTCP_SEND_PORT0 = RTCP_SEND_PORT  #
        self.player = None  # pipeline
        self.toAVS = toAVS  # Флаг, означающий, что видео будет стримится в auto video sink

    def playPipe(self):
        self.initElements()  # инициализация компонентов
        self.linkElements()  # линковка
        self.player.set_state(Gst.State.READY)
        self.player.set_state(Gst.State.PAUSED)
        self.player.set_state(Gst.State.PLAYING)

    def start(self):  # Запуск видео
        if not self.player:  # если не создан pipeline
            self.playPipe()  # запустить pipeline
        else:
            state = self.player.get_state(Gst.CLOCK_TIME_NONE).state  # текущее состояние pipeline
            if state == Gst.State.PAUSED:  # если перед этим была вызвана пауза
                self.player.set_state(Gst.State.PLAYING)
            elif state == Gst.State.PLAYING:  # если видос уже запущен
                raise RTCPipelineError("Нельзя повторно запустить видео")
            else:  # если перед этим было вызвано stop
                self.playPipe()  # запустить pipeline

    def paused(self):  # пауза
        if self.player:
            if ((
                    self.player.get_state(
                        Gst.CLOCK_TIME_NONE).state) == Gst.State.NULL):  # если перед этим было вызвано stop
                raise RTCPipelineError("Нельзя поставить на паузу освобожденные ресурсы")
            else:
                self.player.set_state(Gst.State.PAUSED)

    def stop(self):  # остановка и освобождение ресурсов
        if self.player:
            self.player.set_state(Gst.State.NULL)
            self.cvImage = None

    def on_error(self, bus, msg):  # прием ошибок
        err, dbg = msg.parse_error()
        print("ERROR:", msg.src.get_name(), ":", err.message)  # нужно ли тут вообще исключение?
        if dbg:
            print("Debug info:", dbg)

    def on_eos(self, bus, msg):  # ловим конец передачи видео
        print("End-Of-Stream reached")
        self.player.set_state(Gst.State.READY)

    def initElements(self):  # инициализация компонентов
        self.player = Gst.Pipeline.new("player")  # создаем pipeline
        if not self.player:
            raise RTCInternalError("player", "Не получается создать объект pipeline")

        self.bus = self.player.get_bus()  # создаем шину передачи сообщений и ошибок от GST
        self.bus.add_signal_watch()
        self.bus.connect("message::error", self.on_error)
        self.bus.connect("message::eos", self.on_eos)

        """ VIDEODEPAY """
        self.videodepay0 = None

        if self.codec == "JPEG":
            self.videodepay0 = Gst.ElementFactory.make('rtpjpegdepay',
                                                       'videodepay0')  # создаем раскпаковщик видео формата jpeg

        elif self.codec == "H264":
            self.videodepay0 = Gst.ElementFactory.make('rtph264depay',
                                                       'videodepay0')  # создаем раскпаковщик видео формата h264
        else:
            raise RTCCodecError(self.codec, "такого кодека нет")

        if not self.videodepay0:
            raise RTCInternalError("videodepay0", "Не получается создать объект videodepay")

        """ SOURCE """
        self.rtpbin = Gst.ElementFactory.make('rtpbin', 'rtpbin')  # создаем rtpbin
        self.player.add(self.rtpbin)  # добавляем его в Pipeline
        self.caps = Gst.caps_from_string(self.VIDEO_CAPS)  # в каком формате принимать видео

        """ дальше идет очень странная система RTP """

        def pad_added_cb(rtpbin, new_pad, depay):
            sinkpad = Gst.Element.get_static_pad(depay, 'sink')
            lres = Gst.Pad.link(new_pad, sinkpad)

        self.rtpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtpsrc0')
        self.rtpsrc0.set_property('port', self.RTP_RECV_PORT0)

        """ we need to set caps on the udpsrc for the RTP data """
        self.rtpsrc0.set_property('caps', self.caps)

        self.rtcpsrc0 = Gst.ElementFactory.make('udpsrc', 'rtcpsrc0')
        self.rtcpsrc0.set_property('port', self.RTCP_RECV_PORT0)

        self.rtcpsink0 = Gst.ElementFactory.make('udpsink', 'rtcpsink0')
        self.rtcpsink0.set_property('port', self.RTCP_SEND_PORT0)
        self.rtcpsink0.set_property('host', self.IP)

        """ no need for synchronisation or preroll on the RTCP sink """
        self.rtcpsink0.set_property('async', False)
        self.rtcpsink0.set_property('sync', False)
        self.player.add(self.rtpsrc0, self.rtcpsrc0, self.rtcpsink0)

        self.srcpad0 = Gst.Element.get_static_pad(self.rtpsrc0, 'src')

        self.sinkpad0 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtp_sink_0')
        self.lres0 = Gst.Pad.link(self.srcpad0, self.sinkpad0)

        """ get an RTCP sinkpad in session 0 """
        self.srcpad0 = Gst.Element.get_static_pad(self.rtcpsrc0, 'src')
        self.sinkpad0 = Gst.Element.get_request_pad(self.rtpbin, 'recv_rtcp_sink_0')
        self.lres0 = Gst.Pad.link(self.srcpad0, self.sinkpad0)

        """ get an RTCP srcpad for sending RTCP back to the sender """
        self.srcpad0 = Gst.Element.get_request_pad(self.rtpbin, 'send_rtcp_src_0')
        self.sinkpad0 = Gst.Element.get_static_pad(self.rtcpsink0, 'sink')
        self.lres0 = Gst.Pad.link(self.srcpad0, self.sinkpad0)

        self.rtpbin.set_property('drop-on-latency', True)
        self.rtpbin.set_property('buffer-mode', 1)

        self.rtpbin.connect('pad-added', pad_added_cb, self.videodepay0)

        """ DECODER """
        self.decoder0 = None

        if self.codec == "JPEG":
            self.decoder0 = Gst.ElementFactory.make('jpegdec', "decoder0")

        elif self.codec == "H264":
            self.decoder0 = Gst.ElementFactory.make('avdec_h264', "decoder0")  # декодирует h264 формат

        else:
            raise RTCCodecError(self.codec, "такого кодека нет")

        if not self.decoder0:
            raise RTCInternalError("decoder0", "Не получается создать объект decoder")

        """ VIDEOCONVERT """
        self.videoconvert0 = Gst.ElementFactory.make("videoconvert", "videoconvert0")
        if not self.videoconvert0:
            raise RTCInternalError("videoconvert0", "Не получается создать объект videoconvert")

        """ CAPS AND SINK """
        if self.toAVS:  # если приемник autovideosink
            self.sink = Gst.ElementFactory.make("autovideosink", "sink")
            if not self.sink:
                raise RTCInternalError("sink", "Не получается создать объект sink")

        else:  # если приемник app sink
            def gst_to_opencv(sample):  # создаем матрицу пикселей
                buf = sample.get_buffer()
                caps = sample.get_caps()
                arr = numpy.ndarray(
                    (caps.get_structure(0).get_value('height'),
                     caps.get_structure(0).get_value('width'),
                     3),
                    buffer=buf.extract_dup(0, buf.get_size()),
                    dtype=numpy.uint8)
                return arr

            def new_buffer(sink, data):  # callback функция, исполняющаяся при каждом приходящем кадре
                sample = sink.emit("pull-sample")
                arr = gst_to_opencv(sample)
                self.cvImage = arr  # openCV image
                return Gst.FlowReturn.OK

            """ создаем свой sink для перевода из GST в CV """
            self.sink = Gst.ElementFactory.make("appsink", "sink")
            if not self.sink:
                raise RTCInternalError("sink", "Не получается создать объект sink")

            caps = Gst.caps_from_string("video/x-raw, format=(string){BGR, GRAY8}")  # формат приема sink'a
            self.sink.set_property("caps", caps)

            self.sink.set_property("emit-signals", True)
            self.sink.connect("new-sample", new_buffer, self.sink)

        """ VIDEOSCALE """
        self.videoscale0 = Gst.ElementFactory.make("videoscale", "videoscale0")  # растягиваем изображение
        if not self.videoscale0:
            raise RTCInternalError("videoscale0", "Не получается создать объект videoscale")

        self.player.add(self.videodepay0)  # добавляем все элементы в pipeline
        self.player.add(self.decoder0)
        self.player.add(self.videoscale0)
        self.player.add(self.videoconvert0)
        self.player.add(self.sink)

    def linkElements(self):  # функция линковки элементов
        link_ok = self.videodepay0.link(self.decoder0)
        if not link_ok:
            raise RTCLinkError("videodepay0", "decoder0")

        link_ok = self.decoder0.link(self.videoconvert0)
        if not link_ok:
            raise RTCLinkError("decoder0", "videoconvert0")

        link_ok = self.videoconvert0.link(self.videoscale0)
        if not link_ok:
            raise RTCLinkError("videoconvert0", "videoscale0")

        link_ok = self.videoscale0.link(self.sink)
        if not link_ok:
            raise RTCLinkError("videoscale0", "sink")

    def toAppSink(self):  # переводит изображение в AppSink
        if self.toAVS:
            self.toAVS = False
            self.stop()
            self.start()

    def toAutoVideoSink(self):  # переводит изображение в auto video sink
        if not self.toAVS:
            self.toAVS = True
            self.stop()
            self.start()

