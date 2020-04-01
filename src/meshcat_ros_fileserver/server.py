#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import os
import sys

import tornado.web
import tornado.ioloop

if sys.version_info >= (3, 0):
    ADDRESS_IN_USE_ERROR = OSError
else:
    import socket
    ADDRESS_IN_USE_ERROR = socket.error

import mimetypes
from mimetypes import guess_type

MAX_ATTEMPTS = 1000
DEFAULT_FILESERVER_PORT = 9000
KNOWN_TYPES = ['stl', 'obj', 'dae', 'png', 'bmp', 'jpeg', 'jpg', 'mtl', 'xml', 'xacro', 'urdf']
ORIGIN = "*"

def find_available_port(func, default_port, max_attempts=MAX_ATTEMPTS):
    for i in range(max_attempts):
        port = default_port + i
        try:
            return func(port), port
        except (ADDRESS_IN_USE_ERROR, zmq.error.ZMQError):
            print("Port: {:d} in use, trying another...".format(port), file=sys.stderr)
        except Exception as e:
            print(type(e))
            raise
    else:
        raise(Exception("Could not find an available port in the range: [{:d}, {:d})".format(default_port, max_attempts + default_port)))


class FileHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", ORIGIN)

    def initialize(self, root):
        self.root = root
        mimetypes.add_type("model/vnd.collada+xml", ".dae")
        mimetypes.add_type("text/plain", ".mtl")
        mimetypes.add_type("text/xml", ".xacro")
        mimetypes.add_type("text/xml", ".urdf")

    def get(self, path_in):
        if path_in[0] == '/':
            path = path_in[1:]
        else:
            path = path_in
        file_location = os.path.join(self.root, path)
        filename, file_extension = os.path.splitext(path)
        if any(ext == file_extension.lower() for ext in KNOWN_TYPES):
            raise tornado.web.HTTPError(status_code=403)
        if not os.path.isfile(file_location):
            raise tornado.web.HTTPError(status_code=404)
        content_type, _ = guess_type(file_location)
        self.add_header('Content-Type', content_type)
        with open(file_location, "rb") as source_file:
            self.write(source_file.read())

class FileServer(object):

    def __init__(self, host="127.0.0.1", port=None, path_root=None):
        self.host = host
        self.websocket_pool = set()
        if path_root is None:
            self.path_root = None
        else:
            self.path_root = path_root
            print("Enabling file service with root at '" + self.path_root + "'")
            print("Allowed file extensions: ", KNOWN_TYPES)
            print("Allowing file requests from: '" + ORIGIN + "'")
        self.app = self.make_app()
        self.ioloop = tornado.ioloop.IOLoop.current()
        if port is None:
            _, self.fileserver_port = find_available_port(self.app.listen, DEFAULT_FILESERVER_PORT)
        else:
            self.app.listen(port)
            self.fileserver_port = port
        self.file_url = "http://{host}:{port}/files/".format(host=self.host, port=self.fileserver_port)

    def make_app(self):
        handlers = []
        handlers.append((r"/files/(.*)", FileHandler, {"root": self.path_root}))
        return tornado.web.Application(handlers)

    def run(self):
        self.ioloop.start()

def main():
    global ORIGIN
    import argparse

    parser = argparse.ArgumentParser(description="Serves the ROS files over HTTP")
    parser.add_argument('--file-root', '-f', type=str, nargs="?", default=None)
    parser.add_argument('--port', '-p', type=str, nargs="?", default=DEFAULT_FILESERVER_PORT)
    parser.add_argument('--origin', '-o', type=str, nargs="?", default="*")
    results = parser.parse_args()
    if results.file_root is None:
        print('Please provide a file root!')
        parser.print_usage()
        exit(1)
    ORIGIN = results.origin
    server = FileServer(port = results.port, path_root = results.file_root)
    print("file_url={:s}".format(server.file_url))

    try:
        server.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()