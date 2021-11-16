# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-24-4:02 下午
from keras.layers import Dense, Conv2D, Input
import model
import experience
import encoder
import agent

class go_rl_robot:
    def __init__(self, board_size=19):
        self.board_size = board_size
        self.encoder = encoder.ZeroEncoder(board_size)
        self.input_data = Input(shape=self.encoder.shape(), name='input_data')
        self.model = model.Actor_Critic_Go(self.encoder.num_moves()).call(self.input_data)
        self.black_collector = experience.AlphaGoZeroExperienceCollector()
        self.white_collector = experience.AlphaGoZeroExperienceCollector()
        self.black_agent = agent.AlphaGoZeroAgent(self.model, self.encoder, collector=self.black_collector,
                                                  rounds_per_move=10, c=2.0, lr=1e-2, batch_size=2048)
        self.white_agent = agent.AlphaGoZeroAgent(self.model, self.encoder, collector=self.white_collector,
                                                  rounds_per_move=10, c=2.0, lr=1e-2, batch_size=2048)

    def train(self):
        for i in range(5):
            agent.game_simulation(board_size=self.board_size, black_agent=self.black_agent,
                                  white_agent=self.white_agent, black_collector=self.black_collector,
                                  white_collector=self.white_collector)
        experience_buffer = experience.combine_experience([self.black_collector, self.white_collector])
        self.black_agent.train(experience_buffer)

if __name__=='__main__':
    go_game = go_rl_robot()
    go_game.train()

