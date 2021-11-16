# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-20-10:01 上午
import numpy as np
from Go.encoders.base import Encoder
from Go.go_game_logics.goboard import Move
from Go.go_game_logics.go_elements import Point

class SevenPlaneEncoder(Encoder):
    """
    1. The first plane encode the white stone with one liberty as 1, and encode the remaining points as 0;
    2. Likewise, the second and third planes are corresponding to the white stones with two liberty and three liberty;
    3. Note that the forth plane to the sixth plane represent the black stones with the same encoding principles as the
       white stones;
    4. The seventh plane is used to denote the ko situation.
    """
    def __init__(self, board_size):
        self.board_width, self.board_height = board_size
        self.num_planes = 7

    def name(self):
        return 'seven_planes'

    def encode(self, game_state):
        board = np.zeros(self.shape())
        base_plane = {game_state.next_player: 0,
                      game_state.next_player.other: 3}
        for row in range(self.board_height):
            for col in range(self.board_width):
                point = Point(row=row+1, col=col+1)
                go_string = game_state.board.get_go_string(point)
                if go_string is None:
                    continue
                if game_state.does_move_violate_ko(game_state.next_player, Move.play(point)):
                    board[6][row][col] = 1
                else:
                    # encode the point with the liberties being 1, 2 or 3
                    liberty_plane = min(3, go_string.num_liberties) - 1 + \
                                    base_plane[go_string.color]
                    board[liberty_plane][row][col] = 1

        return board

    def encode_point(self, point):
        return self.board_width * (point.row - 1) + (point.col - 1)

    def decode_point_index(self, index):
        row = index // self.board_width
        col = index % self.board_width
        return Point(row=row + 1, col=col + 1)

    def num_points(self):
        return self.board_width * self.board_height

    def shape(self):
        return self.num_planes, self.board_height, self.board_width



