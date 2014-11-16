import time
from tornado.ioloop import IOLoop
import unittest
from taskmaster.taskmaster_app.process_tools.process_wrapper import ProcessWrapper
from threading import Thread


class ProcessWrapperCase(unittest.TestCase):
    def setUp(self):
        self.ioloop_thread = Thread(target=IOLoop.instance().start)
        self.ioloop_thread.start()

    def tearDown(self):
        IOLoop.instance().stop()

    def test_resource_usage(self):
        process_wrapper = ProcessWrapper(["python", "test_resource_usage.py"], IOLoop.instance())
        process_wrapper.start()

        while process_wrapper.process_running():
            time.sleep(1)

if __name__ == '__main__':
    unittest.main()
