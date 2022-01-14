from hashlib import new
from operator import concat
import IPython
import copy
import itertools

from result import *

NUM_POINTS = 24
NUM_CHECKERS = 15

class CheckerSource:
    """A checker can come from the board or the bar"""
    CHECKER_SOURCE_KIND_BOARD = 0
    CHECKER_SOURCE_KIND_BAR = 1
    def __init__(self, kind):
        self.kind = kind

    def get_board_destination(self, d, token):
        raise NotImplementedError()

    def sanity(dst_point):
        if not 0 <= dst_point < NUM_POINTS:
            return Failure(f'sanity broken: 1 <= destination point={dst_point+1} <= {NUM_POINTS}')
        return Success()

class BoardSource(CheckerSource):
    def __init__(self, point):
        self.point = point
        super().__init__(CheckerSource.CHECKER_SOURCE_KIND_BOARD)

    def get_board_destination(self, d, token):
        if token == Board.TOKEN_ONE:
            dst_point = self.point - d 
        elif token == Board.TOKEN_TWO:
            dst_point = self.point + d
        return CheckerSource.sanity(dst_point).next(Success(dst_point))

class BarSource(CheckerSource):
    def __init__(self):
        super().__init__(CheckerSource.CHECKER_SOURCE_KIND_BAR)

    def get_board_destination(self, d, token):
        if token == Board.TOKEN_ONE:
            dst_point = d - 1
        elif token == Board.TOKEN_TWO:
            dst_point = 24 - d
        return CheckerSource.sanity(dst_point).next(Success(dst_point))

class CheckerDestination:
    KIND_BOARD = 0
    KIND_BEAR_OFF = 1
    def __init__(self, kind):
        self.kind = kind
    
class BoardDestination(CheckerDestination):
    def __init__(self, dst_point):
        self.dst_point = dst_point
        super().__init__(CheckerDestination.KIND_BOARD)

class BearOffDestination(CheckerDestination):
    def __init__(self):
        super().__init__(CheckerDestination.KIND_BEAR_OFF)

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
        self.bars = [0, 0]

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

    def _general_generator(self, token, generator):
        if not self.bar_empty_for(token):
            yield [BarSource()]
            yield [BarSource(), BarSource()]
        else:
            yield from generator(token)

    def _board_move_generator(self, token):
        (my_points, _opponent_points) = self.points_for(token)
        yield from move_generator_double(my_points, lambda i: BoardSource(i))

    def _home_move_generator(self, token):
        offset = 0 if token == Board.TOKEN_ONE else 18
        my_home = self.home_for(token)
        yield from move_generator_single(my_home, lambda i: BoardSource(offset+i))

    def board_move_generator(self, token):
        yield from self._general_generator(token, self._board_move_generator)

    def home_move_generator(self, token):
        yield from self._general_generator(token, self._home_move_generator)

    def get_destination(self, token, source, d):
        (my_points, _opponent_points) = self.points_for(token)
        bearing_off_from = d - 1 if token == Board.TOKEN_ONE else 24 - d
        if self.can_bear_off(token) and bearing_off_from == source.point and my_points[source.point] > 0:
            return Success(BearOffDestination())
        else:
            return source.get_board_destination(d, token).on_content(lambda point: Success(BoardDestination(point)))

    def can_move(self, token, roll):
        # for move in self.board_move_generator(token):
        #     if execute_move(self, token, move, roll).success():
        #         return True
        # return False
        return peek(children(self, roll, token)) is not None

    def bar_empty_for(self, token):
        return self.bar_for(token) == 0

    def can_bear_off(self, token):
        (my_points, _opponent_points) = self.points_for(token)
        my_bar = self.bar_for(token)
        if token == Board.TOKEN_ONE:
            checker_sum = sum(my_points[6:24])
        elif token == Board.TOKEN_TWO:
            checker_sum = sum(my_points[0:18])
        return checker_sum == 0 and my_bar == 0

    def is_terminal(self):
        first_bar_empty = self.bar_empty_for(Board.TOKEN_ONE) 
        second_bar_empty = self.bar_empty_for(Board.TOKEN_TWO)
        first_board_empty = sum(self.points[Board.TOKEN_ONE]) == 0
        second_board_empty = sum(self.points[Board.TOKEN_TWO]) == 0
        return (first_bar_empty and first_board_empty) or (second_bar_empty and second_board_empty)

    def token_marking(token):
        return 'A' if token == Board.TOKEN_ONE else 'B'

    def opponent_token(token):
        return (token+1) % 2

def initial_board():
    return Board()

def move_generator_double(points, make_source):
    num_points = len(points)
    for i in range(0, num_points): # lower chosen point
        if points[i] == 0:
            continue
        yield [make_source(i)]
        for j in range(i, num_points): # higher chosen point
            if points[j] == 0:
                continue
            yield [make_source(i), make_source(j)]
            if i is not j:
                yield [make_source(j), make_source(i)]

def move_generator_single(points, make_source):
    num_points = len(points)
    for i in range(0, num_points): # lower chosen point
        if points[i] == 0:
            continue
        yield [make_source(i)]

