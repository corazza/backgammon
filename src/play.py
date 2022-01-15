from expectiminimax import expectiminimax
from tree import *
import dice
import state
from result import *

import IPython

EMM_DEPTH = 4

dice.init() # seed

def play(player_one_ai, player_two_ai):
    first_roll = dice.first_roll() # (ai roll, human roll)
    first_player = Node.PLAYER_ONE if first_roll[0] > first_roll[1] else Node.PLAYER_TWO
    current_node = initial_node(dice.disregard_order(first_roll), first_player)
    player_marking = None

    while not current_node.is_terminal():
        board = current_node.state
        player = current_node.player

        if player is Node.PLAYER_CHANCE:
            new_roll = dice.disregard_order(dice.dice_roll())
            opponent = current_node.opponent()
            current_node = ActionNode(opponent, board, None, new_roll, None)
            current_node.deleteTree()
        else:
            move = None
            input_move = (player is Node.PLAYER_ONE and not player_one_ai) or (player is Node.PLAYER_TWO and not player_two_ai)
            roll = current_node.roll
            move_twice = roll[0] == roll[1]
            move_twice = False
            token = player_to_token(player)
            player_marking = f'{state.Board.token_marking(token)} ({Node.player_marking(player, player_one_ai, player_two_ai)})'
            print(f'Player: {player_marking}')
            print(f'Roll: {roll}')
            state.print_board(board, player)
            if not board.can_move(token, roll):
                print('No viable moves, forfeiting turn')
            else:
                if input_move:
                    choices = []
                    while len(choices) == 0 or (move_twice and len(choices) == 1):
                        choice = input(f'input: <n> | <n m> | bar | bar bar | exit: ')
                        if choice == 'exit':
                            exit()
                        elif choice == 'bar':
                            choices.append([state.BarSource()])
                        elif choice == 'bar bar':
                            choices.append([state.BarSource(), state.BarSource()])
                        elif ' ' in choice:
                            (n, m) = choice.split(' ')
                            (n, m) = (int(n) - 1, int(m) - 1)
                            choices.append([state.BoardSource(n), state.BoardSource(m)])
                        else:
                            n = int(choice) - 1
                            choices.append([state.BoardSource(n)])
                        move_result = Success()
                        for choice in choices:
                            move_result = move_result.next(state.execute_move(board, player, choice, roll, report=True))
                        if not move_result.success():
                            print('ILLEGAL MOVE:')
                            print(move)
                            move_result.print_reason()
                            continue
                        else:
                            chosen = True
                else:
                    expectiminimax(current_node, EMM_DEPTH, current_node.player)
                    children = current_node.children()
                    max_value_child = children[0]
                    for child in children:
                        if child.value > max_value_child.value:
                            max_value_child = child
                    move = max_value_child.move
                if not state.execute_move(board, player, move, roll, report=False).success():
                    IPython.embed()
                board = state.execute_move(board, player, move, roll, report=True).content
            current_node = RandomNode(board, current_node, None)
            print('=============\n')

    print(f'Winner: {player_marking}')
