# -*- coding: utf-8 -*-
"""
Dynamic programming algorithm to solve nonograms (using recursion)

See details:
https://www.cs.bgu.ac.il/~benr/nonograms/
"""

from itertools import product

from notetool.tool.log import logger
from six.moves import range, zip

from ..core.common import (BOX, SPACE, UNKNOWN, BlottedBlock, partial_sums,
                           slack_space)
from .base import BaseLineSolver, NonogramError

# dummy constant
BOTH_COLORS = -1


class BguSolver(BaseLineSolver):
    """
    The solver uses recursion to solve the line to the most
    """

    def __init__(self, description, line):
        super(BguSolver, self).__init__(description, line)
        self._additional_space = self._set_additional_space()

        self.block_sums = self.calc_block_sum(description)
        self.solved_line = list(self.line)

        self._reset_solutions_table()

    def _reset_solutions_table(self):
        positions = len(self.line)
        job_size = len(self.description) + 1
        self.sol = [[None] * positions for _ in range(job_size)]

    def _set_additional_space(self):
        """
        Define the internal representation of a line to be one cell larger then the original.
        This is done to avoid an edge case later in our recursive formula.
        """
        if self.line[-1] != SPACE:
            self.line = list(self.line) + [SPACE]
            return True

        return False

    def _solve(self):
        if self.try_solve():
            solved = self.solved_line
            if self._additional_space:
                solved = solved[:-1]
            solved = (UNKNOWN if cell ==
                      BOTH_COLORS else cell for cell in solved)
            return solved

        raise NonogramError('Bad line')

    def try_solve(self):
        """
        The main solver function.
        Return whether the line is solvable.
        """
        position, block = len(self.line) - 1, len(self.description)
        return self.get_sol(position, block)

    @classmethod
    def calc_block_sum(cls, blocks):
        """
        calculates the partial sum of the blocks.
        this is used later to determine if we can fit some blocks in the space left on the line
        """
        min_indexes = [s - 1 for s in partial_sums(blocks, colored=False)]
        return [0] + min_indexes

    def fill_matrix_top_down(self, position, block):
        """
        Calculate the solution for line[:position+1]
        in respect to description[:block]

        :param position: position of cell we're currently trying to fill
        :param block: current block number
        :return: whether the segment of line solvable
        """

        if (position < 0) or (block < 0):
            return None

        # too many blocks left to fit this line segment
        if position < self.block_sums[block]:
            return False

        # recursive case
        if self.line[position] == BOX:  # current cell is BOX
            return False  # can't place a block if the cell is black

        # base case
        if position == 0:  # reached the end of the line
            if block == 0:
                self.add_cell_color(position, SPACE)
                return True

            return False

        # current cell is either white or unknown
        white_ans = self.get_sol(position - 1, block)

        # block == 0 means we finished filling all the blocks (can still fill whitespace)
        if block > 0:
            block_size = self.description[block - 1]

            if self.can_place_block(position - block_size, block_size):
                black_ans = self.get_sol(position - block_size - 1, block - 1)
                if black_ans:
                    # set cell white, place the current block and continue
                    self.set_line_block(position - block_size, position)
                    return True

        if white_ans:
            # set cell white and continue
            self.add_cell_color(position, SPACE)
            return True

        return False  # no solution

    def can_place_block(self, position, length):
        """
        check if we can place a block of a specific length in this position
        we check that our partial solution does not negate the line's partial solution
        :param position:  position to place block at
        :param length:  length of block
        """
        if position < 0:
            return False

        # if no negations were found, the block can be placed
        return SPACE not in self.line[position: position + length]

    def add_cell_color(self, position, value):
        """sets a cell in the solution matrix"""

        cell = self.solved_line[position]
        if cell == BOTH_COLORS:
            pass
        elif cell == UNKNOWN:
            self.solved_line[position] = value
        elif cell != value:
            self.solved_line[position] = BOTH_COLORS

    def set_line_block(self, start_pos, end_pos):
        """
        sets a block in the solution matrix. all cells are painted black,
        except the end_pos which is white.
        :param start_pos: position to start painting
        :param end_pos: position to stop painting
        """

        # set blacks
        for i in range(start_pos, end_pos):
            self.add_cell_color(i, BOX)

        self.add_cell_color(end_pos, SPACE)

    def set_sol(self, position, block, value):
        """
        sets a value in the solution matrix
        so we wont calculate this value recursively anymore
        """
        if position < 0:
            return

        self.sol[block][position] = value

    def get_sol(self, position, block):
        """
        gets the value from the solution matrix
        if the value is missing, we calculate it recursively
        """

        if position == -1:
            # finished placing the last block, exactly at the beginning of the line.
            return block == 0

        # self._get_sol(position, block)
        can_be_solved = self.sol[block][position]
        if can_be_solved is None:
            can_be_solved = self.fill_matrix_top_down(position, block)

            # self.set_sol(position, block, can_be_solved)
            self.sol[block][position] = can_be_solved

        return can_be_solved


