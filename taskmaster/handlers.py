import tornado.web
from mako.template import Template
from tornado.escape import to_unicode


class ProcessControlHandler(tornado.web.RequestHandler):
    def initialize(self, process_manager):
        self.process_manager = process_manager

    def post(self, process_index, command):
        if command == 'start':
            self.process_manager.start_process(int(process_index))
        elif command == 'kill':
            self.process_manager.kill(int(process_index))
        else:
            raise tornado.web.HTTPError(404)


class ProcessInfoHandler(tornado.web.RequestHandler):
    def initialize(self, process_info):
        self.process_info = process_info

    def get(self, process_index):
        process_info = self.process_info.get(int(process_index), None)

        if process_info is not None:
            self.write(process_info)
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

    def on_connection_close(self):
        self.process_manager.cancel_callbacks(self)


class StreamingLogHandler(tornado.web.RequestHandler):
    def initialize(self, logging_manager):
        self.logging_manager = logging_manager

    def handle_stream_output(self, process_index, last_output_time, time_index, stream_output_list):
        self.write({'process_index': process_index,
                    'last_output_time': last_output_time,
                    'time_index': time_index,
                    'output': [to_unicode(line) for _, _, line in stream_output_list]})
        self.finish()

    @tornado.web.asynchronous
    def get(self, process_index, last_time, time_index):
        self.logging_manager.get_output(int(process_index),
                                        self,
                                        float(last_time),
                                        int(time_index))

    def on_connection_close(self):
        self.logging_manager.cancel_callbacks(self)


class PageHandler(tornado.web.RequestHandler):
    def get(self):
        template = Template(filename='static/templates/main.html')
        self.write(template.render())