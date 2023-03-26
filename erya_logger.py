# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 16:42:10 2023

@author: R109449
"""
import sys
import os
import time
import logging
from logging.handlers import QueueHandler


def logger_subprocess(log_queue: QueueHandler,
        log_error_queue: QueueHandler, current_directory: str):
    """
    Logger subprocess that will manage logging in file for all processes.

    Parameters
    ----------
    log_queue : logging.QueueHandler()
        Shared logging queue.
    log_file_directory : str
        Logging directory path.

    Returns
    -------
    None.

    """
    try:
        # Main logger creation and basic configuration
        logging.basicConfig(level=logging.NOTSET)
        logger = logging.getLogger('ERYA_logger')
        if logger.hasHandlers():
            logger.handlers.clear()

        #File configuration handler configuration
        logfile = current_directory+os.sep+"log"+os.sep+str(time.time())+".log"
        file_handler = logging.FileHandler(logfile)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        log_error_queue.put("OK")
        logger.info("Logger process activated successfully")
        #Run forever until finish message arrives
        while True:
            # consume a log message, block until one arrives
            message = log_queue.get()
            # check for shutdown
            if message is None:
                break
            # log the message
            logger.handle(message)

    except OSError:
        log_error_queue.put("Error")
        logging.shutdown()
        sys.exit()
