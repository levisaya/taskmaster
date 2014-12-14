__author__ = 'Andy'

import logging
from tornado.ioloop import IOLoop
from taskmaster.process_logging.timed_buffer_handler import TimedBufferHandler


class LoggingManager(object):
    def __init__(self, logging_config, log_cleanup_timeout=30):
        self.log_cleanup_timeout = log_cleanup_timeout

        self.buffer_handlers = {}

        self.disconnected_handlers = []

        for process_index, logging_configuration in logging_config.items():
            logger = logging.getLogger('taskmaster.processes.{}'.format(process_index))

            logger.setLevel(logging_configuration.get('level', logging.INFO))

            self.buffer_handlers[process_index] = TimedBufferHandler(level=logging_configuration.get('level',
                                                                                                     logging.INFO))

            logger.addHandler(self.buffer_handlers[process_index])

            for additional_handler in logging_configuration.get('handlers', []):
                logger.addHandler(additional_handler)

        IOLoop.current().call_later(self.log_cleanup_timeout, self._remove_old_logs)

    def cancel_callbacks(self, handler):
        self.disconnected_handlers.append(handler)

    def _remove_old_logs(self):
        """
        Removes all logs from the in-memory buffer that are older than the configured log_cleanup_timeout.
        """
        old_time = round(IOLoop.instance().time(), 2) - self.log_cleanup_timeout

        for buffer_handler in self.buffer_handlers.values():
            buffer_handler.clean_buffer(old_time)

        IOLoop.current().call_later(self.log_cleanup_timeout, self._remove_old_logs)

    def _write_output_to_handler(self, process_index, handler, last_retrieved_time, time_index):
        if handler not in self.disconnected_handlers:
            ready_to_write = self.buffer_handlers[process_index].get_from_buffer(last_retrieved_time, time_index)
            if len(ready_to_write):
                handler.handle_stream_output(process_index,
                                             round(ready_to_write[-1][0], 2),
                                             ready_to_write[-1][1],
                                             ready_to_write)
            else:
                IOLoop.current().call_later(0.5,
                                            self._write_output_to_handler,
                                            *[process_index,
                                              handler,
                                              last_retrieved_time,
                                              time_index])
        else:
            self.disconnected_handlers.remove(handler)

    def get_output(self, process_index, handler, last_retrieved_time, time_index):
        IOLoop.current().add_callback(self._write_output_to_handler,
                                      *[process_index,
                                        handler,
                                        last_retrieved_time,
                                        time_index])