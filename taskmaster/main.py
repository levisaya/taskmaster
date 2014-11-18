import tornado.ioloop
import tornado.web
from tornado.escape import to_unicode
from process_tools.process_manager import ProcessManager


class ProcessStartHandler(tornado.web.RequestHandler):
    def initialize(self, process_manager):
        self.process_manager = process_manager

    def post(self, process_id):
        self.process_manager.start_process(int(process_id))


class StreamingLogHandler(tornado.web.RequestHandler):
    def initialize(self, process_manager):
        self.process_manager = process_manager

    def handle_stream_output(self, stream_output_list):
        self.write({'output': [to_unicode(line) for line in stream_output_list]})
        self.finish()

    @tornado.web.asynchronous
    def get(self, process_id):
        self.process_manager.get_output(int(process_id), self)


if __name__ == "__main__":
    process_manager = ProcessManager()

    application = tornado.web.Application([
        (r"/process/([0-9]+)/start", ProcessStartHandler, dict(process_manager=process_manager)),
        (r"/logs/streaming/([0-9]+)", StreamingLogHandler, dict(process_manager=process_manager)),
    ])

    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()