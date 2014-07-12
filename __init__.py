import tornado
import tornado.websocket
import tornado.autoreload
import tornado.httpserver
import sys
import time
import json


def log(op, message):
    print '[%d] [%s] %s' % (time.time(), op, message)


# thanks, aaron swartz
class Storage(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'


def to_storage(obj):
    if isinstance(obj, dict):
        return Storage((k, to_storage(v)) for k, v in obj.iteritems())
    if isinstance(obj, list):
        return [to_storage(x) for x in obj]
    return obj


class GameHandler:
    def __init__(self, routes, ns):
        self._ns = ns
        self._handlers = {}

        pool = list(routes)
        while pool:
            self._handlers[pool.pop()] = pool.pop()

    def handle(self, op, client, data=None):
        log(op, data)
        if op in self._handlers:
            self._ns[self._handlers[op]](client, data or {})


class GameClient(tornado.websocket.WebSocketHandler):
    def initialize(self, routes, ns):
        self._handler = GameHandler(routes, ns)

    def __init__(self, *args, **kwargs):
        super(GameClient, self).__init__(*args, **kwargs)
        self.s = Storage()

    def open(self):
        self._handler.handle('_open', self)

    def write(self, obj):
        message = json.dumps(obj)
        return self.write_message(message)

    def send(self, op, **kwargs):
      kwargs['op'] = op
      return self.write(kwargs)

    def error(self, error, op=None):
        if op is None:
            return self.write({'error': error})
        return self.send(op, error=error)

    def on_message(self, message):
        try:
            data = to_storage(json.loads(message))
            op = data.op
            del data.op

            self._handler.handle(op, self, data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error(str(e))

    def on_close(self):
        self._handler.handle('_close', self)


class Application:
    def __init__(self, ns, *routes):
        kwargs = {'routes': routes, 'ns': ns}
        self._app = tornado.web.Application([('/', GameClient, kwargs)])

    def run(self, port):
        server = tornado.httpserver.HTTPServer(self._app)
        server.listen(port)

        ioloop = tornado.ioloop.IOLoop.instance()
        tornado.autoreload.start(ioloop)
        ioloop.start()
