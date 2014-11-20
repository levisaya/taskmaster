import psutil
from subprocess import PIPE
from threading import Thread, Event
from tornado.ioloop import IOLoop
from queue import Queue, Empty
import time
from taskmaster.process_tools.constants import StreamType


class BlockingStreamReader(Thread):
    def __init__(self, stream, callback_queue):
        Thread.__init__(self)
        self.stream = stream
        self.callback_queue = callback_queue
        self.stopping = Event()
        self.stopped = Event()

    def stop(self):
        self.stopping.set()
        self.stopped.wait()

    def run(self):
        while not self.stopping.is_set():
            line = self.stream.readline()
            if not len(line):
                break
            else:
                self.callback_queue.put((time.time(), line))
        self.stopped.set()


class ProcessEventGenerator(object):
    def __init__(self, process_id, process, process_manager, ioloop):
        self.process_id = process_id
        self.process = process
        self.process_manager = process_manager
        self.ioloop = ioloop

        self.stdout_queue = Queue()
        self.stderr_queue = Queue()

        self.stdout_reader = BlockingStreamReader(self.process.stdout, self.stdout_queue)
        self.stderr_reader = BlockingStreamReader(self.process.stderr, self.stderr_queue)
        self.stdout_reader.start()
        self.stderr_reader.start()

        self.ioloop.add_callback(self.performance_stats)
        self.ioloop.add_callback(self.read_stream, *[self.stdout_queue, StreamType.Stdout])
        self.ioloop.add_callback(self.read_stream, *[self.stderr_queue, StreamType.Stderr])

    def read_stream(self, output_queue, stream_type):
        output = []

        try:
            while 1:
                output.append(output_queue.get_nowait())
        except Empty:
            pass

        if len(output):
            self.process_manager.handle_output(self.process_id, output, stream_type)

            self.ioloop.add_callback(self.read_stream, *[output_queue, stream_type])
        else:
            self.ioloop.call_later(0.1, self.read_stream, *[output_queue, stream_type])

    def performance_stats(self):
        try:
            print(self.process.status())
            self.process_manager.handle_status_change(self.process_id, self.ioloop.time(), self.process.status())

            self.ioloop.call_later(0.5, self.performance_stats)
        except psutil.NoSuchProcess:
            self.process_manager.handle_status_change(self.process_id, self.ioloop.time(), psutil.STATUS_DEAD)
            print('Process Terminated')


class ProcessWrapper(object):
    def __init__(self, process_id, process_manager, arglist, ioloop=IOLoop.instance()):
        self.process_id = process_id
        self.process_manager = process_manager
        self.arglist = arglist
        self.ioloop = ioloop
        self.process = None
        self.processor = None

    def start(self):
        self.process = psutil.Popen(self.arglist, stdout=PIPE, stderr=PIPE)

        # Required to give a baseline CPU usage.
        self.process.cpu_percent()
        self.processor = ProcessEventGenerator(self.process_id, self.process, self.process_manager, self.ioloop)

    def process_running(self):
        if self.process is not None:
            return self.process.is_running()
        else:
            return False

    def kill(self):
        if self.process is not None:
            print('Killing {}'.format(self.process_id))
            self.process.kill()


