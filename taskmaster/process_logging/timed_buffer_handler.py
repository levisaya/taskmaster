__author__ = 'Andy'

from logging import Handler, NOTSET


class TimedBufferHandler(Handler):
    def __init__(self, level=NOTSET):
        Handler.__init__(self, level)

        self.buffer = []

    def emit(self, record):
        """
        Handle a log coming off a process.
        Enqueue it in the buffer so clients can retrieve it.
        :param record:
        :return:
        """

        index_for_time = 0
        timestamp = round(record.created, 2)
        if len(self.buffer):
            if self.buffer[-1][0] == timestamp:
                index_for_time = self.buffer[-1][1] + 1

        self.buffer.append((timestamp, index_for_time, record.msg))

    def get_from_buffer(self, most_recent_log, index_for_time):
        print('getting logs: {} {}'.format(most_recent_log, index_for_time))
        return [log for log in self.buffer if log[0] > most_recent_log or (log[0] == most_recent_log and log[1] > index_for_time)]

    def clean_buffer(self, oldest_log_time):
        if len(self.buffer) and min(self.buffer)[0] < oldest_log_time:
            self.buffer = [(timestamp, index_for_time, line) for timestamp, index_for_time, line in self.buffer if timestamp >= oldest_log_time]