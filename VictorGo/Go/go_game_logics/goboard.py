# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-07-10:14 下午
import copy
from Go.go_game_logics.go_elements import Player, Move, Point, GoString
from Go.go_game_logics import zobrist


class Board:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        '''
        keep track of the state of the board, and it is used to store the go string
        of each point
        '''
        self._grid_string = {}
        self._hash_code = zobrist.EMPTY_BOARD

    def zobrist_hash(self):
        return self._hash_code

    def place_stone(self, player, point):
        """
        place stone on the board
        :param player: the stone to be put
        :param point: the corresponding point
        :return: the updated board state
        """
        # check if the cross point is inside the boundary of the board.
        assert self.is_on_grid(point)
        # check if there is a stone on the cross point
        assert self._grid_string.get(point) is None

        adjacent_same_color = []
        adjacent_opposite_color = []
        liberties = []

        '''
        1. check the neighbor points of the stone to be places
        '''
        for neighbor in point.neighbors():
            if not self.is_on_grid(neighbor):
                continue
            # if the neighbor of the point exist, then get the content of that point
            neighbor_string = self._grid_string.get(neighbor)
            # if there is no stone on the point, then regard that point as one liberty.
            if neighbor_string is None:
                liberties.append(neighbor)
            # if there is a stone on the point, and the color of that stone is the
            # same as that of the player
            elif neighbor_string.color == player:
                if neighbor_string not in adjacent_same_color:
                    adjacent_same_color.append(neighbor_string)
            else:
                if neighbor_string not in adjacent_opposite_color:
                    adjacent_opposite_color.append(neighbor_string)
        new_string = GoString(player, [point], liberties)

        '''
        2. Update the state of each string on the board
        '''
        # 1. merge go strings with the same color
        for same_color_string in adjacent_same_color:
            new_string = new_string.merge_with(same_color_string)

        # 2. update the string of each point on the board
        for new_string_point in new_string.stones:
            self._grid_string[new_string_point] = new_string

        self._hash_code ^= zobrist.HASH_CODE[point, player]

        # 3. reduce the liberty of the go string with opposite color
        for other_color_string in adjacent_opposite_color:
            updated_go_string = other_color_string.without_liberty(point)
            if updated_go_string.num_liberties:
                for point in updated_go_string.stones:
                    self._grid_string[point] = updated_go_string
            else:
                self._remove_string(other_color_string)

    def _remove_string(self, string):
        """
        Take the go string (stones) away
        :param string: the string to be moved
        :return: the updated string state
        """
        for point in string.stones:
            # check the neighbor of each point in the string

            for neighbor in point.neighbors():
                # get the go string of each neighbor stone
                neighbor_string = self._grid_string.get(neighbor)
                if neighbor_string is None:
                    continue
                # if the neighbor string is different from the string to be moved
                if neighbor_string is not string:
                    # add the current point as the liberty of the neighbor string
                    updated_go_string = neighbor_string.with_liberties(point)
                    for p in updated_go_string.stones:
                        self._grid_string[p] = updated_go_string

            # set the string of this point as None
            self._grid_string[point] = None

            # update the state of the board
            self._hash_code ^= zobrist.HASH_CODE[point, string.color]

    def is_on_grid(self, point):
        """

        :param point: the point
        :return: judge whether the point is on the board
        """
        return 1 <= point.row <= self.num_rows and \
               1 <= point.col <= self.num_cols

    def get(self, point):
        """
        :param point: the value of point
        :return: if there is stone on the point, then return that stone; otherwise, return None
        """
        string = self._grid_string.get(point)
        if string is None:
            return None
        return string.color

    def get_go_string(self, point):
        """
        :param point: the point
        :return: the belonging string of the input point
        """
        string = self._grid_string.get(point)
        if string is None:
            return None
        return string


