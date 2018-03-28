# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"Logging settings."

import logging

from lib import constants


def set_default_file_handler(logger, log_path, log_level=logging.DEBUG):
    """
 :type logger: logging.Logger
 :param log_path: str
 :param log_level: str
 """
    logger.setLevel(log_level)
    formatter = logging.Formatter(constants.log.FORMAT)
    fh = logging.FileHandler(filename=log_path, mode="w")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
