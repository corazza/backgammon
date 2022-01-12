import expectiminimax as emm
import dice
import state
import IPython

dice.init() # seed

first_roll = dice.first_roll() # (ai roll, human roll)
roll = first_roll
first_player = state.Board.TOKEN_ONE if first_roll[0] > first_roll[1] else state.Board.TOKEN_TWO
player = first_player
board = state.initial_board()

while not board.is_terminal():
    player_marking = state.Board.token_marking(player)
    (d1, d2) = roll
    print(f'Player: {player_marking}')
    print(f'Roll: {roll}')
    state.print_board(board, player)
    chosen_once = False
    while True:
        if chosen_once:
            print('ILLEGAL MOVE')
        chosen_once = True
        choice = input(f'input: <n> OR <n m> OR exit: ')
        if choice == 'exit':
            exit()
        if ' ' in choice:
            (n, m) = choice.split(' ')
            (n, m) = (int(n) - 1, int(m) - 1)
            move = [state.BoardSource(n), state.BoardSource(m)]
            if not move[0].destination_sanity(d1, player, print_reason=True):
                continue
            if board.valid(player, move[0], move[0].get_destination(d1, player), print_reason=True):
                new_board = state.move_one_checker(board, player, move[0], move[0].get_destination(d1, player), report=True)
                if not move[1].destination_sanity(d2, player, print_reason=True):
                    continue
                if new_board.valid(player, move[1], move[1].get_destination(d2, player), print_reason=True):
                    board = state.move_one_checker(new_board, player, move[1], move[1].get_destination(d2, player), report=True)
                    break
        else:
            n = int(choice) - 1
            move = [state.BoardSource(n)]
            if not move[0].destination_sanity(d1, player, print_reason=True):
                continue
            if board.valid(player, move[0], move[0].get_destination(d1, player), print_reason=True):
                new_board = state.move_one_checker(board, player, move[0], move[0].get_destination(d1, player), report=True)
                new_move = [state.BoardSource(move[0].get_destination(d1, player))]
                if not new_move[0].destination_sanity(d2, player, print_reason=True):
                    continue
                if new_board.valid(player, new_move[0], new_move[0].get_destination(d2, player), print_reason=True):
                    board = state.move_one_checker(new_board, player, new_move[0], new_move[0].get_destination(d2, player), report=True)
                    break

    roll = dice.dice_roll()
    player = state.Board.opponent_token(player)
    print('=============\n')
