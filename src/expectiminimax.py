import tree
import state

import IPython
from profilehooks import profile

BEAR_OFF_MULTIPLIER = state.NUM_POINTS + 2
BAR_MULTIPLIER = state.NUM_POINTS + 100

def heuristic_value(node):
    if node.player is tree.Node.PLAYER_CHANCE:
        node = node.parent
    token = tree.player_to_token(node.player)
    opponent_token = state.Board.opponent_token(token)
    (my_points, opponent_points) = node.state.points_for(token)
    my_bar = node.state.bar_for(token)
    opponent_bar = node.state.bar_for(opponent_token)
    checkers_on_board = sum(my_points)
    score = 0
    for i in range(state.NUM_POINTS):
        if token == state.Board.TOKEN_ONE:
            multiplier = state.NUM_POINTS - i
        elif token == state.Board.TOKEN_TWO:
            multiplier = i
        score += my_points[i] * multiplier - opponent_points[i] * (state.NUM_POINTS - multiplier)
    score += BEAR_OFF_MULTIPLIER * (state.NUM_CHECKERS - checkers_on_board - my_bar)
    score += BAR_MULTIPLIER * (opponent_bar - my_bar)
    return score

# @profile(sort='tottime')
def expectiminimax(node, depth, playing_as):
    if node.is_terminal() or depth == 0:
        node.value = heuristic_value(node)
    else:
        value = 0
        if node.player == tree.Node.PLAYER_CHANCE:
            for child in node.children():
                child_value = expectiminimax(child, depth-1, playing_as)
                value = value + (child.probability() * child_value)
        elif node.player == playing_as:
            for child in node.children():
                child_value = expectiminimax(child, depth-1, playing_as)
                value = max(value, child_value) if value is not None else child_value
        elif node.player != playing_as:
            for child in node.children():
                child_value = expectiminimax(child, depth-1, playing_as)
                value = min(value, child_value) if value is not None else child_value
        node.value = value
    return node.value
