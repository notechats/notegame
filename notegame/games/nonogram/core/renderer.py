# -*- coding: utf-8 -*-
"""
Defines various renderers for the game of nonogram
"""

from abc import ABC
from sys import stdout

from notetool.tool.log import logger
from six import integer_types, itervalues, text_type

from ..utils.iter import max_safe, pad
from ..utils.other import two_powers
from .common import BOX, SPACE, UNKNOWN, BlottedBlock, is_list_like


class Cell(object):
    """Represent basic rendered cell"""

    DEFAULT_ICON = ' '

    def __init__(self, icon=None):
        self.icon = icon or self.DEFAULT_ICON

    def ascii_icon(self):
        """How the cell can be printed as a text"""
        return self.DEFAULT_ICON

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class ThumbnailCell(Cell):
    """
    Represent upper-left cell
    (where the thumbnail of the puzzle usually drawn).
    """
    DEFAULT_ICON = '#'


class ClueCell(Cell):
    """
    Represent cell that is part of description (clue).
    They are usually drawn on the top and on the left.
    """

    BLOTTED_SYMBOL = '?'

    def __init__(self, value):
        super(ClueCell, self).__init__()
        if is_list_like(value):
            self.value, self.color = value
        else:
            self.value, self.color = value, None

    def ascii_icon(self):
        """
        Gets a symbolic representation of a cell given its state
        and predefined table `icons`
        """
        if isinstance(self.value, integer_types):
            return text_type(self.value)

        if self.value == BlottedBlock:
            return self.BLOTTED_SYMBOL

        return self.DEFAULT_ICON

    def __repr__(self):
        return '{}(({}, {}))'.format(
            self.__class__.__name__,
            self.value, self.color)


class GridCell(Cell):
    """Represent the main area cell"""

    def __init__(self, value, renderer, colored=False):
        super(GridCell, self).__init__()

        self.renderer = renderer
        self.colored = colored
        if self.colored:
            self.value = tuple(two_powers(value))
        else:
            self.value = value

    def ascii_icon(self):
        value = self.value
        icons = self.renderer.icons

        if not self.colored:
            return icons[self.value]

        if len(value) == 1:
            value = value[0]
        else:
            # multiple colors
            value = UNKNOWN

        symbol = self.renderer.board.symbol_for_color_id(value)
        if symbol is not None:
            return symbol

        return icons.get(value, self.DEFAULT_ICON)

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__, self.value)


class _DummyBoard(object):
    """
    Stub for renderer initialization
    when it created before the corresponding board
    """
    rows_descriptions = columns_descriptions = ()
    width = height = 0


class Renderer(object):
    """Defines the abstract renderer for a nonogram board"""

    def __init__(self, board=None):
        self.cells = None
        self.board = None
        self.board_init(board)

    def board_init(self, board=None):
        """Initialize renderer's properties dependent on board it draws"""
        if board:
            logger.info('Init %r renderer with board %r',
                        self.__class__.__name__, board)
        else:
            if self.board:
                return  # already initialized, do nothing
            board = _DummyBoard()
        self.board = board

    @property
    def full_height(self):
        """The full visual height of a board"""
        return self.header_height + self.board.height

    @property
    def full_width(self):
        """The full visual width of a board"""
        return self.side_width + self.board.width

    @property
    def header_height(self):
        """The size of the header block with columns descriptions"""
        return max_safe(map(len, self.board.columns_descriptions), default=0)

    @property
    def side_width(self):
        """The width of the side block with rows descriptions"""
        return max_safe(map(len, self.board.rows_descriptions), default=0)

    def render(self):
        """Actually print out the board"""
        raise NotImplementedError()

    def draw(self, cells=None):
        """Calculate all the cells and draw an image of the board"""
        self.draw_header()
        self.draw_side()
        self.draw_grid(cells=cells)
        self.render()

    def draw_header(self):
        """
        Changes the internal state to be able to draw columns descriptions
        """
        raise NotImplementedError()

    def draw_side(self):
        """
        Changes the internal state to be able to draw rows descriptions
        """
        raise NotImplementedError()

    def draw_grid(self, cells=None):
        """
        Changes the internal state to be able to draw a main grid
        """
        raise NotImplementedError()

    @property
    def is_colored(self):
        """Whether the linked board is colored board"""
        return self.board.is_colored


class StreamRenderer(Renderer, ABC):
    """
    Simplify textual rendering of a board to a stream (stdout by default)
    """

    DEFAULT_ICONS = {
        UNKNOWN: '_',
        BOX: 'X',
        SPACE: '.',
    }

    def __init__(self, board=None, stream=stdout, icons=None):
        self.stream = stream
        if icons is None:
            icons = dict(self.DEFAULT_ICONS)
        self.icons = icons
        super(StreamRenderer, self).__init__(board)

    def _print(self, *args):
        return print(*args, file=self.stream)


class BaseAsciiRenderer(StreamRenderer):
    """
    Renders a board as a simple text table (without grid)
    """

    __rend_name__ = 'text'

    def board_init(self, board=None):
        super(BaseAsciiRenderer, self).board_init(board)
        logger.info('init cells: %sx%s', self.full_width, self.full_width)

        self.cells = [[Cell()] * self.full_width
                      for _ in range(self.full_height)]

    def cell_icon(self, cell):
        """
        Get a symbolic representation of a cell given its state
        and predefined table `icons`
        """
        return cell.ascii_icon()

    def render(self):
        for row in self.cells:
            res = []
            for index, cell in enumerate(row):
                ico = self.cell_icon(cell)

                # do not pad the last symbol in a line
                if len(ico) == 1:
                    if index < len(row) - 1:
                        ico += ' '

                res.append(ico)

            self._print(''.join(res))

    def draw_header(self):
        for i in range(self.header_height):
            for j in range(self.side_width):
                self.cells[i][j] = ThumbnailCell()

        for j, col in enumerate(self.board.columns_descriptions):
            rend_j = j + self.side_width
            if not col:
                col = [0]

            rend_column = [ClueCell(val) for val in col]
            rend_column = pad(rend_column, self.header_height, Cell())

            # self.cells[:self.header_height, rend_j] = rend_column
            for i, cell in enumerate(rend_column):
                self.cells[i][rend_j] = cell

    def draw_side(self):
        for i, row in enumerate(self.board.rows_descriptions):
            rend_i = i + self.header_height
            # row = list(row)
            if not row:
                row = [0]

            rend_row = [ClueCell(val) for val in row]
            rend_row = pad(rend_row, self.side_width, Cell())
            self.cells[rend_i][:self.side_width] = rend_row

    def draw_grid(self, cells=None):
        if cells is None:
            cells = self.board.cells

        is_colored = self.is_colored

        for i, row in enumerate(cells):
            rend_i = i + self.header_height
            for j, val in enumerate(row):
                rend_j = j + self.side_width
                self.cells[rend_i][rend_j] = GridCell(
                    val, self, colored=is_colored)


def _register_renderers():
    res = dict()
    for obj in itervalues(globals()):
        if isinstance(obj, type):
            if issubclass(obj, StreamRenderer) and hasattr(obj, '__rend_name__'):
                res[obj.__rend_name__] = obj
    return res


RENDERERS = _register_renderers()
