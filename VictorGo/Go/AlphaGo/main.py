# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-20-9:19 上午
from Go.data.processor import GoDataProcessor
from Go.encoders.alphaGo import AlphaGoEncoder
from Go.AlphaGo import Policy_Value_model
from Go.agent.cloning_predict_agent import DLAgent

from keras.callbacks import ModelCheckpoint
import h5py

class go_game_train:
    def __init__(self,
                 rows=19,
                 cols=19,
                 num_games=1000,
                 epochs=200,
                 batch_size=128):
        self.epochs = epochs
        self.batch_size = batch_size
        self.go_board_rows = rows
        self.go_board_cols = cols
        self.num_classes = rows * cols
        self.num_games = num_games
        # self.encoder = SevenPlaneEncoder((rows, cols))
        self.encoder = AlphaGoEncoder()
        self.processor = GoDataProcessor(encoder=self.encoder.name())
        self.train_generator = self.processor.load_go_data('train', self.num_games, generator=True)
        self.test_generator = self.processor.load_go_data('test', self.num_games, generator=True)

    def policy_train(self):
        input_shape = (self.encoder.num_planes, self.go_board_rows, self.go_board_cols)
        model = Policy_Value_model.policy_value_model(input_shape=input_shape, is_policy_net=True)
        model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
        model.fit_generator(generator=self.train_generator.generate(self.batch_size, self.num_classes),
                            epochs=self.epochs, steps_per_epoch=self.train_generator.get_num_samples()/self.batch_size,
                            validation_data=self.test_generator.generate(self.batch_size, self.num_classes),
                            validation_steps=self.test_generator.get_num_samples()/self.batch_size,
                            callbacks=[ModelCheckpoint('./checkpoints/alphago_policy{epoch}.h5')])
        # model.evaluate_generator(generator=self.test_generator.generate(self.batch_size, self.num_classes),
        #                          steps=self.test_generator.get_num_samples()/self.batch_size)
        agent = DLAgent(model, self.encoder)

        with h5py.File('alphago_policy.h5', 'w') as agent_out:
            agent.serialize(agent_out)


if __name__=="__main__":
    go = go_game_train()

