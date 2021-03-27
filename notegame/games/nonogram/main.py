# -*- coding: utf-8 -*-
"""
The program's entry point
"""

import json

from notegame.games.nonogram.core.backtracking import Solver
from notegame.games.nonogram.core.board import make_board
from notegame.games.nonogram.core.renderer import BaseAsciiRenderer
from notegame.games.nonogram.reader import read_example


def solve(d_board, draw_final=False, draw_probes=False, **solver_args):
    """
    Wrapper for solver that handles errors and prints out the results
    """

    if not draw_final:
        d_board.on_solution_round_complete = lambda board: board.draw()
        if d_board.has_blots:
            d_board.on_row_update = lambda index, board: board.draw()
            d_board.on_column_update = lambda index, board: board.draw()

    solver = Solver(d_board, **solver_args)

    exc = False
    try:
        solver.solve()
    except BaseException:
        exc = True
        raise
    finally:
        if exc or draw_final:
            # draw the last solved cells
            d_board.draw()

        if not d_board.is_solved_full:
            d_board.draw_solutions()

        if draw_probes and solver.search_map:
            print(json.dumps(solver.search_map.to_dict(), indent=1))


def draw_solution(board_def, draw_final=False, **solver_args):
    """Solve the given board in terminal with animation"""
    d_board = make_board(*board_def, renderer=BaseAsciiRenderer)

    solve(d_board, draw_final=draw_final, **solver_args)


def main():
    columns = [[7], [1], [1], [1], [7], [0],
               [3], [1, 1, 1], [1, 1, 1], [2], [0],
               [6], [0],
               [6], [0],
               [3], [1, 1], [5], [1, 1], [3], [0],
               [5, 1], ]
    rows = [[1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 2, 1, 1, 3, 1],
            [5, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 4, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 2, 1, 1, 3, 1], ]

    board_def = read_example("hello.txt")
    board_def = (columns, rows)
    draw_solution(board_def)


if __name__ == '__main__':
    main()
