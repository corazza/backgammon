from hashlib import new
from operator import concat
import IPython
import copy

from result import *

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

    def sanity(dst_point):
        if not 0 <= dst_point < NUM_POINTS:
            return Failure(f'sanity broken: 1 <= destination point={dst_point+1} <= {NUM_POINTS}')
        return Success()

class BoardSource(CheckerSource):
    def __init__(self, point):
        self.point = point
        super().__init__(CheckerSource.CHECKER_SOURCE_KIND_BOARD)

    def get_destination(self, d, token):
        if token == Board.TOKEN_ONE:
            dst_point = self.point - d 
        elif token == Board.TOKEN_TWO:
            dst_point = self.point + d
        return CheckerSource.sanity(dst_point).next(Success(dst_point))

class BarSource(CheckerSource):
    def __init__(self):
        super().__init__(CheckerSource.CHECKER_SOURCE_KIND_BAR)

    def get_destination(self, d, token):
        if token == Board.TOKEN_ONE:
            dst_point = 1 + d
        elif token == Board.TOKEN_TWO:
            dst_point = 24 - d
        return CheckerSource.sanity(dst_point).next(Success(dst_point))

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

    def _home_move_generator_single(self, token):
        offset = 0 if token == Board.TOKEN_ONE else 18
        my_home = self.home_for(token)
        yield from move_generator_single(my_home, lambda i: BoardSource(offset+i))

    def _home_move_generator_double(self, token):
        offset = 0 if token == Board.TOKEN_ONE else 18
        my_home = self.home_for(token)
        yield from move_generator_double(my_home, lambda i: BoardSource(offset+i))

    def board_move_generator(self, token):
        yield from self._general_generator(token, self._board_move_generator)

    def home_move_generator_single(self, token):
        yield from self._general_generator(token, self._home_move_generator_single)

    def home_move_generator_double(self, token):
        yield from self._general_generator(token, self.home_move_generator_double)

    def can_move(self, token, roll):
        for move in self.board_generator(token):
            if execute_move(self, token, move, roll).success():
                return True
        return False

    def bar_empty_for(self, token):
        return self.bar_for(token) == 0

    def can_bear_off(self, token):
        (my_points, _opponent_points) = self.points_for(token)
        my_bar = self.bar_for(token)
        return sum(my_points[6:24]) == 0 and my_bar == 0

    def is_terminal(self):
        return sum(self.points[Board.TOKEN_ONE]) == 0 or sum(self.points[Board.TOKEN_TWO]) == 0

    def token_marking(token):
        return 'A' if token == Board.TOKEN_ONE else 'B'

    def opponent_token(token):
        return (token+1) % 2

def initial_board():
    return Board()

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

    valid_destination = Result.conditional(opponent_points[dst_point] <= 1, f'opponent has more than one checker on destination point {dst_point + 1}')
    my_points[dst_point] += 1

    report_hit = ''
    if opponent_points[dst_point] == 1:
        report_hit = f' (opponent checker on {dst_point + 1} hit)'
        opponent_points[dst_point] = 0
        new_board.add_to_bar_for(Board.opponent_token(token), 1)

    if report:
        report_destination = f'{dst_point + 1}'
        print(f'{report_source} -> {report_destination}{report_hit}')

    return valid_source.next(valid_destination).next(Success(new_board))

def execute_move(board, token, move, roll, report=False):
    (d1, d2) = roll
    (higher, lower) = (max(d1, d2), min(d1, d2))
    if len(move) == 1:
        source = move[0]
        dst_point_result_both = source.get_destination(higher+lower, token)
        dst_point_result_higher = source.get_destination(higher, token)
        dst_point_result_lower = source.get_destination(lower, token)
        both_result = dst_point_result_both.on_content(lambda dst_point: move_one_checker(board, token, source, dst_point, report))
        higher_result = dst_point_result_higher.on_content(lambda dst_point: move_one_checker(board, token, source, dst_point, report))
        lower_result = dst_point_result_lower.on_content(lambda dst_point: move_one_checker(board, token, source, dst_point, report))
        if both_result.success():
            return both_result
        elif higher_result.success():
            return higher_result
        elif lower_result.success():
            return lower_result
        else:
            return both_result.next(higher_result).next(lower_result)
    elif len(move) == 2:
        dst_point_result = move[0].get_destination(d1, token)
        board_new_result = dst_point_result.on_content(lambda dst_point: move_one_checker(board, token, move[0], dst_point, report))
        board_new_dst_point_result = board_new_result.on_content(lambda board_new: move[1].get_destination(d2, token).on_content(lambda dst_point: Success((board_new, dst_point))))
        return board_new_dst_point_result.on_content(lambda p: move_one_checker(p[0], token, move[1], p[1], report))
    else:
        return Failure("move has to be [source] or [source source]")

def bear_off_one_checker(board, token, source):
    point = source.point # assert(isinstance(source, BoardSource))
    new_board = copy.deepcopy(board)
    (my_points, _opponent_points) = new_board.points_for(token)
    valid_source = Result.conditional(my_points[point] > 0, f'can\'t bear off from {point + 1} (no checkers)')
    my_points[point] -= 1
    return valid_source.next(Success(new_board))

def execute_bear_off(board, token, move, roll, report=False):
    if len(move) == 1:
        source = move[0]
        new_board = bear_off_one_checker(board, token, source)
        if new_board.success():
            yield (move, new_board.content)
    elif len(move) == 2:
        first_source = move[0]
        second_source = move[1]
        first_bear_off = bear_off_one_checker(board, token, first_source)
        second_bear_off = first_bear_off.on_content(lambda new_board: bear_off_one_checker(new_board, token, second_source))
        if second_bear_off.success():
            yield (move, second_bear_off.content)

def children_from_bearing_off(board, roll, token):
    boards_to_bear_off = list()
    for move in board.home_move_generator_single(token):
        new_board = execute_move(board, token, move, roll)
        if new_board.success():
            boards_to_bear_off.append(new_board.content)
    boards_to_bear_off.append(Success(board))

    for board in boards_to_bear_off:
        for move in board.home_move_generator_double(token):
            new_board = execute_bear_off(board, token, move, roll)
            if new_board.success():
                yield (move, new_board.content)

def children_from_moving(board, roll, token):
    for move in board.board_move_generator.token():
        new_board = execute_move(board, token, move, roll)
        if new_board.success():
            yield (move, new_board.content)

def children(board, roll, token):
    yield from children_from_moving(board, roll, token)
    if board.can_bear_off(token):
        yield from children_from_bearing_off(board, roll, token)

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
