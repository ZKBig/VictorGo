# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-10-9:40 上午
from Go.agent import naive
from Go.go_fundations import utils
from Go.go_game_logics import go_elements, goboard
from six.moves import input

def main():
    board_size = 9
    game = goboard.GameState.new_game(board_size)
    bot = naive.RandomBot()

    while not game.is_over():
        print(chr(27)+"[2J")
        utils.print_board(game.current_board)
        if game.next_player == go_elements.Player.black:
            human_turn = input('Please enter the point coordinate: ')
            point = utils.coordinates_to_point(human_turn.strip())
            move = goboard.Move.play(point)
        else:
            move = bot.select_move(game)
        utils.print_move(game.next_player, move)
        game = game.after_move(move)

if __name__=="__main__":
    main()