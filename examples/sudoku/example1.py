# -*- coding: utf-8 -*-

import logging

from notetool.tool.log import logger

from notegame.games.sudoku import (sudoku_check_solution, sudoku_generate,
                                   sudoku_solve_solution)

logger.setLevel(logging.INFO)
if __name__ == "__main__":
    data1 = [8, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 3, 6, 0, 0, 0, 0, 0,
             0, 7, 0, 0, 9, 0, 2, 0, 0,
             0, 5, 0, 0, 0, 7, 0, 0, 0,
             0, 0, 0, 0, 4, 5, 7, 0, 0,
             0, 0, 0, 1, 0, 0, 0, 3, 0,
             0, 0, 1, 0, 0, 0, 0, 6, 8,
             0, 0, 8, 5, 0, 0, 0, 1, 0,
             0, 9, 0, 0, 0, 0, 4, 0, 0]

    puzzle = sudoku_generate(mask_rate=0.7)
    data1 = puzzle
    logger.start()
    solved1 = sudoku_solve_solution(data1, 1)
    logger.info("method 1:", before=True)
    solved2 = sudoku_solve_solution(data1, 2)
    logger.info("method 2:", before=True)

    sudoku_check_solution(solved1)
    sudoku_check_solution(solved2)
