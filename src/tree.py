from argparse import Action
import state
import dice

def player_to_token(player):
    assert(player is not Node.PLAYER_CHANCE)
    return state.Board.TOKEN_ONE if player is Node.PLAYER_ONE else state.Board.TOKEN_TWO

class Node:
    PLAYER_ONE = 0 # maybe introspection is slow?
    PLAYER_TWO = 1
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

    def opponent(self):
        raise NotImplementedError()

class RandomNode(Node):
    def __init__(self, state, parent, move):
        super().__init__(Node.PLAYER_CHANCE, state, parent, move)
    
    def probability(self):
        raise ValueError("Random nodes should never be asked for probability")

    def is_terminal(self):
        return self.state.is_terminal()

    def opponent(self):
        return self.parent.opponent()

    def _generate_children(self):
        opponent = self.opponent()
        rolls = dice.all_rolls()
        self._children = [ActionNode(opponent, self.state, self, roll, self.move) for roll in rolls]
            
class ActionNode(Node):
    def __init__(self, player, state, parent, roll, move):
        self.roll = roll
        super().__init__(player, state, parent, move)
    
    def is_terminal(self):
        return self.state.is_terminal()

    def opponent(self):
        return Node.PLAYER_ONE if self.player is Node.PLAYER_TWO else Node.PLAYER_TWO

    def probability(self):
        return 1.0 / 36 if self.roll[0] == self.roll[1] else 2.0 / 36

    def _generate_children(self):
        self._children = list()
        for (move, child) in state.children(self.state, self.roll, player_to_token(self.player)):
            self._children.append(RandomNode(child, self, move))

def initial_node(roll, player):
    initial_state = state.initial_board()
    return ActionNode(player, initial_state, None, roll, None)
