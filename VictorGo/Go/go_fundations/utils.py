# -*- coding: utf-8 -*-
# @Description:
# @author: victor
# @create time: 2021-08-09-12:43 下午
from Go.go_game_logics import go_elements

COLS_MARK = 'ABCDEFGHJKLMNOPQRST'
STONE_TO_CHAR = {
    None: '.',
    go_elements.Player.black: 'x',
    go_elements.Player.white: 'o',
}

def print_move(player, move):
    if move.is_pass:
        move_str = 'passes'
    elif move.is_resign:
        move_str = 'resigns'
    else:
        move_str = '%s%d' % (COLS_MARK[move.point.col-1], move.point.row)
    print('%s %s' % (player, move_str))

def print_board(board):
    for row in range(board.num_rows, 0, -1):
        bump = " " if row <= 9 else ""
        line = []
        for col in range(1, board.num_cols+1):
            stone = board.get(go_elements.Point(row=row, col=col))
            line.append(STONE_TO_CHAR[stone])
        print('%s%d %s' % (bump, row, ''.join(line)))

    print('   '+''.join(COLS_MARK[:board.num_cols]))

def coordinates_to_point(coordinates):
    col = COLS_MARK.index(coordinates[0]) + 1
    row = int(coordinates[1:])
    return go_elements.Point(row=row, col=col)

def point_to_coordinates(point):
    return '%s%d'%(
        COLS_MARK[point.col - 1],
        point.row
    )