UNKNOWN_COLORED = 0


class BlottedSolver(BaseLineSolver):
    """Some additional routines to help solve blotted puzzles"""

    @classmethod
    def is_solved(cls, description, line):
        """
        Whether the line already solved.
        Do not solve if so, since the blotted algorithm is computationally heavy.
        """
        raise NotImplementedError()

    @classmethod
    def _blotted_combinations(cls, description, line):
        """
        Generate all the possible combinations of blotted blocks sizes.
        The routine suggests that every size can be in range [0..max_sum]
        """

        blocks_number = sum(1 for block in description
                            if cls._is_blotted(block))
        max_sum = slack_space(len(line), description)

        valid_range = range(max_sum + 1)
        for combination in product(valid_range, repeat=blocks_number):
            if sum(combination) <= max_sum:
                yield combination

    @classmethod
    def _is_blotted(cls, block):
        raise NotImplementedError()

    @classmethod
    def _update_block(cls, current, increase):
        raise NotImplementedError()

    @classmethod
    def _single_color(cls, values):
        raise NotImplementedError()

    @classmethod
    def merge_solutions(cls, one, other=None):
        """Merge solutions from different description suggestions"""
        if other is None:
            return one

        logger.debug('Merging two solutions: %r and %r', one, other)
        return [cls._single_color(set(cells))
                for cells in zip(one, other)]

    @classmethod
    def solve(cls, description, line):
        """Solve the line (or use cached value)"""
        if not line:
            return line

        if not BlottedBlock.how_many(description):
            return super(BlottedSolver, cls).solve(description, line)

        if cls.is_solved(description, line):
            logger.info('No need to solve blotted line: %r', line)
            return line

        blotted_desc, line = tuple(description), tuple(line)
        logger.warning('Solving line %r with blotted description %r',
                       line, blotted_desc)

        blotted_positions = [index for index, block in enumerate(blotted_desc)
                             if cls._is_blotted(block)]

        # prevent from incidental changing
        min_desc = tuple(BlottedBlock.replace_with_1(blotted_desc))

        solution = None
        for index, combination in enumerate(cls._blotted_combinations(
                blotted_desc, line)):

            current_description = list(min_desc)
            for pos, block_size in zip(blotted_positions, combination):
                block = current_description[pos]
                current_description[pos] = cls._update_block(block, block_size)

            logger.debug('Trying %i-th combination %r',
                         index, current_description)

            try:
                solved = tuple(super(BlottedSolver, cls).solve(
                    current_description, line))
            except NonogramError:
                logger.debug('Combination %r is invalid for line %r',
                             current_description, line)
            else:
                solution = cls.merge_solutions(solved, solution)
                logger.debug('Merged solution: %s', solution)
                if tuple(solution) == line:
                    logger.warning('The combination %r (description=%r) is valid but '
                                   'brings no new information. Stopping the combinations search.',
                                   combination, current_description)
                    break

        if not solution:
            raise NonogramError(
                'Cannot solve with blotted clues {!r}'.format(blotted_desc))

        logger.info('United solution from all combinations: %r', solution)
        assert len(solution) == len(line)
        return tuple(solution)


class BguBlottedSolver(BlottedSolver, BguSolver):
    """
    Slightly modified algorithm to solve with blotted descriptions
    """

    @classmethod
    def is_solved(cls, description, line):
        if UNKNOWN in line:
            return False

        return BlottedBlock.matches(description, line)

    @classmethod
    def calc_block_sum(cls, blocks):
        blocks = BlottedBlock.replace_with_1(blocks)
        return super(BguBlottedSolver, cls).calc_block_sum(blocks)

    @classmethod
    def _is_blotted(cls, block):
        return block == BlottedBlock

    @classmethod
    def _update_block(cls, current, increase):
        return current + increase

    @classmethod
    def _single_color(cls, values):
        if len(values) > 1:
            return UNKNOWN

        return tuple(values)[0]
