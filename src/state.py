import copy
import IPython

NUM_POINTS = 24

class CheckerSource:
    """A checker can come from the board or the bar"""
    CHECKER_SOURCE_KIND_BOARD = 0
    CHECKER_SOURCE_KIND_BAR = 1
    def __init__(self, kind):
        self.kind = kind

    def get_destination(self, d, token):
        raise NotImplementedError()

    def sanity():
        raise NotImplementedError()

class BoardSource(CheckerSource):
    def __init__(self, point):
        self.point = point
        super().__init__(CheckerSource.CHECKER_SOURCE_KIND_BOARD)

    def sanity(self, print_reason=False):
        return source_sanity(self.point, print_reason)

    def _compute_dst_point(self, d, token):
        if token == Board.TOKEN_ONE:
            return self.point - d 
        elif token == Board.TOKEN_TWO:
            return self.point + d

    def get_destination(self, d, token):
        dst_point = self._compute_dst_point(d, token)
        assert(destination_sanity(dst_point))
        return dst_point

    def destination_sanity(self, d, token, print_reason):
        dst_point = self._compute_dst_point(d, token)
        return destination_sanity(dst_point, print_reason)

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
        return my_points[0:6] if token == Board.TOKEN_ONE else my_points[18:24]

    def bar_for(self, token):
        return self.bars[token]

    def add_to_bar_for(self, token, x):
        self.bars[token] += x

    def board_move_generator(self, token):
        (my_points, _opponent_points) = self.points_for(token)
        yield from move_generator_double(my_points, lambda i: BoardSource(i))

    def home_move_generator_single(self, token):
        offset = 0 if token == Board.TOKEN_ONE else 18
        my_home = self.home_for(token)
        yield from move_generator_single(my_home, lambda i: BoardSource(offset+i))

    def home_move_generator_double(self, token):
        offset = 0 if token == Board.TOKEN_ONE else 18
        my_home = self.home_for(token)
        yield from move_generator_double(my_home, lambda i: BoardSource(offset+i))

    def can_move(self, token, roll):
        for move in self.board_generator(token):
            if self.can_execute_move(token, move, roll):
                return True
        return False

    def can_execute_move(self, token, move, roll):
        (d1, d2) = roll
        if len(move) == 1:
            source = move[0]
            destination = source.get_destination(d1+d2, token)
            return self.can_move_to(token, source, destination)
        elif len(move) == 2:
            first_source = move[0]
            second_source = move[1]
            if self.can_move_to(token, first_source, first_source.get_destination(d1)):
                board_new = move_one_checker(self, token, first_source, first_source.get_destination(d1))
                return board_new.can_move_to(token, second_source, second_source.get_destination(d2))
        else:
            raise ValueError()

    def _valid_source(self, token, source, print_reason=False):
        (my_points, opponent_points) = self.points_for(token)
        if source.kind == CheckerSource.CHECKER_SOURCE_KIND_BOARD:
            src_point = source.point
            if my_points[src_point] == 0:
                if print_reason:
                    print(f'no checkers on source point {src_point + 1}')
                return False
        elif source.kind == CheckerSource.CHECKER_SOURCE_KIND_BAR:
            my_bar = self.bar_for(token)
            if my_bar == 0:
                if print_reason:
                    print('no checkers on the bar')
                return False
        return True
    
    def _valid_destination(self, token, dst_point, print_reason=False):
        (_my_points, opponent_points) = self.points_for(token)
        if opponent_points[dst_point] > 1:
            if print_reason:
                print(f'opponent has more than one checker on destination point {dst_point + 1}')
            return False
        elif opponent_points[dst_point] == 1: # hit
            return True
        elif opponent_points[dst_point] == 0: # free
            return True

    def valid(self, token, source, dst_point, print_reason=False):
        assert(sanity(source, dst_point, print_reason))
        valid_source = self._valid_source(token, source, print_reason)
        valid_destination = self._valid_destination(token, dst_point, print_reason)
        return valid_source and valid_destination

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

    def opponent_token(token):
        return (token+1) % 2

def initial_board():
    return Board()

def source_sanity(src_point, print_reason=False):
    if not 0 <= src_point < NUM_POINTS:
        if print_reason:
            print(f'sanity broken: 0 <= source point={src_point} < {NUM_POINTS}')
        return False
    return True

def destination_sanity(dst_point, print_reason=False):
    if not 0 <= dst_point < NUM_POINTS:
        if print_reason:
            print(f'sanity broken: 0 <= destination point={dst_point} < {NUM_POINTS}')
        return False
    return True

def sanity(source, dst_point, print_reason=False):
    sane_destination = destination_sanity(dst_point, print_reason)
    sane_source = source.sanity()
    return sane_destination and sane_source

