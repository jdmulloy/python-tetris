#!/usr/bin/python

import curses
import time
import random


class Board(object):
    def __init__(self, stdscr):
        self.stdscr = stdscr

        curses.curs_set(0)
        curses.init_pair(curses.COLOR_WHITE, curses.COLOR_BLACK,
                         curses.COLOR_WHITE)
        curses.init_pair(curses.COLOR_CYAN, curses.COLOR_BLACK,
                         curses.COLOR_CYAN)
        curses.init_pair(curses.COLOR_BLUE, curses.COLOR_BLACK,
                         curses.COLOR_BLUE)
        curses.init_pair(curses.COLOR_YELLOW, curses.COLOR_BLACK,
                         curses.COLOR_YELLOW)
        curses.init_pair(curses.COLOR_GREEN, curses.COLOR_BLACK,
                         curses.COLOR_GREEN)
        curses.init_pair(curses.COLOR_MAGENTA, curses.COLOR_BLACK,
                         curses.COLOR_MAGENTA)
        curses.init_pair(curses.COLOR_RED, curses.COLOR_BLACK,
                         curses.COLOR_RED)
        b_y = 1
        b_x = 1
        self.height = 20
        self.width = 10
        self.y_limit = self.height - 1
        self.x_limit = self.width - 1
        self.speed = 1
        self.delay = 1

        self.state = []
        self.total_rows_cleared = 0
        self.score = 0
        self.next_piece = self.get_random_piece()

        for row in range(self.height):
            self.state.append([curses.COLOR_BLACK] * self.width)

        self.board = curses.newwin(self.height, self.width * 2, b_y, b_x)

        self.stdscr.addstr(b_y-1, b_x-1, "                      ",
                           curses.color_pair(curses.COLOR_WHITE))
        for i in range(1, self.height + 1):
            self.stdscr.addstr(i, 0, " ",
                               curses.color_pair(curses.COLOR_WHITE))
            self.stdscr.addstr(i, (self.width * 2) + 1, " ",
                               curses.color_pair(curses.COLOR_WHITE))
        self.stdscr.addstr(self.height + 1, 0, "                      ",
                           curses.color_pair(curses.COLOR_WHITE))
        self.stdscr.refresh()

        self.info_win = curses.newwin(3, 30, 0, self.width*2 + 5)
        self.info_win.addstr(0, 0, "SCORE: ")
        self.info_win.addstr(1, 0, "SPEED: " + str(self.speed).rjust(7))
        self.info_win.addstr(2, 0,
                             " ROWS: " + str(self.total_rows_cleared).rjust(7))
        self.increase_score(0)

        self.preview = curses.newwin(3, 8, 4, self.width*2 + 5)
        self.preview.addstr(0, 1, "NEXT:")
        self.preview.refresh()

    def increase_total_rows_cleared(self):
        self.total_rows_cleared += 1
        # Increase speed by 1 for every divisor number of rows cleared
        self.speed = 1 + self.total_rows_cleared/10
        self.delay = 1.0/self.speed
        self.info_win.addstr(1, 7, str(self.speed).rjust(7))
        self.info_win.addstr(2, 7, str(self.total_rows_cleared).rjust(7))
        self.info_win.refresh()

    def increase_score(self, new_points):
        self.score += new_points
        self.info_win.addstr(0, 7, str(self.score).rjust(7))
        self.info_win.refresh()

    def clear_blocks(self, cords):
        for cord in cords:
            row = cord[0]
            col = cord[1]
            self.state[row][col] = curses.COLOR_BLACK
        self.draw_board()

    def update_blocks(self, color, new_cords, old_cords=[]):
        for cord in set(new_cords) - set(old_cords):
            row = cord[0]
            col = cord[1]
            if self.state[row][col] != curses.COLOR_BLACK:
                return False
        self.clear_blocks(old_cords)
        for cord in new_cords:
            row = cord[0]
            col = cord[1]
            self.state[row][col] = color
        self.draw_board()
        return True

    def draw_preview(self):
        for row in range(1, 3):
            self.preview.insstr(row, 0, "        ",
                                curses.color_pair(curses.COLOR_BLACK))
        for cord in self.next_piece.get_preview_cords():
            y = 2 + cord[0]
            x = 2 + cord[1] * 2
            color = curses.color_pair(self.next_piece.color)
            self.preview.insstr(y, x, "  ", color)
        self.preview.refresh()

    def draw_board(self):
        for row in range(self.height):
            for col in range(self.width):
                pass
                self.board.insstr(row, col * 2, "  ",
                                  curses.color_pair(self.state[row][col]))
        self.board.refresh()

    def clear_full_rows(self):
        rows_cleared = 0
        for row in range(self.height):
            if curses.COLOR_BLACK not in self.state[row]:
                self.increase_total_rows_cleared()
                rows_cleared += 1
                self.state[row] = [curses.COLOR_WHITE] * self.width
        self.draw_board()
        time.sleep(0.1)
        self.increase_score(1000 * rows_cleared * rows_cleared * self.speed)
        for row in range(self.height):
            if curses.COLOR_BLACK not in self.state[row]:
                del self.state[row]
                self.state.insert(0, [curses.COLOR_BLACK] * self.width)
        self.draw_board()

    def get_random_piece(self):
        r = random.randint(0, 6)
        if r == 0:
            return Piece_T(self)
        elif r == 1:
            return Piece_I(self)
        elif r == 2:
            return Piece_S(self)
        elif r == 3:
            return Piece_Z(self)
        elif r == 4:
            return Piece_O(self)
        elif r == 5:
            return Piece_L(self)
        elif r == 6:
            return Piece_J(self)

    def get_piece(self):
        piece = self.next_piece
        self.next_piece = self.get_random_piece()
        self.draw_preview()
        return piece

    def main(self):
        p = self.get_piece()

        p.draw()

        curses.halfdelay(1)

        t1 = time.time()

        while True:
            c = self.stdscr.getch()
            t2 = time.time()
            if t2 - t1 > self.delay:
                t1 = t2
                if not p.move_down():
                    self.clear_full_rows()
                    p = self.get_piece()
                    if not p.draw():
                        break
            elif c == 456:
                if not p.move_down():
                    self.clear_full_rows()
                    p = self.get_piece()
                    if not p.draw():
                        break
            if c == ord('q'):
                break
            if c == 450:
                p.rotate()
            if c == 452:
                p.move_left()
            if c == 454:
                p.move_right()
            if c == ord(' '):
                while p.move_down():
                    pass
                self.clear_full_rows()
                p = self.get_piece()
                if not p.draw():
                    break

        self.stdscr.addstr(2, 6, "GAME OVER!")
        self.stdscr.addstr(4, 3, "Press Q to QUIT")
        c = self.stdscr.getch()
        while c != ord('q') and c != ord('Q'):
            c = self.stdscr.getch()


