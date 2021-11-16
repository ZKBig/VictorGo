# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-21-10:19 上午
from keras.models import Sequential
from keras.layers.core import Dense, Flatten
from keras.layers.convolutional import Conv2D

def policy_value_model(input_shape,
                       num_filters=192,
                       is_policy_net=False,
                       first_kernel_size=5,
                       other_kernel_size=3):
    model = Sequential()
    model.add(
        Conv2D(num_filters, first_kernel_size, input_shape=input_shape, padding="same", data_format='channels_first', activation='relu')
    )

    for i in range(2, 12):
        model.add(
            Conv2D(num_filters, other_kernel_size, padding='same', data_format='channels_first', activation='relu')
        )

    # policy networks
    if is_policy_net:
        model.add(
            Conv2D(filters=1, kernel_size=1, padding='same', data_format='channels_first', activation='softmax')
        )
        model.add(Flatten())

        return model
    # value networks
    else:
        model.add(
            Conv2D(num_filters, other_kernel_size, padding='same', data_format='channels_first', activation='relu')
        )
        model.add(
            Conv2D(filters=1, kernel_size=1, padding='same', data_format='channels_first', activation='relu')
        )
        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dense(1, activation='tanh'))
        return model

