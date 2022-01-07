import sys
import tree

def expectiminimax(node, depth):
    if node.is_terminal() or depth == 0:
        return 0 # the heuristic value of node

    value = None

    if node.player == tree.PLAYER_AI:
        for child in node.children():
            child_value = expectiminimax(child, depth-1)
            value = min(value, child_value) if value is not None else child_value
    elif node.player == tree.PLAYER_HUMAN:
        for child in node.children():
            child_value = expectiminimax(child, depth-1)
            value = max(value, child_value) if value is not None else child_value
    else: # node.player == tree.PLAYER_CHANCE
        value = 0
        for child in node.children():
            child_value = expectiminimax(child, depth-1)
            value = value + (child.probability() * child_value)

    node.value = value
    return value
