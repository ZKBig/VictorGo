# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-09-12:51 下午
from Go.agent import naive
from Go.go_fundations import goboard_slow
from Go.go_game_logics import go_elements
from Go.go_fundations.utils import print_move, print_board
import time

def main():
    board_size = 9
    game = goboard_slow.GameState.new_game(board_size)
    bots = {
        go_elements.Player.black: naive.RandomBot(),
        go_elements.Player.white: naive.RandomBot(),
    }
    while not game.is_over():
        time.sleep(0.3)

        print(chr(27)+"[2J")
        print_board(game.current_board)
        bot_move = bots[game.next_player].select_move(game)
        print_move(game.next_player, bot_move)
        game = game.after_move(bot_move)

if __name__=='__main__':
    main()