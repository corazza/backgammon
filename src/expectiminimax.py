from telnetlib import IP
import tree
import state

import IPython
from profilehooks import profile
import math

BAR_MULTIPLIER = 2*math.log(state.NUM_POINTS+1, 2)
BEAR_OFF_MULTIPLIER = 3*math.log(state.NUM_POINTS+1, 2)

def score_for(node, token):
    (my_points, _opponent_points) = node.state.points_for(token)
    my_bar = node.state.bar_for(token)
    checkers_on_board = sum(my_points)
    score = 0
    for i in range(state.NUM_POINTS):
        if token == state.Board.TOKEN_ONE:
            multiplier = state.NUM_POINTS - i
        elif token == state.Board.TOKEN_TWO:
            multiplier = i+1
        score += my_points[i] * math.log(multiplier, 2)
    score += BEAR_OFF_MULTIPLIER * (state.NUM_CHECKERS - checkers_on_board - my_bar)
    score -= BAR_MULTIPLIER * my_bar
    return score

def heuristic_value(node):
    if node.player is tree.Node.PLAYER_CHANCE:
        node = node.parent
    token = tree.player_to_token(node.player)
    my_score = score_for(node, token)
    opponent_token = state.Board.opponent_token(token)
    opponent_score = score_for(node, opponent_token)
    return my_score - opponent_score

# @profile(sort='tottime')
def expectiminimax(node, depth, playing_as):
    if node.is_terminal() or depth == 0:
        node.value = heuristic_value(node)
    else:
        value = None
        if node.player == tree.Node.PLAYER_CHANCE:
            value = 0
            for child in node.children():
                child_value = expectiminimax(child, depth-1, playing_as)
                value += child.probability() * child_value
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