class Piece(object):
    def __init__(self, board):
        self.board = board
        self.x = 5
        self.y = 1
        self.orientation = 0

    def get_cords(self):
        return [(self.y + y, self.x + x) for (y, x)
                in self.layouts[self.orientation]]

    def get_new_cords(self, y_delta, x_delta, orientation):
        return [(self.y + y + y_delta, self.x + x + x_delta) for (y, x)
                in self.layouts[orientation]]

    def get_preview_cords(self):
        return self.layouts[0]

    def bounds_valid(self, y_delta, x_delta, orientation):
        for cord in self.get_new_cords(y_delta, x_delta, orientation):
            row = cord[0]
            col = cord[1]
            # (( is the only way to silence pep8 :(
            # https://github.com/PyCQA/pycodestyle/issues/126
            if ((row < 0 or row > self.board.y_limit or
                 col < 0 or col > self.board.x_limit)):
                return False
        return True

    def draw(self, old_cords=[]):
        return self.board.update_blocks(self.color, self.get_cords(),
                                        old_cords)

    def rotate(self):
        old_cords = self.get_cords()
        new_orientation = (self.orientation + 1) % len(self.layouts)
        if self.bounds_valid(0, 0, new_orientation):
            self.orientation = new_orientation
            if self.draw(old_cords):
                return True
            else:
                self.orientation = (self.orientation - 1) % len(self.layouts)
        return False

    def move(self, y_delta, x_delta):
        old_cords = self.get_cords()
        if self.bounds_valid(y_delta, x_delta, self.orientation):
            self.y += y_delta
            self.x += x_delta
            if self.draw(old_cords):
                return True
            else:
                self.y -= y_delta
                self.x -= x_delta
        return False

    def move_left(self):
        return self.move(0, -1)

    def move_right(self):
        return self.move(0, 1)

    def move_down(self):
        return self.move(1, 0)


class Piece_T(Piece):
    def __init__(self, board):
        super(Piece_T, self).__init__(board)
        self.layouts = [
            [(-1, 0), (0, -1), (0, 0), (0, 1)],
            [(-1, 0),  (0, 0), (0, 1), (1, 0)],
            [(0, -1),  (0, 0), (0, 1), (1, 0)],
            [(-1, 0), (0, -1), (0, 0), (1, 0)],
        ]
        self.color = curses.COLOR_MAGENTA


class Piece_I(Piece):
    def __init__(self, board):
        super(Piece_I, self).__init__(board)
        self.layouts = [
            [(0, -1), (0, 0), (0, 1), (0, 2)],
            [(-1, 0), (0, 0), (1, 0), (2, 0)],
        ]
        self.color = curses.COLOR_CYAN


class Piece_S(Piece):
    def __init__(self, board):
        super(Piece_S, self).__init__(board)
        self.layouts = [
            [(-1, 0), (-1, 1), (0, -1), (0, 0)],
            [(-1, 0), (0, 0), (0, 1), (1, 1)],
        ]
        self.color = curses.COLOR_GREEN


class Piece_Z(Piece):
    def __init__(self, board):
        super(Piece_Z, self).__init__(board)
        self.layouts = [
            [(-1, -1), (-1, 0), (0, 0), (0, 1)],
            [(-1, 1), (0, 0), (0, 1), (1, 0)],
        ]
        self.color = curses.COLOR_RED


class Piece_O(Piece):
    def __init__(self, board):
        super(Piece_O, self).__init__(board)
        self.layouts = [
            [(-1, -1), (-1, 0), (0, -1), (0, 0)]
        ]
        self.color = curses.COLOR_WHITE


class Piece_L(Piece):
    def __init__(self, board):
        super(Piece_L, self).__init__(board)
        self.layouts = [
            [(-1, 1), (0, -1), (0, 0), (0, 1)],
            [(-1, 0), (0, 0), (1, 0), (1, 1)],
            [(0, -1), (0, 0), (0, 1), (1, -1)],
            [(-1, -1), (-1, 0), (0, 0), (1, 0)],
        ]
        self.color = curses.COLOR_YELLOW


class Piece_J(Piece):
    def __init__(self, board):
        super(Piece_J, self).__init__(board)
        self.layouts = [
            [(-1, -1), (0, -1), (0, 0), (0, 1)],
            [(-1,  0), (-1, 1), (0, 0), (1, 0)],
            [(0, -1), (0, 0), (0, 1), (1, 1)],
            [(-1, 0), (0, 0), (1, -1), (1, 0)],
        ]
        self.color = curses.COLOR_BLUE


def tetris_main(stdscr):
    b = Board(stdscr)
    b.main()

curses.wrapper(tetris_main)
