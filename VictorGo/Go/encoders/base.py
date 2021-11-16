# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-10-8:34 下午
import importlib

class Encoder:
    def name(self):
        raise NotImplementedError()

    # convert the go to data
    def encode(self, game_state):
        raise NotImplementedError()

    # convert a point to an index
    def encode_point(self, point):
        raise NotImplementedError()

    # convert an index to a point
    def decode_point_index(self, index):
        raise NotImplementedError()

    # the total number of cross points
    def num_points(self):
        raise NotImplementedError()

    def shape(self):
        raise NotImplementedError()


def get_encoder_by_name(name, board_size):
    if isinstance(board_size, int):
        board_size = (board_size, board_size)
    module = importlib.import_module('Go.encoders.'+name)
    constructor = getattr(module, 'create')
    return constructor(board_size)

