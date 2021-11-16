# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-10-9:40 下午
import numpy as np
from Go.encoders.base import Encoder
from Go.go_game_logics.go_elements import Point

class OnePlaneEncoder(Encoder):
    def __init__(self, board_size):
        self.board_width, self.board_height = board_size
        self.num_planes = 1

    def name(self):
        return 'one_plane'

    def encode(self, game_state):
        board = np.zeros(self.shape())
        next_player = game_state.next_player
        for r in range(self.board_height):
            for c in range(self.board_width):
                p = Point(row=r+1, col=c+1)
                go_string = game_state.current_baord.get_go_string(p)
                if go_string is None:
                    continue
                if go_string.color == next_player:
                    board[0, r, c] = 1
                else:
                    board[0, r, c] = -1

        return board

    def encode_point(self, point):
        return self.board_width * (point.row - 1) + (point.col - 1)

    def decode_point_index(self, index):
        row = index // self.board_width
        col = index % self.board_width

        return Point(row=row+1, col=col+1)

    def num_point(self):
        return self.board_width * self.board_height

    def shape(self):
        return self.num_planes, self.board_height, self.board_width

