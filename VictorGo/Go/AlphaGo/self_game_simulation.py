# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-21-5:21 下午
from Go.go_fundations import scoring
from Go.go_game_logics.goboard import Player, GameState
from Go.AlphaGo import experience


def simulate_game(black_player, white_player, board_size):
    game = GameState.new_game(board_size)
    moves = []
    agents = {
        Player.black: black_player,
        Player.white: white_player,
    }

    while not game.is_over():
        next_move = agents[game.next_player].select_move(game)
        moves.append(next_move)
        game = game.after_move(next_move)

    game_result = scoring.compute_game_result(game)

    return game_result

def experience_simulator(num_games, agent1, agent2):
    collector1 = experience.ExperienceCollector()
    collector2 = experience.ExperienceCollector()

    color = Player.black
    for i in range(num_games):
        collector1.begin_episode()
        collector2.begin_episode()
        agent1.set_collector(collector1)
        agent2.set_collector(collector2)

        if color == Player.black:
            black_player, white_player = agent1, agent2
        else:
            black_player, white_player = agent2, agent1
        game_record = simulate_game(black_player, white_player)
        if game_record.winner == color:
            collector1.complete_episode(reward=1)
            collector2.complete_episode(reward=-1)
        else:
            collector1.complete_episode(reward=-1)
            collector2.complete_episode(reward=1)
        color = color.other

    return experience.combine_experience([collector1, collector2])




