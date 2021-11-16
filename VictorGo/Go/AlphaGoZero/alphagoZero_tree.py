# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-23-6:12 下午

class Branch:
    def __init__(self, prior):
        self.prior = prior
        self.visit_num = 0
        self.total_value = 0.0

class TreeNode:
    def __init__(self, board_state, state_value, priors, parent, last_move):
        self.board_state = board_state
        self.state_value = state_value
        self.parent = parent
        self.last_move = last_move
        self.total_visit_count = 1
        self.branches = {}
        for move, prob in priors.items():
            if board_state.is_valid_move(move):
                self.branches[move] = Branch(prob)
        self.children = {}

    def get_moves(self):
        return self.branches.keys()

    def add_child(self, move, child_node):
        self.children[move] = child_node

    def has_child(self, move):
        return move in self.children

    def get_child(self, move):
        return self.children[move]

    def get_move_expected_value(self, move):
        branch = self.branches[move]
        if branch.visit_num == 0:
            return 0.0
        else:
            return branch.total_value / branch.visit_num

    def get_move_prior(self, move):
        return self.branches[move].prior

    def get_move_visit_num(self, move):
        if move in self.branches:
            return self.branches[move].visit_num
        else:
            return 0

    def record_visit(self, move, value):
        self.total_visit_count += 1
        self.branches[move].visit_num += 1
        self.branches[move].total_value += value




