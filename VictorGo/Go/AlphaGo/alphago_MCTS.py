# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-23-3:08 下午
from Go.agent.base import Agent
from Go.go_game_logics.goboard import Move

import numpy as np
import operator

class AlphaGoNode:
    def __init__(self, parent=None, prob=1.0):
        '''

        :param parent:
        :param prob:
        '''
        self.parent = parent
        self.children = {}
        self.visit_count = 0
        self.q_value = 0
        self.action_value = prob
        self.u_value = prob

    def select_child(self):
        return max(self.children.items(), key=lambda child: child[1].q_value + child[1].u_value)

    def add_children(self, moves, probs):
        for move, prob in zip(moves, probs):
            if move not in self.children:
                self.children[move] = AlphaGoNode(prob=prob)

    def update_values(self, leaf_node_value):
        if self.parent is not None:
            # guarantee traversing the tree from the top tpo the bottom
            self.parent.update_values(leaf_node_value)

        self.visit_count += 1
        self.q_value += leaf_node_value / self.visit_count

        if self.parent is not None:
            c_u = 5
            self.u_value = c_u * np.sqrt(self.parent.visit_count) \
                * self.action_value / (1 + self.visit_count)

class AlphaGoMCTS(Agent):
    def __inti__(self,
                 policy_agent,
                 fast_policy_agent,
                 value_agent,
                 lambda_value=0.5,
                 num_simulations=1000,
                 depth=50,
                 rollout_limit=100):
        '''

        :param policy_agent:
        :param fast_policy_agent:
        :param value_agent:
        :param lambda_value: V(l) = lambda_value * value(l) + (1 - lambda_value) * rollout(l)
        :param num_simulations: then number of simulation process
        :param depth: the search depth
        :param rollout_limit: determines the time when the rollout is over
        :return:
        '''
        self.policy_agent = policy_agent
        self.rollout_policy_agent = fast_policy_agent
        self.value_agent = value_agent
        self.lambda_value = lambda_value
        self.num_simulations = num_simulations
        self.depth = depth
        self.rollout_limit = rollout_limit
        self.root = AlphaGoNode

    def select_move(self, game_state):
        for simulation in range(self.num_simulations):
            current_state = game_state
            node = self.root
            for depth in range(self.depth):
                if not node.children:
                    if current_state.is_over():
                        break
                    moves, probs = self.policy_probabilities(current_state)
                    node.add_children(moves, probs)

                move, node = node.select_child()
                current_state = current_state.after_move(move)

            value = self.value_agent.predict(current_state)
            rollout = self.policy_rollout(current_state)
            weighted_value = (1 - self.lambda_value) * value + self.lambda_value * rollout

            node.update_values(weighted_value)

        move = max(self.root.children, key=lambda move:self.root.children.get(move).visit_conut)
        self.root = AlphaGoNode
        if move in self.root.children:
            self.root = self.root.children[move]
            self.root.parent = None
        return move

    def policy_probabilities(self, game_state):
        encoder = self.policy_agent.encoder
        outputs = self.policy_agent.predict(game_state)
        legal_moves = game_state.legal_moves()
        if not legal_moves:
            return [], []
        encoded_points = [encoder.encode_point(move.point) for move in legal_moves if move.point]
        legal_outputs = outputs[encoded_points]
        # normalize the output probabilities
        normalized_outputs = legal_outputs / np.sum(legal_outputs)

        return legal_moves, normalized_outputs

    def policy_rollout(self, game_state):
        for step in range(self.rollout_limit):
            if game_state.is_over():
                break
            move_probabilities = self.rollout_policy_agent.predict(game_state)
            encoder = self.rollout_policy_agent.encoder
            # filter all the moves and retain all th legal moves
            valid_moves = [m for index, m in enumerate(move_probabilities)
                           if Move(encoder.decode_point_index(index)) in game_state.legal_moves()]

            max_index, max_value = max(enumerate(valid_moves), key=operator.itemgetter(1))
            max_point = encoder.decode_point_index(max_index)
            move = Move(max_point)
            game_state = game_state.after_move(move)

        next_player = game_state.next_player
        winner = game_state.winner
        if winner is not None:
            return 1 if winner == next_player else -1
        else:
            return 0