class GameState:
    """
    this class is used to record the state of the current game.
    the state of the game is defined as
    the current state of the board,
    the next player,
    the previous game state
    and the previous move.
    """

    def __init__(self, board, next_player, last_state, last_move):
        self.current_board = board
        self.next_player = next_player
        self.last_state = last_state

        # the previous states are used zobrist hash code to represent
        if self.last_state is None:
            self.previous_states = frozenset()
        else:
            self.previous_states = frozenset(
                last_state.previous_states |
                {(last_state.next_player, last_state.current_board.zobrist_hash())}
            )
        self.last_move = last_move

    def after_move(self, move):
        """
        :param move: the move
        :return: the new state of the game of move
        """
        if move.is_play:
            next_board = copy.deepcopy(self.current_board)
            next_board.place_stone(self.next_player, move.point)
        else:
            next_board = self.current_board
        return GameState(next_board, self.next_player.other, self, move)

    @classmethod
    def new_game(cls, board_size):
        """
        :param board_size: the board size of the game
        :return: the new game state
        """
        if isinstance(board_size, int):
            board_size = (board_size, board_size)
        board = Board(*board_size)
        return GameState(board, Player.black, None, None)

    def is_over(self):
        """
        if the current state is the beginning of the game, the game is obviously not over;
        if the last move is resign, the game is over;
        if the game only go towards to the second scene, the game cannot be over;
        as for the remaining cases, only both the two players choose to pass the game will
        the game is over.
        :return:
        """
        if self.last_move is None:
            return False
        if self.last_move.is_resign:
            return True
        second_last_move = self.last_state.last_move
        if second_last_move is None:
            return False
        return self.last_move.is_pass and second_last_move.is_pass

    def is_move_self_capture(self, player, move):
        """
        check is the self_capture is illegal by copying the current board
        :param player:
        :param move:
        :return: bool value
        """
        if not move.is_play:
            return False
        next_board = copy.deepcopy(self.current_board)
        next_board.place_stone(player, move.point)
        new_string = next_board.get_go_string(move.point)
        return new_string.num_liberties == 0

    @property
    def situation(self):
        """
        :return: the tuple of the next player and the state of the current board
        """
        return self.next_player, self.current_board

    def does_move_violate_ko(self, player, move):
        """
        judge whether the move causes ko
        :param player:
        :param move:
        :return: bool value to judge whether the ko occurs or not
        """
        if not move.is_play:
            return False

        next_board = copy.deepcopy(self.current_board)
        next_board.place_stone(player, move.point)
        next_situation = (player.other, next_board.zobrist_hash())
        return next_situation in self.previous_states

    def is_valid_move(self, move):
        if self.is_over():
            return False
        if move.is_pass or move.is_resign:
            return True
        return (self.current_board.get(move.point) is None and
                not self.is_move_self_capture(self.next_player, move) and
                not self.does_move_violate_ko(self.next_player, move))

    def legal_moves(self):
        """
        :return: the legal moves in this game state
        """
        moves = []
        for row in range(1, self.current_board.num_rows + 1):
            for col in range(1, self.current_board.num_cols + 1):
                move = Move.play(Point(row, col))
                if self.is_valid_move(move):
                    moves.append(move)

        moves.append(Move.pass_turn())
        moves.append(Move.resign())


def is_point_an_eye(board, point, color):
    if board.get(point) is not None:
        return False
    for neighbor in point.neighbors():
        if board.is_on_grid(neighbor):
            neighbor_color = board.get(neighbor)
            # all the neighbors' color should be the same as the player
            if neighbor_color != color:
                return False

    friendly_corners = 0
    off_board_corners = 0
    corners = [
        Point(point.row-1, point.col-1),
        Point(point.row-1, point.col+1),
        Point(point.row+1, point.col-1),
        Point(point.row+1, point.col+1),
    ]

    for corner in corners:
        if board.is_on_grid(corner):
            corner_color = board.get(corner)
            if corner_color == color:
                friendly_corners += 1
        else:
            off_board_corners += 1

    # the point is at the boundary of the board or the corner of the board
    if off_board_corners > 0:
        return off_board_corners + friendly_corners == 4

    # the point is inside the board
    return friendly_corners >= 3

