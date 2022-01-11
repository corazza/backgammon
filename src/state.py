import copy

NUM_POINTS = 24
NUM_CHECKERS = 15

class CheckerSource:
    """A checker can come from the board or the bar"""
    CHECKER_SOURCE_KIND_BOARD = 0
    CHECKER_SOURCE_KIND_BAR = 1
    def __init__(self, kind):
        self.kind = kind

    def get_destination(self, d, token):
        raise NotImplementedError()

class BoardSource(CheckerSource):
    def __init__(self, point):
        self.point = point
        super().__init__(CheckerSource.CHECKER_SOURCE_KIND_BOARD)
    
    def get_destination(self, d, token):
        if token == Board.TOKEN_ONE:
            destination = self.point - d 
        elif token == Board.TOKEN_TWO:
            destination = self.point + d
        assert(0 <= destination <= 23)
        return destination

class BarSource(CheckerSource):
    def __init__(self):
        super().__init__(CheckerSource.CHECKER_SOURCE_KIND_BAR)

    def get_destination(self, d, token):
        if token == Board.TOKEN_ONE:
            destination = 1 + d
        elif token == Board.TOKEN_TWO:
            destination = 24 - d
        assert(0 <= destination <= 23)
        return destination

class Board:
    TOKEN_ONE = 0
    TOKEN_TWO = 1
    def __init__(self):
        self.points = ([0] * NUM_POINTS, [0] * NUM_POINTS)
        self.points[Board.TOKEN_ONE][23] = 2
        self.points[Board.TOKEN_ONE][7] = 3
        self.points[Board.TOKEN_ONE][12] = 5
        self.points[Board.TOKEN_ONE][5] = 5
        self.points[Board.TOKEN_TWO][0] = 2
        self.points[Board.TOKEN_TWO][16] = 3
        self.points[Board.TOKEN_TWO][11] = 5
        self.points[Board.TOKEN_TWO][18] = 5
        self.bars = (0, 0)

    def points_for(self, token):
        if token == Board.TOKEN_ONE:
            return (self.points[Board.TOKEN_ONE], self.points[Board.TOKEN_TWO])
        elif token == Board.TOKEN_TWO:
            return (self.points[Board.TOKEN_TWO], self.points[Board.TOKEN_ONE])

    def home_for(self, token):
        (my_points, _opponent_points) = self.points_for(token)
        return my_points[0:6]

    def bar_for(self, token):
        return self.bars[token]

    def add_to_bar_for(self, token, x):
        self.bars[token] += x

    # check single roll validity
    def can_move_to(self, token, source, dst_point):
        if dst_point > 23:
            return False
        if source.kind == CheckerSource.CHECKER_SOURCE_KIND_BOARD:
            src_point = source.point
            (my_points, opponent_points) = self.points_for(token)
            assert(my_points[src_point] > 0) # at least one checker is on the point to be moved
        elif source.kind == CheckerSource.CHECKER_SOURCE_KIND_BAR:
            my_bar = self.bar_for(token)
            assert(my_bar > 0)
        if opponent_points[dst_point] > 1:
            return False
        elif opponent_points[dst_point] == 1: # hit
            return True
        elif opponent_points[dst_point] == 0: # free
            return True

    def can_bear_off(self, token):
        (my_points, _opponent_points) = self.points_for(token)
        my_bar = self.bar_for(token)
        return sum(my_points[6:24]) == 0 and my_bar == 0

    def can_bear_off_from(self, token, roll):
        (my_points, _opponent_points) = self.points_for(token)
        return self.can_bear_off(token) and my_points[roll-1] > 0

    def is_terminal(self):
        return sum(self.points[Board.TOKEN_ONE]) == 0 or sum(self.points[Board.TOKEN_TWO]) == 0

    def token_marking(token):
        return 'A' if token == Board.TOKEN_ONE else 'B'

    def print(self, token):
        opponent_token = Board.opponent_token(token)
        my_marking = Board.token_marking(token)
        opponent_marking = Board.token_marking(opponent_token)
        points = self.points_for(token)
        points_to_print = ['---']*NUM_POINTS
        for i in range(0, NUM_POINTS):
            if points[token][i] > 0:
                points_to_print[i] = f'{points[token][i]}:{my_marking}'
            if points[opponent_token][i] > 0:
                points_to_print[i] = f'{points[opponent_token][i]}:{opponent_marking}'
        markings_upper = [0] * int(NUM_POINTS/2)
        markings_lower = [0] * int(NUM_POINTS/2)
        for i in range(int(NUM_POINTS/2)):
            markings_upper[i] = f'{i + 12 + 1} '
            markings_lower[i] = f'{12 - i } ' if 12-i >= 9 else f' {12 - i } '

        if token == Board.TOKEN_TWO:
            (markings_upper, markings_lower) = (markings_lower, markings_upper)

        markings_upper = ' '.join(markings_upper)
        markings_lower = ' '.join(markings_lower)
        upper = ' '.join(points_to_print[int(NUM_POINTS/2) : NUM_POINTS])
        lower = ' '.join(reversed(points_to_print[0 : int(NUM_POINTS/2)]))

        print_order = [markings_upper, upper, '|', lower, markings_lower]
        print('\n'.join(print_order))

        bar = f'{self.bars[Board.TOKEN_ONE]}:A {self.bars[Board.TOKEN_TWO]}:B'
        print(bar)

    def opponent_token(token):
        return (token+1) % 2

