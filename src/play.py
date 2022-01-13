from expectiminimax import expectiminimax
from tree import *
import dice
import state

dice.init() # seed

first_roll = dice.first_roll() # (ai roll, human roll)
first_player = Node.PLAYER_AI if first_roll[0] > first_roll[1] else Node.PLAYER_HUMAN
current_node = initial_node(first_roll, first_player)

while not current_node.is_terminal():
    board = current_node.state
    player = current_node.player

    if player is Node.PLAYER_CHANCE:
        new_roll = dice.dice_roll()
        if current_node.parent.player == Node.PLAYER_AI:
            current_node = HumanNode(board, current_node, new_roll)
        else:
            current_node = AINode(board, current_node, new_roll)
    else:
        roll = current_node.roll
        token = player_to_token(player)
        player_marking = f'{state.Board.token_marking(token)} ({Node.player_marking(player)})'
        print(f'Player: {player_marking}')
        print(f'Roll: {roll}')
        state.print_board(board, player)
        if not board.can_move(token):
            print('No viable moves, forfeiting turn')
        elif player is Node.PLAYER_HUMAN:
            while True:
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
        elif player is Node.PLAYER_AI:
            expectiminimax(current_node, 4, Node.PLAYER_AI)
            board = board
        current_node = RandomNode(board, current_node)