import tornado.ioloop
import tornado.web
from taskmaster.process_tools.process_manager import ProcessManager
from taskmaster.process_logging.logging_manager import LoggingManager
import argparse
from taskmaster.config_utils import load_and_verify_config, parse_config
import logging
from taskmaster.handlers import PageHandler, ProcessControlHandler, ProcessStatusHandler, ProcessInfoHandler, StreamingLogHandler


def main(config_file):
    config = load_and_verify_config(config_file)

    if config is None:
        logging.error('Failed to get the config, exiting.')
    else:
        logging_configuration, process_info, process_args = parse_config(config)

        logging_manager = LoggingManager(logging_configuration)

        process_manager = ProcessManager(process_args)

        application = tornado.web.Application([
            (r"/", PageHandler),
            (r"/process/([0-9]+)/(.+)", ProcessControlHandler, dict(process_manager=process_manager)),
            (r"/process_status/([0-9]+.[0-9]+)", ProcessStatusHandler, dict(process_manager=process_manager)),
            (r"/process_info/([0-9]+)", ProcessInfoHandler, dict(process_info=process_info)),
            (r"/logs/streaming/([0-9]+)/([0-9]+.[0-9]+)/([0-9]+)",
             StreamingLogHandler,
             dict(logging_manager=logging_manager)),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
        ])

        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-config-file', '-c', dest='config_file', type=str, required=True, help='Path to the config file')

    args = parser.parse_args()
    main(args.config_file)