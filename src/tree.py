import state
import dice

def player_to_token(player):
    assert(player is not Node.PLAYER_CHANCE)
    return state.Board.TOKEN_ONE if player is Node.PLAYER_TWO else state.Board.TOKEN_TWO

class Node:
    PLAYER_TWO = 0 # maybe introspection is slow?
    PLAYER_ONE = 1
    PLAYER_CHANCE = 2
    def __init__(self, player, state, parent, move):
        self.player = player
        self.state = state
        self.parent = parent
        self.move = move
        self.value = None
        self._children = None

    def children(self):
        if self._children is None:
            self._generate_children()
        return self._children

    def probability(self): # from parent_children
        raise NotImplementedError() 

    def is_terminal(self):
        return self.state.is_terminal()
    
    def deleteTree(self):
        if self._children is not None:
            for child in self._children:
                child.deleteTree()
            self._children = None

    def _generate_children(self):
        raise NotImplementedError()

    def player_marking(player, player_one_ai, player_two_ai):
        if player is Node.PLAYER_CHANCE:
            return "Chance"
        elif player is Node.PLAYER_ONE and not player_one_ai or player is Node.PLAYER_TWO and not player_two_ai:
            return "Human"
        else:
            return "AI"

class RandomNode(Node):
    def __init__(self, state, parent, move):
        super().__init__(Node.PLAYER_CHANCE, state, parent, move)
    
    def probability(self):
        raise ValueError("Random nodes should never be asked for probability")

    def is_terminal(self):
        return False

    def _generate_children(self):
        if self.parent.player == Node.PLAYER_TWO:
            self._children = [HumanNode(self.state, self, roll, self.move) for roll in dice.all_rolls()]
        else:
            self._children = [AINode(self.state, self, roll, self.move) for roll in dice.all_rolls()]
            
class ActionNode(Node):
    def __init__(self, player, state, parent, roll, move):
        self.roll = roll
        super().__init__(player, state, parent, move)
    
    def probability(self):
        return 1.0 / 36 if self.roll[0] == self.roll[1] else 2.0 / 36

    def _generate_children(self):
        self._children = list()
        for (move, child) in state.children(self.state, self.roll, player_to_token(self.player)):
            self._children.append(RandomNode(child, self, move))

class HumanNode(ActionNode):
    def __init__(self, state, parent, roll, move):
        super().__init__(Node.PLAYER_ONE, state, parent, roll, move)

class AINode(ActionNode):
    def __init__(self, state, parent, roll, move):
        super().__init__(Node.PLAYER_TWO, state, parent, roll, move)

def initial_node(roll, player):
    initial_state = state.initial_board()
    if player is Node.PLAYER_TWO:
        return AINode(initial_state, None, roll, None)
    else:
        return HumanNode(initial_state, None, roll, None)
