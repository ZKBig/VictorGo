# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-09-12:14 下午
import random
from Go.agent.base import Agent
from Go.agent.helpers import is_point_an_eye
from Go.go_fundations.goboard_slow import Move
from Go.go_game_logics.go_elements import Point

class RandomBot(Agent):
    def select_move(self, game_state):
        """
        choose a random valid move that preserves our own eyes.
        :param game_state:
        :return:
        """

        move_candidates = []
        for r in range(1, game_state.current_board.num_rows + 1):
            for c in range(1, game_state.current_board.num_cols + 1):
                move_candidate = Point(row=r, col=c)
                if game_state.is_valid_move(Move.play(move_candidate)) and \
                    not is_point_an_eye(game_state.current_board, move_candidate, game_state.next_player):
                    move_candidates.append(move_candidate)

        if not move_candidates:
            return Move.pass_turn()
        return Move.play(random.choice(move_candidates))


