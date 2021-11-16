# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-24-4:12 下午
import tensorflow as tf
import keras
import keras.layers as layers
import os

class Actor_Critic_Go(keras.Model):
    def __init__(self, policy_output_dims):
        super(Actor_Critic_Go, self).__init__()

        self.policy_output_dims = policy_output_dims

        self.conv1 = layers.Conv2D(64, (3,3), padding='same',
                                   data_format='channels_last', activation='relu')
        self.conv2 = layers.Conv2D(64, (3, 3), padding='same',
                                   data_format='channels_last', activation='relu')
        self.conv3 = layers.Conv2D(64, (3, 3), padding='same',
                                   data_format='channels_last', activation='relu')
        self.conv4 = layers.Conv2D(64, (3, 3), padding='same',
                                   data_format='channels_last', activation='relu')
        self.conv5 = layers.Conv2D(64, (3, 3), padding='same',
                                   data_format='channels_last', activation='relu')
        self.conv6 = layers.Conv2D(64, (3, 3), padding='same',
                                   data_format='channels_last', activation='relu')
        self.conv7 = layers.Conv2D(64, (3, 3), padding='same',
                                   data_format='channels_last', activation='relu')
        self.conv8 = layers.Conv2D(64, (3, 3), padding='same',
                                   data_format='channels_last', activation='relu')

        self.policy_conv = layers.Conv2D(2, (1,1), data_format='channels_last', activation='relu')
        self.policy_flat = layers.Flatten()
        self.policy_output = layers.Dense(self.policy_output_dims, activation='softmax')

        self.value_conv = layers.Conv2D(1, (1,1), data_format='channels_last', activation='relu')
        self.value_flat = layers.Flatten()
        self.value_hidden = layers.Dense(256, activation='relu')
        self.value_output = layers.Dense(1, activation='tanh')

    def call(self, board_input):
        x = self.conv1(board_input)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.conv5(x)
        x = self.conv6(x)
        x = self.conv7(x)
        x = self.conv8(x)
        policy_conv = self.policy_conv(x)
        policy_flat = self.policy_flat(policy_conv)
        moves_priors = self.policy_output(policy_flat)

        value_conv = self.value_conv(x)
        value_flat = self.value_flat(value_conv)
        value_hidden = self.value_hidden(value_flat)
        move_value = self.value_output(value_hidden)

        model = keras.models.Model(inputs=[board_input], outputs=[moves_priors, move_value])

        return model







