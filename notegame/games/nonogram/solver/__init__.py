# -*- coding: utf-8 -*-
"""Define nonogram solving operations"""


import logging

from notegame.games.nonogram.core.common import (normalize_description,
                                                 normalize_row)
from notegame.games.nonogram.core.line import bgu, efficient, machine, simpson

# TODO: choose the method for each registered solver
SOLVERS = {
    'partial_match': machine.PartialMatchSolver,

    'reverse_tracking': machine.ReverseTrackingSolver,
    'reverse_tracking_color': machine.ReverseTrackingColoredSolver,

    'simpson': simpson.FastSolver,

    'bgu': bgu.BguSolver,
    'bgu_color': bgu.BguColoredSolver,
    'blot': bgu.BguBlottedSolver,
    'blot_color': bgu.BguColoredBlottedSolver,

    'efficient': efficient.EfficientSolver,
    'efficient_color': efficient.EfficientColorSolver,
}


def solve_line(desc, line, method='reverse_tracking', normalized=False):
    """
    Utility for row solving that can be used in multiprocessing map
    """
    # method = kwargs.pop('method', 'reverse_tracking')
    #
    # if len(args) == 1:
    #     # mp's map supports only one iterable, so this weird syntax
    #     args = args[0]
    #
    # desc, line = args

    if not normalized:
        desc = normalize_description(desc)
        # desc = tuple(desc)
        line = normalize_row(line)

    try:
        solver = SOLVERS[method]
    except KeyError:
        raise KeyError("Cannot find solver '%s'" % method)

    return solver.solve(desc, line)


# TODO: automatically set the log level for each registered solver
def _set_solvers_log_level(level=logging.WARNING):
    machine.LOG.setLevel(level)
    simpson.LOG.setLevel(level)


_set_solvers_log_level()