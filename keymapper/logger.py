#!/usr/bin/python3
# -*- coding: utf-8 -*-
# key-mapper - GUI for device specific keyboard mappings
# Copyright (C) 2020 sezanzeb <proxima@hip70890b.de>
#
# This file is part of key-mapper.
#
# key-mapper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# key-mapper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with key-mapper.  If not, see <https://www.gnu.org/licenses/>.


"""Logging setup for key-mapper."""


import os
import time
import logging
import pkg_resources


SPAM = 5


def spam(self, message, *args, **kwargs):
    """Log a more-verbose message than debug."""
    # pylint: disable=protected-access
    if self.isEnabledFor(SPAM):
        # https://stackoverflow.com/a/13638084
        self._log(SPAM, message, args, **kwargs)


logging.addLevelName(SPAM, "SPAM")
logging.Logger.spam = spam

start = time.time()


class Formatter(logging.Formatter):
    """Overwritten Formatter to print nicer logs."""
    def format(self, record):
        """Overwritten format function."""
        # pylint: disable=protected-access
        debug = is_debug()
        if record.levelno == logging.INFO and not debug:
            # if not launched with --debug, then don't print "INFO:"
            self._style._fmt = '%(message)s'
        else:
            # see https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
            # for those numbers
            color = {
                logging.WARNING: 33,
                logging.ERROR: 31,
                logging.FATAL: 31,
                logging.DEBUG: 36,
                SPAM: 34,
                logging.INFO: 32,
            }.get(record.levelno, 0)

            # if this runs in a separate process, write down the pid
            # to debug exit codes and such
            pid = ''
            if os.getpid() != logger.main_pid:
                pid = f'pid {os.getpid()}, '

            if debug:
                self._style._fmt = (  # noqa
                    '\033[1m'  # bold
                    f'\033[{color}m'  # color
                    f'%(levelname)s'
                    '\033[0m'  # end style
                    f'\033[{color}m'  # color
                    f': {pid}%(filename)s, line %(lineno)d, %(message)s'
                    '\033[0m'  # end style
                )
            else:
                self._style._fmt = (  # noqa
                    f'\033[{color}m%(levelname)s\033[0m: %(message)s'
                )
        return super().format(record)


logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(Formatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.getLogger('asyncio').setLevel(logging.WARNING)
logger.main_pid = os.getpid()


def is_debug():
    """True, if the logger is currently in DEBUG or SPAM mode."""
    return logger.level <= logging.DEBUG


def log_info():
    """Log version and name to the console"""
    # read values from setup.py
    try:
        name = pkg_resources.require('key-mapper')[0].project_name
        version = pkg_resources.require('key-mapper')[0].version
        logger.info('%s %s', name, version)
    except pkg_resources.DistributionNotFound as error:
        logger.info('Could not figure out the version')
        logger.debug(error)

    logger.debug('pid %s', os.getpid())


def update_verbosity(debug):
    """Set the logging verbosity according to the settings object.

    Also enable rich tracebacks in debug mode.
    """
    if debug:
        logger.setLevel(SPAM)

        try:
            from rich.traceback import install
            install(show_locals=True)
            logger.debug('Using rich.traceback')
        except Exception as error:
            # since this is optional, just skip all exceptions
            if not isinstance(error, ImportError):
                logger.debug('Cannot use rich.traceback: %s', error)
    else:
        logger.setLevel(logging.INFO)


def add_filehandler(path='~/.log/key-mapper'):
    """Clear the existing logfile and start logging to it."""
    log_path = os.path.expanduser(path)
    log_file = os.path.join(log_path, 'log')

    os.makedirs(log_path, exist_ok=True)

    if os.path.exists(log_file):
        # keep the log path small, start from scratch each time
        os.remove(log_file)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(Formatter())

    logger.info('Logging to "%s"', log_file)

    logger.addHandler(file_handler)

    return os.path.join(log_path, log_file)
