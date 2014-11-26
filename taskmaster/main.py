import tornado.ioloop
import tornado.web
from tornado.escape import to_unicode
from taskmaster.process_tools.process_manager import ProcessManager
from taskmaster.process_tools.constants import StreamType
from mako.template import Template


class ProcessControlHandler(tornado.web.RequestHandler):
    def initialize(self, process_manager):
        self.process_manager = process_manager

    def post(self, process_id, command):
        if command == 'start':
            self.process_manager.start_process(int(process_id))
        elif command == 'kill':
            self.process_manager.kill(int(process_id))
        else:
            raise tornado.web.HTTPError(404)


class ProcessStatusHandler(tornado.web.RequestHandler):
    def initialize(self, process_manager):
        self.process_manager = process_manager

    def handle_status_changes(self, changes):
        self.write(changes)
        self.finish()

    @tornado.web.asynchronous
    def get(self, last_time):
        self.process_manager.get_status(self, float(last_time))


class StreamingLogHandler(tornado.web.RequestHandler):
    def initialize(self, process_manager):
        self.process_manager = process_manager

    def handle_stream_output(self, last_output_time, stream_output_list):
        self.write({'last_output_time': last_output_time,
                    'output': [to_unicode(line) for line in stream_output_list]})
        self.finish()

    @tornado.web.asynchronous
    def get(self, process_id, stream_type, last_time):
        self.process_manager.get_output(int(process_id),
                                        StreamType(int(stream_type)),
                                        self,
                                        float(last_time))


class PageHandler(tornado.web.RequestHandler):
    def get(self):
        template = Template(filename='static/templates/main.html')
        self.write(template.render())

if __name__ == "__main__":
    process_manager = ProcessManager()

    application = tornado.web.Application([
        (r"/", PageHandler),
        (r"/process/([0-9]+)/(.+)", ProcessControlHandler, dict(process_manager=process_manager)),
        (r"/process_status/([0-9]+.[0-9]+)", ProcessStatusHandler, dict(process_manager=process_manager)),
        (r"/logs/streaming/([0-9]+)/([0-9]+)/([0-9]+.[0-9]+)", StreamingLogHandler, dict(process_manager=process_manager)),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()