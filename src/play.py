import expectiminimax as emm
import tree
import dice

dice.init() # seed

first_roll = dice.first_roll() # (ai roll, human roll)
first_player = tree.PLAYER_AI if first_roll[0] > first_roll[1] else tree.PLAYER_HUMAN
current_node = tree.initial_node(first_roll, first_player)

while not current_node.is_terminal():
    if current_node.player == tree.PLAYER_HUMAN:
        children = current_node.children()
        print(f'Your roll: {current_node.roll}')
        choice = int(input(f'Choose child 0-{len(children)-1}: '))
        chosen_child = children[choice]
        for child in children:
            if child is not chosen_child:
                child.deleteTree()
        current_node = chosen_child
    elif current_node.player == tree.PLAYER_AI:
        assert(isinstance(current_node, tree.ActionNode))
        assert(current_node.player == tree.PLAYER_AI)
        emm.expectiminimax(current_node, 4, tree.PLAYER_AI)
    else: # current_node.player == tree.PLAYER_CHANCE
        roll = dice.dice_roll()
        if current_node.parent.player == tree.PLAYER_AI:
            current_node = tree.HumanNode(current_node.state, current_node, roll)
        else:
            current_node = tree.RandomNode(current_node.state, current_node, roll)
