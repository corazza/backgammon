from re import L
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
    print(f'Player: {player_marking}')
    print(f'Roll: {roll}')
    state.print_board(board, player)
    can_move = board.can_move(player)
    while True and can_move:
        choice = input(f'input: <n> | <n m> | bar | bar bar | exit: ')
        if choice == 'exit':
            exit()
        elif choice == 'bar':
            move = [state.BarSource()]
        elif choice == 'bar bar':
            move = [state.BarSource(), state.BarSource()]
        elif ' ' in choice:
            (n, m) = choice.split(' ')
            (n, m) = (int(n) - 1, int(m) - 1)
            move = [state.BoardSource(n), state.BoardSource(m)]
        else:
            n = int(choice) - 1
            move = [state.BoardSource(n)]
        move_result = state.execute_move(board, player, move, roll, report=True)
        if not move_result.success():
            print('ILLEGAL MOVE:')
            move_result.print_reason()
            continue
        else:
            board = move_result.content
            break

    if not can_move:
        print('No viable moves, forfeiting turn')

    roll = dice.dice_roll()
    player = state.Board.opponent_token(player)
    print('=============\n')
