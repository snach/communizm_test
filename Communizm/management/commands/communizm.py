# coding: utf-8

import SocketServer
import struct
import threading
import sys


COMMUNIZM_HOST = 'localhost'
COMMUNIZM_PORT = 38202



class CommUnizmRequestHandler(SocketServer.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def parse(self, data):
        protocol = struct.unpack_from('!B', data)[0]

        if protocol == 1:
            p = struct.unpack('!BBIiih8s', data)
            #self.server.proc.debug('recv()->"%s"', p)
        elif protocol == 2:
            p = None
        else:
            p = None

        return protocol, p

    def response(self, protocol):
        if protocol == 1:
            received_status = 2
            urgency = 1
            data = u'''Test message
with
разделителем строк'''.encode('utf-8')
            msglen = len(data)
            fmt = '!BBI{}s'.format(msglen)
        else:
            received_status = 0
            urgency = 0
            data = 'Protocol does not exist'
            msglen = len(data)
            fmt = '!BBI{}s'.format(msglen)

        return struct.pack(fmt, received_status, urgency, msglen, data)

    def handle(self):
        data = self.request.recv(1024)

        #self.server.proc.debug('recv()->"%s"', data)

        protocol, p = self.parse(data)

        protocol, event_type, event_time, latitude, longitude, altitude, userkey = p
        latitude *= 0.0000001
        longitude *= 0.0000001

        msg = dict(event_type=12, time=event_time, lat=latitude, lon=longitude, height=altitude, control_id=userkey)

        print msg
        #print self.response(protocol)

        self.request.send(self.response(protocol))


class CommUnizmServer(SocketServer.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, handler_class=CommUnizmRequestHandler, proc=None):
        print '__init__'

        SocketServer.TCPServer.__init__(self, server_address, handler_class, bind_and_activate=True)

    def server_activate(self):
        print 'server_activate'

        SocketServer.TCPServer.server_activate(self)

    def serve_forever(self, *args, **kwargs):
        print 'Waiting for request %s, %s' % (args, kwargs)

        while True:
            self.handle_request()


class CommThreads(threading.Thread):
    def __init__(self):
        self.server = None
        threading.Thread.__init__(self)

    def run(self):
        if self.server == None:
            self.server = CommUnizmServer((COMMUNIZM_HOST, COMMUNIZM_PORT), CommUnizmRequestHandler, proc=self)
        self.server.serve_forever()


from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        stdin = options.get('stdin', sys.stdin)
        print stdin
        thr = CommThreads()
        thr.setDaemon(True)
        thr.start()
        while True:
            pass
