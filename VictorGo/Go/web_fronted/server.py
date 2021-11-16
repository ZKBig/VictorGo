# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-20-8:04 下午
import os

from flask import Flask
from flask import jsonify
from flask import request

from Go.go_game_logics import goboard
from Go.go_fundations.utils import coordinates_to_point
from Go.go_fundations.utils import point_to_coordinates

__all__ = [
    'get_web_app',
]


def get_web_app(bot_map):
    """Create a flask application for serving bot moves.
    The bot_map maps from URL path fragments to Agent instances.
    The /static path will return some static content (including the
    jgoboard JS).
    Clients can get the post move by POSTing json to
    /select-move/<bot name>
    Returns: Flask application instance
    """
    here = os.path.dirname(__file__)
    static_path = os.path.join(here, 'static')
    app = Flask(__name__, static_folder=static_path, static_url_path='/static')

    @app.route('/select-move/<bot_name>', methods=['POST'])
    def select_move(bot_name):
        content = request.json
        board_size = content['board_size']
        game_state = goboard.GameState.new_game(board_size)
        # Replay the game up to this point.
        for move in content['moves']:
            if move == 'pass':
                next_move = goboard.Move.pass_turn()
            elif move == 'resign':
                next_move = goboard.Move.resign()
            else:
                next_move = goboard.Move.play(coordinates_to_point(move))
            game_state = game_state.apply_move(next_move)
        bot_agent = bot_map[bot_name]
        bot_move = bot_agent.select_move(game_state)
        if bot_move.is_pass:
            bot_move_str = 'pass'
        elif bot_move.is_resign:
            bot_move_str = 'resign'
        else:
            bot_move_str = point_to_coordinates(bot_move.point)
        return jsonify({
            'bot_move': bot_move_str,
            'diagnostics': bot_agent.diagnostics()
        })

    return app