import state
import dice

PLAYER_AI = 0 # maybe introspection is slow?
PLAYER_HUMAN = 1
PLAYER_CHANCE = 2

def player_to_token(player):
    assert(player is not PLAYER_CHANCE)
    return state.TOKEN_ONE if player is PLAYER_AI else state.TOKEN_TWO

class Node:
    def __init__(self, player, state, parent):
        self.player = player
        self.state = state
        self.parent = parent
        self.value = None
        self._children = None

    def children(self):
        if self._children is None:
            self._generate_children()
        return self._children

    def probability(self): # from parent_children
        raise NotImplementedError() 

    def is_terminal(self):
        return state.is_terminal(self.state)
    
    def deleteTree(self):
        for child in self._children:
            child.deleteTree()
            self._children = None

    def _generate_children(self):
        raise NotImplementedError()

class RandomNode(Node):
    def __init__(self, state, parent):
        super().__init__(PLAYER_CHANCE, state, parent)
    
    def probability(self):
        raise ValueError("Random nodes should never be asked for probability")

    def is_terminal(self):
        return ValueError("Random nodes cannot be terminal regardless of their state")

    def _generate_children(self):
        if self.parent.player == PLAYER_AI:
            self._children = [HumanNode(self.state, self, roll) for roll in dice.all_rolls()]
        else:
            self._children = [AINode(self.state, self, roll) for roll in dice.all_rolls()]
            
class ActionNode(Node):
    def __init__(self, player, state, parent, roll):
        self.roll = roll
        super().__init__(player, state, parent)
    
    def probability(self):
        return 1.0 / len(self.parent.children())

    def _generate_children(self):
        self._children = state.children(self.parent.state, self.roll, player_to_token(self.parent.player))

class HumanNode(ActionNode):
    def __init__(self, state, parent, roll):
        super().__init__(PLAYER_HUMAN, state, parent, roll)

class AINode(ActionNode):
    def __init__(self, state, parent, roll):
        super().__init__(PLAYER_AI, state, parent, roll)

def initial_node(roll, player):
    initial_state = state.initial_board()
    if player == PLAYER_AI:
        return AINode(initial_state, None, roll)
    else:
        return HumanNode(initial_state, None, roll)
