# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-20-12:12 下午
from Go.go_game_logics.goboard import is_point_an_eye
from Go.go_game_logics import goboard
from Go.agent.base import Agent
from Go import encoders

import h5py
import numpy as np
import tempfile
import keras
import os



def save_model_h5(model, file):
    fd, fname = tempfile.mkstemp(prefix='temp_model')
    try:
        os.close(fd)
        keras.models.save_model(model, fname)
        serialized_model = h5py.File(fname, 'r')
        root_item = serialized_model.get('/')
        serialized_model.copy(root_item, file, 'keras_model')
        serialized_model.close()
    finally:
        os.unlink(fname)

def load_model_h5(file, custom_objects=None):
    fd, fname = tempfile.mkstemp(prefix='temp_model')
    try:
        os.close(fd)
        serialized_model = h5py.File(fname, 'w')
        root_item = file.get('keras_model')
        for attr_name, attr_value in root_item.attrs.items():
            serialized_model.attrs[attr_name] = attr_value
        for k in root_item.keys():
            file.copy(root_item.get(k), serialized_model, k)
        serialized_model.close()
        return keras.models.load_model(fname, custom_object=custom_objects)
    finally:
        os.unlink(fname)

class DLAgent(Agent):
    def __init__(self, model, encoder):
        Agent.__init__(self)
        self.model = model
        self.encoder = encoder

    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)
        input_data = np.array([encoded_state])
        return self.model.predict(input_data)[0]

    def select_move(self, game_state, eps=1e-6):
        num_moves = self.encoder.board_width * self.encoder.board_height
        move_probs = self.predict(game_state)
        move_probs = move_probs ** 3
        move_probs = np.clip(move_probs, eps, 1 - eps)
        move_probs = move_probs / np.sum(move_probs)

        candidates = np.arange(num_moves)
        # pick out the potential candidate which are from the ranked indeices of points
        ranked_moves = np.random.choice(candidates, num_moves, replace=False, p=move_probs)
        for point_index in ranked_moves:
            point = self.encoder.decode_point_index(point_index)
            if game_state.is_valid_move(goboard.Move.play(point)) and not \
                    is_point_an_eye(game_state.board, point, game_state.next_player):
                return goboard.Move.play(point)

        return goboard.Move.pass_turn()

    def serialize(self, h5file):
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self.encoder.name()
        h5file['encoder'].attrs['board_width'] = self.encoder.board_width
        h5file['encoder'].attrs['board_height'] = self.encoder.board_height
        h5file.create_group('model')
        save_model_h5(self.model, h5file['model'])

    def load_prediction(self, h5file):
        model = load_model_h5(h5file['model'])
        encoder_name = h5file['encoder'].attrs['name']
        if not isinstance(encoder_name, str):
            encoder_name = encoder_name.decode('ascii')
        board_width = h5file['encoder'].attrs['board_width']
        board_height = h5file['encoder'].attrs['board_height']
        encoder = encoders.get_encoder_by_name(encoder_name, (board_width, board_height))

        return model, encoder

def load_predict_model(h5file):
    model = load_model_h5(h5file['model'])
    encoder = h5file['encoder'].attrs['name']
    if not isinstance(encoder, str):
        encoder = encoder.decode('ascii')
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['encoder'].attrs['board_height']
    encoder = encoders.get_encoder_by_name(encoder, (board_width, board_height))
    return DLAgent(model, encoder)
