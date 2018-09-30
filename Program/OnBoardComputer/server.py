#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Сервер, установленный на малине """
from xmlrpc.server import SimpleXMLRPCServer
import subprocess

from config import *
# from config import *

cmd = 'hostname -I | cut -d\' \' -f1'
selfIP = subprocess.check_output(cmd, shell=True)     # получаем IP
selfIP.rstrip().decode("utf-8")     # удаляем \n, переводим в текст


server = SimpleXMLRPCServer((selfIP, RPCServerPort))

server.register_function(rotate)
server.register_function(turnForward)
server.register_function(turnBackside)
server.register_function(move)

server.register_function(defaultPosition)
server.register_function(rotateBase)
server.register_function(rotateCrank)
server.register_function(rotateRod)
server.register_function(rotateGrasp)

server.serve_forever()
