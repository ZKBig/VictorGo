# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-07-10:14 下午
import enum
from collections import namedtuple


class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        """
        :return: next stone color of player
        """
        return Player.black if self == Player.white else Player.white


class Point(namedtuple('Point', 'row col')):
    def neighbors(self):
        """
        :return: the four neighbor points of the current point
        """
        return [
            Point(self.row - 1, self.col),
            Point(self.row + 1, self.col),
            Point(self.row, self.col - 1),
            Point(self.row, self.col + 1),
        ]


class Move:
    """
    this class is used to represent the movement of the player, namely,
    play, pass and resign. Note that when play is implemented, the point of
    the stone to be put needs determining.
    """

    def __init__(self, point=None, is_pass=False, is_resign=False):
        self.point = point
        self.is_play = (self.point is not None)
        self.is_pass = is_pass
        self.is_resign = is_resign

    @classmethod
    def play(cls, point):
        return Move(point=point)

    @classmethod
    def pass_turn(cls):
        return Move(is_pass=True)

    @classmethod
    def resign(cls):
        return Move(is_resign=True)


class GoString:
    """
    the class is used to define a string of stones, which makes it easy to check the
    take implementation;
    note that using 'frozenset' to store the stones and the liberties of a go string
    means that the elements in the set cannot be changed.
    """

    def __init__(self, color, stones, liberties):
        self.color = color
        self.stones = frozenset(stones)
        self.liberties = frozenset(liberties)

    def without_liberty(self, point):
        new_liberties = self.liberties - {point}
        return GoString(self.color, self.stones, new_liberties)

    def with_liberty(self, point):
        new_liberties = self.liberties | {point}
        return GoString(self.color, self.stones, new_liberties)

    def merge_with(self, go_string):
        assert go_string.color == self.color
        combines_stones = self.stones | go_string.stones
        return GoString(self.color, combines_stones, (self.liberties | go_string.liberties) - combines_stones)

    def num_liberties(self):
        return len(self.liberties)

    def __eq__(self, other):
        return isinstance(other, GoString) and \
               self.color == other.color and \
               self.stones == other.stones and \
               self.liberties == other.liberties
