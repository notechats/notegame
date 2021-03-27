# -*- coding: utf-8 -*-
"""
Defines various renderers for the game of nonogram
"""

import curses
import locale
import time

from notetool.tool.log import logger
from six import itervalues, string_types
from six.moves import queue

from notegame.games.nonogram.core.renderer import BaseAsciiRenderer


class CursesRenderer(BaseAsciiRenderer):
    """
    Hack for renderers to be able to put their strings in queue
    instead of printing them out into stream
    """

    def _print(self, *args):
        for arg in args:
            self.stream.put(arg)

    def render(self):
        # clear the screen before next board
        self._print(self.separator)
        super(CursesRenderer, self).render()
        # allow the drawing thread to do its job
        time.sleep(0)

    CLS_SEPARATOR = '\n'
    separator = CLS_SEPARATOR

    def draw(self, cells=None):
        """
        Additionally set up the separator between solutions
        to enable clearing the screen on ordinary update
        and informational message when a unique solution gets printed
        """
        if cells is None:
            self.separator = self.CLS_SEPARATOR
        else:
            # do not clear the screen for new solution
            self.separator = 'Unique solution'

        super(CursesRenderer, self).draw(cells=cells)