def move_one_checker(board, token, source, destination, report=False):
    report_source = None
    new_board = copy.deepcopy(board)
    (my_points, opponent_points) = new_board.points_for(token)
    if source.kind == CheckerSource.CHECKER_SOURCE_KIND_BOARD:
        src_point = source.point
        report_source = f'{src_point + 1}'
        valid_source = Result.conditional(my_points[src_point] > 0, f'no checkers on source point {src_point + 1}')
        valid_source = valid_source.next(Result.conditional(new_board.bar_empty_for(token), f'bar not empty'))
        my_points[src_point] -= 1
    elif source.kind == CheckerSource.CHECKER_SOURCE_KIND_BAR:
        report_source = f'bar'
        valid_source = Result.conditional(not board.bar_empty_for(token), f'no checkers on bar')
        new_board.add_to_bar_for(token, -1)

    report_hit = ''
    report_destination = None
    if destination.kind == CheckerDestination.KIND_BOARD:
        dst_point = destination.dst_point
        valid_destination = Result.conditional(opponent_points[dst_point] <= 1, f'opponent has more than one checker on destination point {dst_point + 1}')
        my_points[dst_point] += 1
        if opponent_points[dst_point] == 1:
            report_hit = f' (opponent checker on {dst_point + 1} hit)'
            opponent_points[dst_point] = 0
            new_board.add_to_bar_for(Board.opponent_token(token), 1)
        report_destination = f'{dst_point + 1}'
    elif destination.kind == CheckerDestination.KIND_BEAR_OFF:
        valid_destination = Result.conditional(board.can_bear_off(token), f'can\'t bear off')
        report_destination = 'bear off'

    if report:
        success = '(unsuccessful move) ' if not valid_source.next(valid_destination).success() else ''
        print(f'{success}{report_source} -> {report_destination}{report_hit}')

    return valid_source.next(valid_destination).next(Success(new_board))

def execute_move(board, token, move, roll, report=False):
    (d1, d2) = roll
    (higher, lower) = (max(d1, d2), min(d1, d2))
    my_bar = board.bar_for(token)
    if len(move) == 1:
        source = move[0]
        assert(source.kind == CheckerSource.CHECKER_SOURCE_KIND_BAR or my_bar == 0)
        dst_point_result_both = board.get_destination(token, source, higher+lower)
        dst_point_result_higher = board.get_destination(token, source, higher)
        dst_point_result_lower = board.get_destination(token, source, lower)
        both_result = dst_point_result_both.on_content(lambda destination: move_one_checker(board, token, source, destination, report=False))
        higher_result = dst_point_result_higher.on_content(lambda destination: move_one_checker(board, token, source, destination, report=False))
        lower_result = dst_point_result_lower.on_content(lambda destination: move_one_checker(board, token, source, destination, report=False))
        if both_result.success():
            dst_point_result_both.on_content(lambda destination: move_one_checker(board, token, source, destination, report))
            return both_result
        elif higher_result.success():
            dst_point_result_higher.on_content(lambda destination: move_one_checker(board, token, source, destination, report))
            return higher_result
        elif lower_result.success():
            dst_point_result_lower.on_content(lambda destination: move_one_checker(board, token, source, destination, report))
            return lower_result
        else:
            return both_result.next(higher_result).next(lower_result)
    elif len(move) == 2:
        dst_point_result = board.get_destination(token, move[0], d1)
        board_new_result = dst_point_result.on_content(lambda destination: move_one_checker(board, token, move[0], destination, report))
        board_new_dst_point_result = board_new_result.on_content(lambda board_new: board.get_destination(token, move[1], d2).on_content(lambda destination: Success((board_new, destination))))
        if board_new_dst_point_result.success():
            new_bar = board_new_dst_point_result.content[0].bar_for(token)
            assert(move[1].kind == CheckerSource.CHECKER_SOURCE_KIND_BAR or new_bar == 0)
        return board_new_dst_point_result.on_content(lambda p: move_one_checker(p[0], token, move[1], p[1], report))
    else:
        return Failure("move has to be [source] or [source source]")

def children(board, roll, token):
    for move in board.board_move_generator(token):
        new_board = execute_move(board, token, move, roll)
        if new_board.success():
            yield (move, new_board.content)

def print_board(board, token):
    opponent_token = Board.opponent_token(token)
    my_marking = Board.token_marking(token)
    opponent_marking = Board.token_marking(opponent_token)
    points = board.points
    upper_direction_marking = '←'
    lower_direction_marking = '→'
    if token == Board.TOKEN_TWO:
        (lower_direction_marking, upper_direction_marking) = (upper_direction_marking, lower_direction_marking)
    points_to_print_upper = [f' {upper_direction_marking} ']*int(NUM_POINTS/2)
    points_to_print_lower = [f' {lower_direction_marking} ']*int(NUM_POINTS/2)
    points_to_print = concat(points_to_print_lower, points_to_print_upper)
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
    bar = f'Bar: {board.bars[Board.TOKEN_ONE]}:A {board.bars[Board.TOKEN_TWO]}:B'

    print(bar)
    print(markings_upper)
    print(upper)
    if token == Board.TOKEN_ONE:
        print('↓')
    elif token == Board.TOKEN_TWO:
        print('↑')
    print(lower)
    print(markings_lower)

def peek(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return first, itertools.chain([first], iterable)
