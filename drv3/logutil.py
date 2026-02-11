# -*- coding: utf-8 -*-

import logging
import os
import sys

ROOT_LOGGER_NAME = "drv3"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def setup_logging(log_file, console_level = logging.ERROR, file_level = logging.ERROR):
  logger = logging.getLogger(ROOT_LOGGER_NAME)
  logger.setLevel(logging.DEBUG)
  logger.propagate = False
  
  for handler in list(logger.handlers):
    logger.removeHandler(handler)
    handler.close()
  
  log_dir = os.path.dirname(log_file)
  if log_dir:
    os.makedirs(log_dir, exist_ok = True)
  
  formatter = logging.Formatter(LOG_FORMAT)
  
  console_handler = logging.StreamHandler(sys.stderr)
  console_handler.setLevel(console_level)
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  
  file_handler = logging.FileHandler(log_file, encoding = "utf-8")
  file_handler.setLevel(file_level)
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  
  return logger


def get_logger(name):
  if name.startswith(ROOT_LOGGER_NAME + "."):
    return logging.getLogger(name)
  
  if name == ROOT_LOGGER_NAME:
    return logging.getLogger(ROOT_LOGGER_NAME)
  
  return logging.getLogger("%s.%s" % (ROOT_LOGGER_NAME, name))


### EOF ###
