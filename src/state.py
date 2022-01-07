def initial_state():
    raise NotImplementedError()

def children(state, roll, token):
    raise NotImplementedError() # return states

def is_terminal(state):
    raise NotImplementedError()