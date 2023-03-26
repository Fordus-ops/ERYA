# -*- coding: utf-8 -*"""
"""
Created on Mon Jan 23 09:59:05 2023

@author: R109449
"""
import sys
import os
import logging
from logging.handlers import QueueHandler
import multiprocessing
from PyQt5.QtWidgets import QApplication
import erya_gui
import erya_logger

if __name__ == '__main__':
    #Starts the app
    app = QApplication(sys.argv)

    #Multiprocessing shared queue for logging
    log_queue = multiprocessing.Queue()
    log_error_queue = multiprocessing.Queue()
    mod_error_queue = multiprocessing.Queue()

    #Logger that will be used in main process
    logger = logging.getLogger("ERYA_main")

    #Logger configuration
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(QueueHandler(log_queue))
    logger.setLevel(logging.INFO)

    #Starts the logger subprocess than will handle messages coming from all processes
    logger_process = multiprocessing.Process(target=erya_logger.logger_subprocess,
        args=(log_queue, log_error_queue, os.getcwd()))
    logger_process.start()

    #Ensures the logger is created properly
    error_message = log_error_queue.get(block=True, timeout=10)
    if error_message == "Error":
        erya_gui.error_window("Error when creating logger",
            "The program was unable to start the main logger")
        sys.exit()
    elif error_message == "OK":
        #Basic information to be logger
        logger.info("ERYA Tool® V0.1")
        logger.info("Main process PID %s",os.getpid())
        logger.info("Logger process PID %s",logger_process.pid)
    else:
        erya_gui.error_window("Timeout when creating logger",
            "The program was unable to start the main logger (Timeout)")
        sys.exit()
    
    #Starts the main window
    window = erya_gui.MainWindow(log_queue, logger_process, logger)
    window.show()

    #Exits the app
    sys.exit(app.exec_())
