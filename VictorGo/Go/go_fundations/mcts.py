# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-11-9:56 上午
from Go.go_game_logics import go_elements
from Go.agent.base import Agent
import random
import math

class MCTSNode(object):
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.win_counts = {
            go_elements.Player.black: 0,
            go_elements.Player.white: 0,
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = game_state.legal_moves()

    def add_child(self):
        index = random.randint(0, len(self.unvisited_moves)-1)
        new_move = self.unvisited_moves.pop(index)
        new_game_state = self.game_state.after_move(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner):
        self.win_counts[winner] += 1
        self.num_rollouts += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        return self.game_state.is_over()

    def winning_frac(self, player):
        return float(self.win_counts[player]) / float(self.num_rollouts)

class MCTAgent(Agent):
    def select_move(self, game_state):
        '''
        1. regard the current game state as the root node to create a new search tree.
        2. in each turn, traverse the tree from the root node until a new child node is found.
        3. when the new node is found, select the next_move using 'add_random+child'
           and add it to the tree.
        4. using 'simulate_random_game' to rollout the game
        5. update the information of the nodes.
        6. When all the rollouts are done, all the branches of the root node are needed checking,
           and the branch with the biggest value will be chosen .
        '''
        root = MCTSNode(game_state=game_state)

        for i in range(self.num_rounds):
            node = root
            # step 5:
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)

            if node.can_add_child():
                node = self.add_random_child()

            winner = self.simulate_random_game(node.game_state)

            while node is not None:
                node.record_win(winner)
                node = node.parent

        best_move = None
        best_pct = -1.0
        for child in root.children:
            child_pct = child.winning_frac(game_state.next_player)
            if child_pct > best_pct:
                best_pct = child_pct
                best_move = child.move
        return best_move

    def _uct_score(self, parent_rollouts, child_rollouts, win_pct, temperature):
        exploration = math.sqrt(math.log(parent_rollouts) / child_rollouts)
        return win_pct + temperature * exploration

    def select_child(self, node):
        '''

        :param node: the node that explores the branch with the biggest uct value
        :return: the node with the biggest uct value
        '''
        total_rollouts = sum(child.num_rollouts for child in node.children)

        best_score = -1
        best_child = None
        for child in node.children:
            uct_score = self._uct_score(total_rollouts, child.num_rollouts,
                                    child.winning_frac(node.game_state.next_player))
            if uct_score > best_score:
                best_score = uct_score
                best_child = child

        return best_child




