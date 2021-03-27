# -*- coding: utf-8 -*-
"""
Dynamic programming algorithm to solve nonograms (using recursion)

See details in the work 'An Efficient Approach to Solving Nonograms':
https://ir.nctu.edu.tw/bitstream/11536/22772/1/000324586300005.pdf
"""

from six.moves import zip

from ..core.common import BOX, SPACE, UNKNOWN, partial_sums
from .base import BaseLineSolver, NonogramError


class EfficientSolver(BaseLineSolver):
    """
    Recursive nonogram line solver.
    Adapted from the work 'An Efficient Approach to Solving Nonograms'
    """

    def __init__(self, description, line):
        super(EfficientSolver, self).__init__(description, line)

        self.minimum_lengths = self.min_lengths(self.description)
        self.additional_space = self._set_additional_space()

        self._cache_width = len(self.description) + 1
        self._fix_table = self._init_tables()
        self._paint_table = self._init_tables()

    def _init_tables(self):
        cache_height = len(self.line) + 1
        return [None] * (self._cache_width * cache_height)

    def _linear_index(self, i, j):
        return (i + 1) * self._cache_width + (j + 1)

    def _set_additional_space(self):
        space = self.empty_cell()
        if self.line[0] != space:
            self.line = (space,) + self.line
            return True
        return False

    @classmethod
    def min_lengths(cls, description):
        """
        The minimum line sizes in which can squeeze from 0 to i-th block
        """

        min_indexes = [s - 1 for s in partial_sums(description, colored=False)]
        return min_indexes

    def fix(self, i, j):
        """
        Verify whether blocks from 0 to (j-1)-th
        can be resided inside a substring line[:i+1]
        """

        fixable = self._fix_table[self._linear_index(i, j)]
        if fixable is None:
            fixable = self._fix(i, j)
            self._fix_table[self._linear_index(i, j)] = fixable
        return fixable

    @classmethod
    def _can_be_space(cls, cell):
        return cell in (SPACE, UNKNOWN)

    def _fix_border_conditions(self, i, j):
        if j < 0:
            assert j == -1

            if i < 0:
                return True

            # NB: improvement
            return all(map(self._can_be_space, self.line[:i + 1]))

        # reached the beginning of the line
        if i < 0:
            assert i == -1

            # no more blocks to fill
            return j < 0

        if i < self.minimum_lengths[j]:
            return False

        return None

    def _fix(self, i, j):
        """
        Determine whether S[:i+1] is fixable with respect to D[:j+1]
        :param i: line size
        :param j: block number
        """
        res = self._fix_border_conditions(i, j)
        if res is not None:
            return res

        res = self._fix0(i, j) or self._fix1(i, j)
        return res

    def _fix0(self, i, j):
        """
        Determine whether S[:i+1] is fixable with respect to D[:j+1]
        in assumption that S[i] can be 0
        :param i: line size
        :param j: block number
        """

        if self._can_be_space(self.line[i]):
            return self.fix(i - 1, j)

        return False

    def _fix1(self, i, j):
        """
        Determine whether S[:i+1] is fixable with respect to D[:j+1]
        in assumption that S[i] can be 1
        :param i: line size
        :param j: block number
        """
        block_size = self.description[j]
        if j >= 0 and i >= block_size:
            block = self.line[i - block_size: i + 1]
            if self._is_space_with_block(block):
                return self.fix(i - block_size - 1, j - 1)

        return False

    @classmethod
    def _is_space_with_block(cls, line):
        if cls._can_be_space(line[0]):
            if all(pixel in (BOX, UNKNOWN) for pixel in line[1:]):
                return True

        return False

    @classmethod
    def _space_with_block(cls, block_size):
        return [cls.empty_cell()] + ([BOX] * block_size)

    @classmethod
    def empty_cell(cls):
        """
        Represent a single line symbol that is empty (no color)
        """
        return SPACE

    def paint(self, i, j):
        """
        Paint unsolved cells of line[:i+1]
        using blocks from 0 to (j+1)-th as description
        """
        if i < 0:
            return []

        painted = self._paint_table[self._linear_index(i, j)]
        if painted is None:
            if j < 0:
                if all(map(self._can_be_space, self.line[:i + 1])):
                    painted = [self.empty_cell()] * (i + 1)
                else:
                    raise NonogramError('Excess cells found at the beginning')
            else:
                painted = self._paint(i, j)

            self._paint_table[self._linear_index(i, j)] = painted

        return painted

    def _paint(self, i, j):
        fix0 = self._fix0(i, j)
        fix1 = self._fix1(i, j)

        if fix0:
            if fix1:
                return self._paint_both(i, j)

            return self._paint0(i, j)

        if fix1:
            return self._paint1(i, j)

        raise NonogramError('Block %r not fixable at position %r' % (j, i))

    def _paint0(self, i, j):
        return self.paint(i - 1, j) + [self.empty_cell()]

    def _paint1(self, i, j):
        block_size = self.description[j]
        return self.paint(i - block_size - 1, j - 1) + self._space_with_block(block_size)

    @classmethod
    def _merge_iter(cls, line1, line2):
        for pixel1, pixel2 in zip(line1, line2):
            if pixel1 == pixel2:
                yield pixel1
            else:
                yield UNKNOWN

    def _paint_both(self, i, j):
        return list(self._merge_iter(
            self._paint0(i, j),
            self._paint1(i, j)
        ))

    def _solve(self):
        res = self.paint(len(self.line) - 1, len(self.description) - 1)
        if self.additional_space:
            res = res[1:]

        return res

