import logging
import importlib.machinery
import os


def verify_config(config_module):
    verified = True
    for i, process in enumerate(config_module.processes):
        process_name = None
        if not len(process.get('name', '')):
            logging.error('Process at index {} is missing a "name" entry!'.format(i))
            verified = False
        else:
            process_name = process.get('name')

        if not len(process.get('arguments', '')):
            if process_name is not None:
                logging.error('Process {} is missing arguments!'.format(process_name))
            else:
                logging.error('Process at index {} is missing arguments!'.format(i))
            verified = False
    return verified


def load_and_verify_config(config_file_path):
    if not os.path.exists(config_file_path):
        logging.error('Config file {} does not exist!'.format(config_file_path))
        return None
    else:
        path, file = os.path.split(config_file_path)

        loader = importlib.machinery.SourceFileLoader(file.replace('.py', ''), config_file_path)
        config = loader.load_module()

        if verify_config(config):
            return config
        else:
            return None