import expectiminimax as emm
import tree
import dice
import state

dice.init() # seed

first_roll = dice.first_roll() # (ai roll, human roll)
roll = first_roll
first_player = state.Board.TOKEN_ONE if first_roll[0] > first_roll[1] else state.Board.TOKEN_TWO
player = first_player
board = state.initial_board()

while not board.is_terminal():
    print(f'Player: {player}')
    print(f'Roll: {roll}')
    board.print()
    choice = input(f'select points n OR n m:')
    if ' ' in choice:
        (n, m) = choice.split(' ')
        move = [state.BoardSource(n), state.BoardSource(m)]
        assert(board.can_move_to(player, move[0], move[0].get_destination[0]))
        board = state.execute_move(board, player, move[0], move[0].get_destination(roll[0]))
        assert(board.can_move_to(player, move[1], move[1].get_destination[1]))
        board = state.execute_move(board, player, move[1], move[1].get_destination(roll[1]))
    else:
        n = int(choice)
        move = [state.BoardSource(n)]
        assert(board.can_move_to(player, move[0], move[0].get_destination[0]))
        board = state.execute_move(board, player, move[0], move[0].get_destination(roll[0]))
    roll = dice.dice_roll()
    player = state.Board.opponent_token(player)