def initial_board():
    return Board()

def execute_move(board, token, source, dst_point):
    new_board = copy.deepcopy(board)
    (my_points, opponent_points) = new_board.points_for(token)
    if source.kind == CheckerSource.CHECKER_SOURCE_KIND_BOARD:
        src_point = source.point
        assert(my_points[src_point] > 0) # at least one checker is on the point to be moved
        my_points[src_point] -= 1
    elif source.kind == CheckerSource.CHECKER_SOURCE_KIND_BAR:
        my_bar = new_board.my_bar(token)
        assert(my_bar > 0)
        new_board.add_to_bar_for(token, -1)
    my_points[dst_point] += 1
    if opponent_points[dst_point] == 1:
        opponent_points[dst_point] = 0
        new_board.add_to_bar_for(Board.opponent_token(token), 1)
    return new_board

def bear_off(board, token, source):
    point = source.point # assert(isinstance(source, BoardSource))
    new_board = copy.deepcopy(board)
    (my_points, _opponent_points) = new_board.points_for(token)
    assert(my_points[point - 1] > 0)
    my_points[point - 1] -= 1
    return new_board

def attempt_moves_from(points, first_generator, second_generator):
    for i in first_generator(): # lower chosen point
        if points[i] == 0:
            continue
        yield [BoardSource(i)]
        for j in second_generator(i): # higher chosen point
            if points[j] == 0:
                continue
            yield [BoardSource(i), BoardSource(j)]

def children_from_bearing_off(board, roll, token):
    board = copy.deepcopy(board)
    (d1, d2) = roll
    my_home = board.home_for(token)
    first_generator = lambda: range(0, len(my_home))
    second_generator = lambda i: () # moving two checkers happens in children_from_moving
    move_list = list(attempt_moves_from(my_home, first_generator, second_generator))
    boards_to_bear_off = list()
    for move_from in move_list:
        source = move_from[0]
        first_dst_point = source.get_destination(d1, token)
        second_dst_point = source.get_destination(d2, token)
        if board.can_move_to(token, source, first_dst_point):
            new_board = execute_move(board, token, source, first_dst_point)
            boards_to_bear_off.append(new_board)
        if board.can_move_to(token, source, second_dst_point):
            new_board = execute_move(board, token, source, second_dst_point)
            boards_to_bear_off.append(new_board)

    boards_to_bear_off.append(board)
    for board in boards_to_bear_off:
        first_generator = lambda: range(0, len(my_home))
        second_generator = lambda i: range(i, len(my_home))
        for move in attempt_moves_from(my_home, first_generator, second_generator):
            if len(move) == 1:
                source = move[0]
                if board.can_bear_off(token, source):
                    yield bear_off(board, token, source)
            elif len(move) == 2:
                first_source = move[0]
                second_source = move[1]
                if board.can_bear_off(token, first_source) and board.can_bear_off(token, second_source):
                    yield bear_off(board, token, source)

def children_from_moving(board, roll, token):
    (d1, d2) = roll
    my_bar = board.my_bar(token)
    attempt_moves_from = list()
    # choose two points (possibly the same one) from which to attempt a move
    if my_bar == 0:
        first_generator = lambda: range(0, NUM_POINTS)
        second_generator = lambda i: range(i, NUM_POINTS)
        move_list = list(attempt_moves_from(board[token], first_generator, second_generator))
    elif my_bar > 0:
        move_list = list()
        move_list.append([BarSource()])
        move_list.append([BarSource(), BarSource()])

    for move in move_list:
        if len(move) == 1:
            source = move[0]
            dst_point = source.get_destination(d1+d2, token)
            if board.can_move_to(token, source, dst_point):
                yield execute_move(board, token, source, dst_point)
        elif len(move) == 2:
            first_source = move[0]
            second_source = move[1]
            if board.can_move_to(token, first_source, first_source.get_destination(d1, token)):
                board_new = execute_move(board, token, first_source, first_source.get_destination(d1, token))
                if board_new.can_move_to(token, second_source, second_source.get_destination(d2, token)):
                    yield execute_move(board_new, token, second_source, second_source.get_destination(d2, token))
            if board.can_move_to(token, second_source, second_source.get_destination(d1, token)):
                board_new = execute_move(board, token, second_source, second_source.get_destination(d1, token))
                if board_new.can_move_to(token, first_source, first_source.get_destination(d2, token)):
                    yield execute_move(board_new, token, first_source, first_source.get_destination(d2, token))

def children(board, roll, token):
    yield from children_from_moving(board, roll, token)
    if board.can_bear_off(token):
        yield from children_from_bearing_off(board, roll, token)
