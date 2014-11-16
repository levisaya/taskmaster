import psutil
from subprocess import PIPE
from threading import Thread, Event
from tornado.ioloop import IOLoop, PeriodicCallback
from queue import Queue, Empty


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
                self.callback_queue.put(line)
        self.stopped.set()


class ProcessEventGenerator(object):
    def __init__(self, process, ioloop):
        self.process = process
        self.ioloop = ioloop

        self.stdout_queue = Queue()
        self.stderr_queue = Queue()

        self.stdout_reader = BlockingStreamReader(self.process.stdout, self.stdout_queue)
        self.stderr_reader = BlockingStreamReader(self.process.stderr, self.stderr_queue)
        self.stdout_reader.start()
        self.stderr_reader.start()

        self.ioloop.add_callback(self.performance_stats)
        self.ioloop.add_callback(self.read_stream, *[self.stdout_queue])
        self.ioloop.add_callback(self.read_stream, *[self.stderr_queue])

    def read_stream(self, output_queue):
        output = []

        try:
            while 1:
                output.append(output_queue.get_nowait())
        except Empty:
            pass

        if len(output):
            print('Stream output: {}'.format(output))
            self.ioloop.add_callback(self.read_stream, *[output_queue])
        else:
            self.ioloop.call_later(0.1, self.read_stream, *[output_queue])

    def performance_stats(self):
        try:
            print(self.process.cpu_percent(), self.process.memory_info())
            self.ioloop.call_later(0.5, self.performance_stats)
        except psutil.NoSuchProcess:
            print('Process Terminated')


class ProcessWrapper(object):
    def __init__(self, arglist, ioloop):
        self.arglist = arglist
        self.ioloop = ioloop
        self.process = None
        self.processor = None

    def start(self):
        self.process = psutil.Popen(self.arglist, stdout=PIPE, stderr=PIPE)

        # Required to give a baseline CPU usage.
        self.process.cpu_percent()
        self.processor = ProcessEventGenerator(self.process, self.ioloop)

    def process_running(self):
        if self.process is not None:
            return self.process.is_running()
        else:
            return False

    def wait(self):
        if self.process is not None:
            self.process.wait()
