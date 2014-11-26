from taskmaster.process_tools.process_wrapper import ProcessWrapper
from taskmaster.process_tools.constants import StreamType
from tornado.ioloop import IOLoop
import time
import psutil


class ProcessManager(object):
    def __init__(self):
        current_time = round(IOLoop.instance().time(), 2)
        self.processes = {1: {'name': 'test print (3s)',
                              'arguments': ['python', '-c', 'import time; time.sleep(1); print("hello world"); time.sleep(1); print("goodbye world")'],
                              'process': None,
                              'status':  {'last_updated': current_time,
                                          'status': psutil.STATUS_DEAD}},
                          2: {'name': 'very long!',
                              'arguments': ['python', '-c', 'import time; time.sleep(5)'],
                              'process': None,
                              'status': {'last_updated': current_time,
                                         'status': psutil.STATUS_DEAD}}
                          }

        self.output_buffers = {process_id: {StreamType.Stdout: [], StreamType.Stderr: []} for process_id in self.processes.keys()}

    def start_process(self, process_index):
        if self.processes[process_index]['process'] is None:
            self.processes[process_index]['process'] = ProcessWrapper(process_index, self, self.processes[process_index]['arguments'])
            self.processes[process_index]['process'].start()

    def kill(self, process_index):
        if self.processes[process_index]['process'] is not None:
            self.processes[process_index]['process'].kill()

    def _write_output_to_handler(self, process_index, stream_type, stream_handler, last_retrieved_time):
        ready_to_write = [log for timestamp, log in self.output_buffers[process_index][stream_type] if timestamp > last_retrieved_time]

        if len(ready_to_write):
            stream_handler.handle_stream_output(max(self.output_buffers[process_index][stream_type])[0], ready_to_write)
        else:
            IOLoop.current().call_later(0.1, self._write_output_to_handler, *[process_index, stream_type, stream_handler, last_retrieved_time])

    def get_output(self, process_index, stream_type, stream_handler, last_retrieved_time):
        IOLoop.current().add_callback(self._write_output_to_handler, *[process_index, stream_type, stream_handler, last_retrieved_time])

    def _handle_process_output(self, process_index, output, stream_type):
        # TODO: Make cleaning up more robust. Right now if we write a bunch of logs in 59 seconds and no more they
        # stay forever.
        buffer_timeout = time.time() - 60
        self.output_buffers[process_index][stream_type] =\
            [(timestamp, log) for timestamp, log in self.output_buffers[process_index][stream_type] if timestamp >= buffer_timeout]

        self.output_buffers[process_index][stream_type].extend(output)

    def handle_output(self, process_index, output, stream_type):
        IOLoop.current().add_callback(self._handle_process_output, *[process_index, output, stream_type])

    def _write_status_to_handler(self, handler, last_retrieved_time):
        process_status = {}

        for process_index, process_info in self.processes.items():
            if process_info['status']['last_updated'] > last_retrieved_time:
                process_status[process_index] = process_info['status']

        if process_status != {}:
            most_recent_update = max([process_data['last_updated'] for process_data in process_status.values()])
            handler.handle_status_changes({'last_update_time': most_recent_update,
                                           'process_data': process_status})
        else:
            IOLoop.current().call_later(0.1, self._write_status_to_handler, *[handler, last_retrieved_time])

    def get_status(self, handler, last_retrieved_time):
        IOLoop.current().add_callback(self._write_status_to_handler, *[handler, last_retrieved_time])

    def _handle_status_change(self, process_id, change_time, new_status):
        if new_status != self.processes[process_id]['status']['status']:
            self.processes[process_id]['status']['last_updated'] = change_time
            self.processes[process_id]['status']['status'] = new_status

            if new_status == psutil.STATUS_DEAD:
                self.processes[process_id]['process'] = None

    def handle_status_change(self, process_id, change_time, new_status):
        IOLoop.current().add_callback(self._handle_status_change, *[process_id, change_time, new_status])


