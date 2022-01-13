import sys
import tree
import state

def heuristic_value(node):
    if node.player == tree.Node.PLAYER_AI:
        node = node.parent
    token = tree.player_to_token(node.player)
    (my_points, opponent_points) = node.state.points_for(token)
    my_bar = node.state.bar_for(token)
    checkers_on_board = 0
    score = 0
    for i in range(state.NUM_POINTS):
        if token == state.Board.TOKEN_ONE:
            multiplier = state.NUM_POINTS - i
        elif token == state.Board.TOKEN_TWO:
            multiplier = i
        score += my_points[i] * multiplier - opponent_points[i] * (state.NUM_POINTS - multiplier)
        checkers_on_board += my_points[i]
    score += state.NUM_POINTS * (state.NUM_CHECKERS - checkers_on_board - my_bar) * 2
    return score

def expectiminimax(node, depth):
    if node.is_terminal() or depth == 0:
        return heuristic_value(node)
    value = None

    if node.player == tree.Node.PLAYER_AI:
        for child in node.children():
            child_value = expectiminimax(child, depth-1)
            value = min(value, child_value) if value is not None else child_value
    elif node.player == tree.Node.PLAYER_HUMAN:
        for child in node.children():
            child_value = expectiminimax(child, depth-1)
            value = max(value, child_value) if value is not None else child_value
    else: # node.player == tree.Node.PLAYER_CHANCE
        value = 0
        for child in node.children():
            child_value = expectiminimax(child, depth-1)
            value = value + (child.probability() * child_value)

    node.value = value
    return value
