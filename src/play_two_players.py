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
    player_marking = state.Board.token_marking(player)
    print(f'Player: {player_marking}')
    print(f'Roll: {roll}')
    board.print(player)
    choice = input(f'select points n OR n m OR exit: ')
    if choice == 'exit':
        exit()
    if ' ' in choice:
        (n, m) = choice.split(' ')
        (n, m) = (int(n) - 1, int(m) - 1)
        move = [state.BoardSource(n, player), state.BoardSource(m)]
        assert(board.can_move_to(player, move[0], move[0].get_destination(roll[0], player)))
        board = state.execute_move(board, player, move[0], move[0].get_destination(roll[0], player))
        assert(board.can_move_to(player, move[1], move[1].get_destination(roll[1], player)))
        board = state.execute_move(board, player, move[1], move[1].get_destination(roll[1], player))
    else:
        n = int(choice) - 1
        move = [state.BoardSource(n)]
        assert(board.can_move_to(player, move[0], move[0].get_destination(roll[0], player)))
        board = state.execute_move(board, player, move[0], move[0].get_destination(roll[0], player))
        move = [state.BoardSource(n+roll[0])]
        assert(board.can_move_to(player, move[0], move[0].get_destination(roll[0], player)))
        board = state.execute_move(board, player, move[0], move[0].get_destination(roll[0], player))
    roll = dice.dice_roll()
    player = state.Board.opponent_token(player)

# TODO here movement is in the negative direction!
