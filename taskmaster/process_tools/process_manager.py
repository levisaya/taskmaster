from taskmaster.process_tools.process_wrapper import ProcessWrapper
from tornado.ioloop import IOLoop
import psutil


class ProcessManager(object):
    def __init__(self, process_args):
        current_time = round(IOLoop.instance().time(), 2)

        self.processes = {}
        self.process_status = {}
        for process_index, process_arglist in process_args.items():
            self.processes[process_index] = ProcessWrapper(process_index, self, process_arglist)
            self.process_status[process_index] = {'last_updated': current_time,
                                                  'status': psutil.STATUS_DEAD}

        self.disconnected_handlers = []

    def cancel_callbacks(self, handler):
        self.disconnected_handlers.append(handler)

    def start_process(self, process_index):
        if self.processes[process_index].get_status() == psutil.STATUS_DEAD:
            self.process_status[process_index] = {'last_updated': round(IOLoop.instance().time(), 2),
                                                  'status': 'starting'}
            self.processes[process_index].start()

    def kill(self, process_index):
        if self.processes[process_index].get_status() != psutil.STATUS_DEAD:
            self.processes[process_index].kill()

    def _write_status_to_handler(self, handler, last_retrieved_time):
        if handler not in self.disconnected_handlers:
            new_process_status = {}

            for process_index, process_status in self.process_status.items():
                if process_status['last_updated'] > last_retrieved_time:
                    new_process_status[process_index] = process_status

            if new_process_status != {}:
                most_recent_update = max([process_data['last_updated'] for process_data in new_process_status.values()])
                handler.handle_status_changes({'last_update_time': most_recent_update,
                                               'process_data': new_process_status})
            else:
                IOLoop.current().call_later(0.1, self._write_status_to_handler, *[handler, last_retrieved_time])
        else:
            self.disconnected_handlers.remove(handler)

    def get_status(self, handler, last_retrieved_time):
        IOLoop.current().add_callback(self._write_status_to_handler, *[handler, last_retrieved_time])

    def _handle_status_change(self, process_id, change_time, new_status):
        if new_status != self.process_status[process_id]['status']:
            self.process_status[process_id]['last_updated'] = change_time
            self.process_status[process_id]['status'] = new_status

    def handle_status_change(self, process_id, change_time, new_status):
        IOLoop.current().add_callback(self._handle_status_change, *[process_id, change_time, new_status])


