# -*- coding: utf-8 -*-

import datetime
import logging
import threading
import SocketServer

from lib.database import UrandomizationStorage


class UrandomServerHandler(SocketServer.BaseRequestHandler):

    block_size = 8192

    def setup(self):
        thread = threading.current_thread()
        self.logger = logging.getLogger('UrandomServerHandler(%s)' % thread.name)
        self.logger.info('new connection from %s' % str(self.client_address))

    def handle(self):
        data = self.request.recv(8192)
        self.logger.info('urandomization')
        self.request.sendall("HTTP/1.1 200 OK\r\n" +
                             "Content-Type: text/html\r\n" +
                             # "Content-Encoding: gzip\r\n" +
                             "Content-Length: 1000000000000\r\n" +
                             "Connection: keep-alive\r\n" +
                             "Server: Apache\r\n" +
                             "\r\n")
        # self.request.sendall("\x1f\x8b" + # magic number
        #                      "\x08" + # deflate
        #                      "\x00" + # flag
        #                      "\x00\x00\x00\x00" + # time
        #                      "\x02" + # extra flag
        #                      "\xff" # operating system
        #                      )
        start_time = datetime.datetime.now()
        byte_count = 0
        try:
            with open('/dev/urandom', 'rb') as urandom:
                while self.request.sendall(urandom.read(self.block_size)) is None:
                    byte_count += self.block_size
        except Exception as e:
            self.logger.exception(e)
            self.logger.info('stop urandomization')
        stop_time = datetime.datetime.now()
        storage = UrandomizationStorage()
        storage.put_urandomization(
                start_time=start_time,
                stop_time=stop_time,
                byte_count=byte_count,
                ip_address=self.client_address[0],
                port=self.client_address[1],
                data=data
            )
        self.request.close()
        self.logger.info('%s eats %d bytes in %s' % (
                str(self.client_address),
                byte_count,
                str(stop_time - start_time)
            )
        )


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class UrandomServer(object):

    def __init__(self, host, port):
        self.logger = logging.getLogger('UrandomServer')
        self.logger.debug('__init__(host=%s, port=%s)' % (host, port))
        self.server = ThreadedTCPServer((host, port), UrandomServerHandler)

    def start(self):
        self.logger.debug('start')
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        self.logger.debug('stop')
        self.server.shutdown()
        self.server.server_close()
