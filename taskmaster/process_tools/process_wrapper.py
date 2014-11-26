import psutil
from subprocess import PIPE
from threading import Thread, Event
from tornado.ioloop import IOLoop
from queue import Queue, Empty
import time
from taskmaster.process_tools.constants import StreamType


class BlockingStreamReader(Thread):
    """
    Thread to read the blocking output stream from a spawned process.
    Usually there are two BlockingStreamReaders created, one for stdout, one for stderr.
    """

    def __init__(self, stream, callback_queue):
        """
        :param stream: Reference to the stdout/stderr file object obtained from the Popen object.
        :param callback_queue: Queue to place the read text lines onto.
        """
        Thread.__init__(self)
        self.stream = stream
        self.callback_queue = callback_queue

    def run(self):
        """
        Read text off the stream until EOF.
        Note that we manually flush the streams in ProcessEventGenerator to trigger EOF.
        """
        while True:
            line = self.stream.readline()
            if not len(line):
                # EOF, stop!
                break
            else:
                # Put the text on the queue, along with the time it was read.
                self.callback_queue.put((round(time.time(), 2), line))


class ProcessEventGenerator(object):
    """
    One ProcessEventGenerator is created per process.
    It performs two functions:
    1. Periodically retrieve buffered stdout and stderr text and pass it out to the ProcessManager for retrieval by
       clients.
    2. Periodically poll process status/statistics and pass them out to the ProcessManager for retrieval by clients.
    """

    def __init__(self, process_index, process, process_manager, ioloop=IOLoop.instance()):
        """
        :param process_index: The integer identifier used to identify the unique process in the ProcessManager.
        :param process: The psutil.Popen object wrapping the process.
        :param process_manager: Reference to the ProcessManager instance.
        :param ioloop: Tornado IOLoop instance used to schedule callbacks.
        """
        self.process_index = process_index
        self.process = process
        self.process_manager = process_manager
        self.ioloop = ioloop

        # These queues will have the text output of the process placed on them by the BlockingStreamReader threads.
        self.stdout_queue = Queue()
        self.stderr_queue = Queue()

        # Create and start the BlockingStreamReader threads.
        # These will read their given stream until EOF, then politely die.
        self.stdout_reader = BlockingStreamReader(self.process.stdout, self.stdout_queue)
        self.stderr_reader = BlockingStreamReader(self.process.stderr, self.stderr_queue)
        self.stdout_reader.start()
        self.stderr_reader.start()

        # Place the initial callbacks on the event loop.
        # All of these will reschedule themselves for as long as the process exists.
        self.ioloop.add_callback(self.performance_stats)
        self.ioloop.add_callback(self.read_stream, *[self.stdout_queue, StreamType.Stdout])
        self.ioloop.add_callback(self.read_stream, *[self.stderr_queue, StreamType.Stderr])

    def read_stream(self, output_queue, stream_type):
        """
        Read the buffered output of one of the output streams from the process and pass it to the ProcessManager.
        Consumes the queue filled by the BlockingStreamReader thread.
        :param output_queue: The Queue containing the process output.
        :param stream_type: Enum indicating if we are reading stdout or stderr. Used to separate the output in the
                            ProcessManager.
        """
        output = []

        # Get all available output off the queue.
        try:
            while 1:
                output.append(output_queue.get_nowait())
        except Empty:
            pass

        # If we read any output, toss it out to the ProcessManager
        if len(output):
            self.process_manager.handle_output(self.process_index, output, stream_type)

        # Get the current status to determine if we should try to read more or stop.
        current_status = psutil.STATUS_DEAD
        try:
            current_status = self.process.status()
        except psutil.NoSuchProcess:
            pass

        if current_status != psutil.STATUS_DEAD:
            # Process still alive, schedule the call to read more output.
            self.ioloop.call_later(0.1, self.read_stream, *[output_queue, stream_type])
        else:
            # Process has died. Flush the iostreams so the BlockingStreamReader triggers one last time and
            # nicely exits.
            self.process.stdout.flush()
            self.process.stderr.flush()

    def performance_stats(self):
        """
        TODO- Finish this, read more status off of the process (CPU/Memory usage, etc)
        """
        current_status = psutil.STATUS_DEAD
        try:
            current_status = self.process.status()
        except psutil.NoSuchProcess:
            pass

        self.process_manager.handle_status_change(self.process_index, round(self.ioloop.time(), 2), current_status)

        if current_status != psutil.STATUS_DEAD:
            self.ioloop.call_later(0.5, self.performance_stats)


class ProcessWrapper(object):
    def __init__(self, process_id, process_manager, arglist, ioloop=IOLoop.instance()):
        self.process_id = process_id
        self.process_manager = process_manager
        self.arglist = arglist
        self.ioloop = ioloop
        self.process = None
        self.processor = None

    def start(self):
        self.process = psutil.Popen(self.arglist, stdout=PIPE, stderr=PIPE, bufsize=1)

        # Quote from the psutil docs:
        # "Warning: the first time this function is called with interval = 0.0 or None it will return a meaningless 0.0 value which you are supposed to ignore."
        # Lets get that bogus value out of the way.
        self.process.cpu_percent(interval=None)

        # Start reading process output and status and passing it to the ProcessManager.
        self.processor = ProcessEventGenerator(self.process_id, self.process, self.process_manager, self.ioloop)


    def kill(self):
        if self.process is not None:
            print('Killing {}'.format(self.process_id))
            self.process.kill()


