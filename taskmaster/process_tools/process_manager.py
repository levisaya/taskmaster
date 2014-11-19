from taskmaster.process_tools.process_wrapper import ProcessWrapper
from taskmaster.process_tools.constants import ProcessState, StreamType
from tornado.ioloop import IOLoop
import time


class ProcessManager(object):
    def __init__(self):
        self.processes = {1: {'name': 'test print (3s)',
                              'arguments': ['python', '-c', 'import time; time.sleep(1); print("hello world"); time.sleep(1); print("goodbye world")'],
                              'state': ProcessState.NotRunning,
                              'process': None}}

        self.output_buffers = {process_id: {StreamType.Stdout: [], StreamType.Stderr: []} for process_id in self.processes.keys()}

    def start_process(self, process_id):
        if self.processes[process_id]['process'] is None:
            self.processes[process_id]['process'] = ProcessWrapper(process_id, self, self.processes[process_id]['arguments'])
            self.processes[process_id]['process'].start()

    def send_signal(self, process_id, signal):
        pass

    def _write_output_to_handler(self, process_id, stream_type, stream_handler, last_retrieved_time):
        ready_to_write = [log for timestamp, log in self.output_buffers[process_id][stream_type] if timestamp > last_retrieved_time]

        if len(ready_to_write):
            stream_handler.handle_stream_output(max(self.output_buffers[process_id][stream_type])[0], ready_to_write)
        else:
            IOLoop.current().call_later(0.1, self._write_output_to_handler, *[process_id, stream_type, stream_handler, last_retrieved_time])

    def get_output(self, process_id, stream_type, stream_handler, last_retrieved_time):
        IOLoop.current().add_callback(self._write_output_to_handler, *[process_id, stream_type, stream_handler, last_retrieved_time])

    def _handle_process_output(self, process_id, output, stream_type):
        buffer_timeout = time.time() - 60
        self.output_buffers[process_id][stream_type] =\
            [(timestamp, log) for timestamp, log in self.output_buffers[process_id][stream_type] if timestamp >= buffer_timeout]

        self.output_buffers[process_id][stream_type].extend(output)

    def handle_output(self, process_id, output, stream_type):
        IOLoop.current().add_callback(self._handle_process_output, *[process_id, output, stream_type])