def print_board(board, token):
    opponent_token = Board.opponent_token(token)
    my_marking = Board.token_marking(token)
    opponent_marking = Board.token_marking(opponent_token)
    points = board.points
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

    markings_upper = ' '.join(markings_upper)
    markings_lower = ' '.join(markings_lower)
    upper = ' '.join(points_to_print[int(NUM_POINTS/2) : NUM_POINTS])
    lower = ' '.join(reversed(points_to_print[0 : int(NUM_POINTS/2)]))

    print_order = [markings_upper, upper, '|', lower, markings_lower]
    print('\n'.join(print_order))

    bar = f'{board.bars[Board.TOKEN_ONE]}:A {board.bars[Board.TOKEN_TWO]}:B'
    print(bar)


def move_generator_double(points, offset, make_source):
    num_points = len(points)
    for i in range(0, num_points): # lower chosen point
        if points[i] == 0:
            continue
        yield [make_source(i)]
        for j in range(i, num_points): # higher chosen point
            if points[j] == 0:
                continue
            yield [make_source(i), make_source(j)]
            yield [make_source(j), make_source(i)]

def move_generator_single(points, make_source):
    num_points = len(points)
    for i in range(0, num_points): # lower chosen point
        if points[i] == 0:
            continue
        yield [make_source(i)]

def move_one_checker(board, token, source, dst_point, report=False):
    report_source = None
    report_destination = None
    report_hit = ''
    new_board = copy.deepcopy(board)
    (my_points, opponent_points) = new_board.points_for(token)
    if source.kind == CheckerSource.CHECKER_SOURCE_KIND_BOARD:
        src_point = source.point
        assert(my_points[src_point] > 0) # at least one checker is on the point to be moved
        my_points[src_point] -= 1
        report_source = f'{src_point + 1}'
    elif source.kind == CheckerSource.CHECKER_SOURCE_KIND_BAR:
        my_bar = new_board.my_bar(token)
        assert(my_bar > 0)
        new_board.add_to_bar_for(token, -1)
        report_source = f'bar'
    my_points[dst_point] += 1
    report_destination = f'{dst_point + 1}'
    if opponent_points[dst_point] == 1:
        opponent_points[dst_point] = 0
        new_board.add_to_bar_for(Board.opponent_token(token), 1)
        report_hit = f' (opponent checker on {dst_point + 1} hit)'
    if report:
        print(f'{report_source} -> {report_destination}{report_hit}')
    return new_board

def bear_off(board, token, source):
    point = source.point # assert(isinstance(source, BoardSource))
    new_board = copy.deepcopy(board)
    (my_points, _opponent_points) = new_board.points_for(token)
    assert(my_points[point - 1] > 0)
    my_points[point - 1] -= 1
    return new_board

def children_from_bearing_off(board, roll, token):
    board = copy.deepcopy(board)
    (d1, d2) = roll
    my_home = board.home_for(token)
    boards_to_bear_off = list()
    for move_from in board.home_move_generator_double(token):
        source = move_from[0]
        first_dst_point = source.get_destination(d1, token)
        second_dst_point = source.get_destination(d2, token)
        if board.can_move_to(token, source, first_dst_point):
            new_board = move_one_checker(board, token, source, first_dst_point)
            boards_to_bear_off.append(new_board)
        if board.can_move_to(token, source, second_dst_point):
            new_board = move_one_checker(board, token, source, second_dst_point)
            boards_to_bear_off.append(new_board)

    boards_to_bear_off.append(board)
    for board in boards_to_bear_off:
        for move in board.home_move_generator_double(token):
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
    # choose two points (possibly the same one) from which to attempt a move
    if my_bar == 0:
        move_list = list(board.board_move_generator(token))
    elif my_bar > 0:
        move_list = list()
        move_list.append([BarSource()])
        move_list.append([BarSource(), BarSource()])
 
    for move in move_list:
        if len(move) == 1:
            source = move[0]
            dst_point = source.get_destination(d1+d2, token)
            if board.can_move_to(token, source, dst_point):
                yield move_one_checker(board, token, source, dst_point)
        elif len(move) == 2:
            first_source = move[0]
            second_source = move[1]
            if board.can_move_to(token, first_source, first_source.get_destination(d1, token)):
                board_new = move_one_checker(board, token, first_source, first_source.get_destination(d1, token))
                if board_new.can_move_to(token, second_source, second_source.get_destination(d2, token)):
                    yield move_one_checker(board_new, token, second_source, second_source.get_destination(d2, token))

def children(board, roll, token):
    yield from children_from_moving(board, roll, token)
    if board.can_bear_off(token):
        yield from children_from_bearing_off(board, roll, token)
