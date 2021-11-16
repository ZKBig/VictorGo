# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-21-2:38 下午
import numpy as np
from keras import backend
from Go.agent.base import Agent
from Go import encoders
from Go.go_game_logics import goboard
import tempfile
import os
import h5py
import keras

from Go.go_game_logics.goboard import is_point_an_eye


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


class PolicyAgent(Agent):
    def __init__(self,
                 model,
                 encoder,
                 lr=1e-7,
                 clip=1.0,
                 batch_size=512,
                 epochs=1):
        Agent.__init__(self)
        self._model = model
        self._encoder = encoder
        self._collector = None
        self._temperature = 0.0
        self.lr = lr
        self.clip = clip
        self.batch_size = batch_size
        self.epochs = epochs

    def predict(self, game_state):
        encoded_state = self._encoder.encode(game_state)
        input = np.array([encoded_state])
        return self._model.predict(input)[0]

    def set_temperature(self, temperature):
        self._temperature = temperature

    def set_collector(self, collector):
        self._collector = collector

    def select_move(self, game_state):
        num_moves = self._encoder.board_width * self._encoder.board_height
        encoded_state = self._encoder.encode(game_state)
        x = np.array([encoded_state])

        if np.random.random() < self._temperature:
            move_probs = np.ones(num_moves) / num_moves
        else:
            move_probs = self._model.predict(x)[0]

        eps = 1e-5
        move_probs = np.clip(move_probs, eps, 1 - eps)
        move_probs = move_probs / np.sum(move_probs)

        candidates = np.array(num_moves)
        ranked_moves = np.random.choice(candidates, num_moves, replace=False, p=move_probs)
        for point_index in ranked_moves:
            point = self._encoder.decode_point_index(point_index)
            if game_state.is_valid_move(goboard.Move.play(point)) and \
                not is_point_an_eye(game_state.board, point, game_state.next_player):
                if self._collector is not None:
                    self._collector.record_decision(
                        state=encoded_state,
                        action=point_index
                    )
                return goboard.Move.play(point)
        return goboard.Move.pass_turn()

    def train(self, experience):
        self._model.compile(loss='categorical_crossentropy',
                            optimizers=keras.optimizers.SGD(lr=self.lr, clipnorm=self.clip))
        n = experience.states.shape[0]
        num_moves = self._encoder.board_width * self._encoder.board_height
        y = np.zeros((n, num_moves))
        for i in range(n):
            action = experience.actions[i]
            reward = experience.rewards[i]
            y[i][action] = reward

        self._model.fit(experience.states, y, batch_size=self.batch_size, epochs=self.epochs)

    def serialize(self, h5file):
        h5file.create_group('encoder')
        h5file['encoder'].attrs['name'] = self._encoder.name()
        h5file['encoder'].attrs['board_width'] = self._encoder.board_width
        h5file['encoder'].attrs['board_height'] = self._encoder.board_height
        h5file.create_group('model')
        save_model_h5(self._model, h5file['model'])

def policy_gradient_loss(y_true, y_pred):
    clip_pred = backend.clip(y_pred, backend.epsilon(), 1 - backend.epsilon())
    loss = -1 * y_true * backend.log(clip_pred)
    return backend.mean(backend.sum(loss, axis=1))

def normalize(x):
    total = np.sum(x)
    return x / total

def load_agent(h5file):
    model = load_model_h5(h5file['model'], custom_objects={'policy_gradient_loss': policy_gradient_loss})
    encoder_name = h5file['encoder'].attrs['name']
    if not isinstance(encoder_name, str):
        encoder_name = encoder_name.decode('ascii')
    board_width = h5file['encoder'].attrs['board_width']
    board_height = h5file['enocder'].attrs['board_heihgt']
    encoder = encoders.get_encoder_by_name(encoder_name, (board_width, board_height))

    return PolicyAgent(model, encoder)
