from taskmaster.process_tools.process_wrapper import ProcessWrapper

class ProcessManager(object):
    def __init__(self):
        self.process_arguments = {1: ['python', '-c', 'import time; time.sleep(3); print("hello world")']}

        self.running_processes = {1: None}

    def start_process(self, process_id):
        if self.running_processes[process_id] is None:
            self.running_processes[process_id] = ProcessWrapper(self.process_arguments[process_id])
            self.running_processes[process_id].start()

    def get_output(self, process_id, stream_handler):
        if self.running_processes[process_id] is not None:
            self.running_processes[process_id].get_output(stream_handler)

