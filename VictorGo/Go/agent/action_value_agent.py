# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-23-10:28 上午
from Go.go_game_logics.goboard import Move
from Go.agent.helpers import is_point_an_eye
from Go.agent.base import Agent
from Go import encoders

import numpy as np
import keras
import tempfile
import h5py
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

class ValueAgent(Agent):
    def __init__(self,
                 model,
                 encoder,
                 lr=0.1,
                 batch_size=128,
                 epochs=1):
        Agent.__init__(self)
        self.model = model
        self.encoder = encoder
        self.collector = None
        self.epsilon = 0.0
        self.last_move_value = 0
        self.lr = lr
        self.batch_size = batch_size
        self.epochs = epochs

    def predict(self, game_state):
        encoded_state = self.encoder.encode(game_state)
        input_states = np.array([encoded_state])
        return self.model.predict(input_states)[0]

    def select_move(self, game_state):
        moves = []
        boards = []
        for move in game_state.legal_moves():
            if not move.is_play:
                continue
            next_state = game_state.after_move(move)
            board = self.encoder.encode(next_state)
            moves.append(move)
            boards.append(board)
        if not moves:
            return Move.pass_turn()

        opp_states_values = self.model.predict(boards=np.array([boards]))
        opp_states_values = opp_states_values.reshape(len(moves))

        states_values = 1 - opp_states_values
        ranked_moves = self.ranked_moves_eps_greedy(states_values)

        for move_index in ranked_moves:
            move = moves[move_index]
            # board = boards[move_index]
            if not is_point_an_eye(game_state.board, move.point, game_state.next_player):
                if self.collector is not None:
                    self.collector.record_decision(
                        state_value=states_values[move_index],
                        action=self.encoder.encode_point(move.point)
                    )
                self.last_move_value = float(states_values[move_index])
                return move

        return Move.pass_turn()

    def train(self, experience):
        self.model.compile(loss='mse', optimizer=keras.optimizers.SGD(lr=self.lr))
        n = experience.state_values.shape[0]
        y = np.zeros((n,))
        for i in range(n):
            reward = experience.rewards[i]
            y[i] = 1 if reward > 0 else -1

        self.model.fit(experience.state_values, y, batch_size=self.batch_size, epochs=self.epochs)


    def serialize(self, h5file):
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self.encoder.name()
        h5file['encoder'].attrs['board_width'] = self.encoder.board_width
        h5file['encoder'].attrs['board_height'] = self.encoder.board_height
        h5file.create_group('model')
        save_model_h5(self.model, h5file['model'])

    def ranked_moves_eps_greedy(self, values):
        if np.random.random() < self.epsilon:
            values = np.random.random(values.shape)

        ranked_moves = np.argsort(values)

        return ranked_moves[::-1]

def load_value_agent(h5file):
    model = load_model_h5(h5file['model'])
    encoder_name = h5file['encoder'].attrs['name']
    if not isinstance(encoder_name, str):
        encoder_name = encoder_name.decode('ascii')
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['encoder'].attrs['board_height']
    encoder = encoders.get_encoder_by_name(
        encoder_name,
        (board_width, board_height))
    return ValueAgent(model, encoder)











