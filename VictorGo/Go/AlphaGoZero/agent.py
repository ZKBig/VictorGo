# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-23-6:24 下午
from Go.agent.base import Agent
from Go.go_game_logics.goboard import Player, GameState
from Go.go_fundations import scoring
from alphagoZero_tree import TreeNode

import numpy as np
import keras

class AlphaGoZeroAgent(Agent):
    def __init__(self,
                 model,
                 encoder,
                 collector=None,
                 rounds_per_move=1600,
                 c=2.0,
                 lr=1e-7,
                 batch_size=128,
                 epochs=20):
        '''

        :param model: the trained model
        :param encoder: the game state encoder
        :param rounds_per_move:
        :param c:
        '''
        self.model = model
        self.encoder = encoder
        self.collector = collector
        self.num_rounds = rounds_per_move
        self.c = c
        self.lr = lr
        self.batch_size = batch_size
        self.epochs = epochs

    def create_node(self, game_state, move=None, parent=None):
        '''
        implement the last move and get the new game state,
        then input the new game state into the network so that
        the priors value are obtained.

        :param game_state: the new game state
        :param move: the last move
        :param parent: the parent of this node
        :return: the new node
        '''
        encoded_state = self.encoder.encode(game_state)
        input_data = np.array([encoded_state])
        # input_data = tf.transpose(input_data, [0, 2, 3, 1])
        # print(input_data.shape)
        priors, values = self.model.predict(input_data)
        priors = priors[0]
        value = values[0][0]
        move_priors = {
            self.encoder.decode_move_index(index): prior for index, prior in enumerate(priors)
        }
        new_node = TreeNode(game_state, value, move_priors, parent, move)
        if parent is not None:
            parent.add_child(move, new_node)

        return new_node

    def select_branch(self, node):
        N = node.total_visit_count

        def score_branch(move):
            """
            Scoring function:

            Branch Value = Q + c * P * sqrt(N) / (1 + n)

            Q: the average of the expected values of the branched through the move;
            P: the prior probability of the move;
            N: the visit number of the parent node of the current move branch;
            n: the visit number of the current move branch;
            c: the weighted parameter

            :param move: the move candidate branch
            :return: the value of the scoring function of a branch
            """

            q = node.get_move_expected_value(move)
            p = node.get_move_prior(move)
            n = node.get_move_visit_num(move)
            return q + self.c * p * np.sqrt(N) / (n + 1)

        return max(node.get_moves(), key=score_branch)

    def select_move(self, game_state):
        root = self.create_node(game_state)

        for i in range(self.num_rounds):
            # 1. find the next move branch to be added to the tree
            node = root
            next_move = self.find_branch(node)

            # 2. create the new tree node
            new_state = node.board_state.after_move(next_move)
            child_node = self.create_node(new_state, parent=node)

            # 3. add the new node to the tree
            node.add_child(next_move, child_node)

            # 4. update the stored data
            move = next_move
            value = -1 * child_node.state_value
            while node is not None:
                node.record_visit(move, value)
                move = node.last_move
                node = node.parent
                value = -1 * value

        if self.collector is not None:
            root_state = self.encoder.encode(game_state)
            moves = [index for index in range(self.encoder.num_moves())]
            visit_number = np.array([root.get_move_visit_num(index) for index in moves])
            self.collector.record_decision(root_state, visit_number)

        return max(root.get_moves(), key=root.get_move_visit_num)

    def find_branch(self, node):
        next_move = self.select_branch(node)
        # the move has already been added to the search tree
        while node.has_child(next_move):
            node = node.get_child(next_move)
            next_move = self.select_branch(node)

        return next_move

    def train(self, experience):
        num_examples = experience.states.shape[0]

        input_data = experience.states

        visit_sums = np.sum(experience.visit_number, axis=1).reshape((num_examples, 1))
        action_target = experience.visit_number / visit_sums
        value_target = experience.rewards

        self.model.compile(keras.optimizers.SGD(lr=self.lr), loss=['categorical_crossentropy', 'mse'])
        self.model.fit(input_data, [action_target, value_target], batch_size=self.batch_size)

def game_simulation(board_size,
                    black_agent,
                    black_collector,
                    white_agent,
                    white_collector):
    print('**********game start***********')
    game = GameState.new_game(board_size)
    agents = {
        Player.black: black_agent,
        Player.white: white_agent
    }

    black_collector.begin_episode()
    white_collector.begin_episode()
    while not game.is_over():
        next_move = agents[game.next_player].select_move(game)
        game = game.after_move(next_move)

    game_result = scoring.compute_game_result(game)
    if game_result.winner == Player.black:
        black_collector.complete_episode(1)
        white_collector.complete_episode(-1)
    else:
        black_collector.complete_episode(-1)
        white_collector.complete_episode(1)



