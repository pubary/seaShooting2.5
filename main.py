from time import sleep
from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел за пределы поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Выстрел в эту клетку уже был!'


class BoardWrongShipException(BoardException):
    pass


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def __eq__(self, anyone):
        return self.x == anyone.x and self.y == anyone.y


class Ship:
    def __init__(self, base_point, length, direction):
        self.base_point = base_point
        self.length = length
        self.direction = direction
        self.lives = length

    @property
    def points(self):
        ship_points = []

        for i in range(self.length):
            step_x = self.base_point.x
            step_y = self.base_point.y

            if self.direction == 0:
                step_x += i

            elif self.direction == 1:
                step_y += i

            ship_points.append(Point(step_x, step_y))

        return ship_points

    def shooting(self, shot):
        return shot in self.points


class Board:
    def __init__(self, size=6, hid=False):
        self.count = 0
        self.size = size
        self.hid = hid
        self.busy = []
        self.fine_shot = []
        self.ships = []
        self.field = [['○'] * size for _ in range(size)]

    def add_ship(self, ship):
        for p in ship.points:
            if self.out(p) or p in self.busy:
                raise BoardWrongShipException()

        for p in ship.points:
            self.field[p.x][p.y] = '░'
            self.busy.append(p)

        self.ships.append(ship)
        self.perimeter(ship)

    def perimeter(self, ship, show=False):
        per = [(-1, -1), (-1, 0), (-1, 1),
               (0, -1), (0, 0), (0, 1),
               (1, -1), (1, 0), (1, 1)]

        for p in ship.points:
            for dx, dy in per:
                near = Point(p.x + dx, p.y + dy)
                if not (self.out(near)) and not (self.busy_check(near)):
                    if show:
                        self.field[near.x][near.y] = '●'
                    self.busy.append(near)

    def busy_check(self, p):
        return p in self.busy

    def out(self, p):
        return not ((0 <= p.x < self.size) and (0 <= p.y < self.size))

    def shot(self, p):
        if self.busy_check(p):
            raise BoardUsedException()

        if self.out(p):
            raise BoardOutException()

        self.busy.append(p)

        for ship in self.ships:
            if p in ship.points:
                ship.lives -= 1
                self.field[p.x][p.y] = '█'
                if ship.lives == 0:
                    self.count += 1
                    self.perimeter(ship, show=True)
                    self.fine_shot.append(p)
                    print('Корабль уничтожен!')
                    return True
                else:
                    self.fine_shot.append(p)
                    print('Корабль повреждён!')
                    return True

        self.field[p.x][p.y] = "●"
        print('Мимо!')
        return False

    def __str__(self, size=6):
        self.size = size
        res = '  |'
        for u in range(size):
            res += f' {u + 1} |'
        for w, row in enumerate(self.field):
            res += f'\n{w + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:
            res = res.replace('░', '○')
        return res

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, player_board, enemy_board):
        self.player_board = player_board
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):

        def target_selection():
            target_kit = []
            target_points = [(-1, 0), (0, -1), (0, 1), (1, 0)]
            for p in self.enemy_board.fine_shot:
                for dx, dy in target_points:
                    next_target = Point(p.x + dx, p.y + dy)
                    if not self.enemy_board.out(next_target) and not self.enemy_board.busy_check(next_target):
                        target_kit.append(next_target)

            if len(target_kit):

                for p in target_kit:
                    a1 = Point(p.x + 1, p.y)
                    a2 = Point(p.x + 2, p.y)
                    b1 = Point(p.x, p.y + 1)
                    b2 = Point(p.x, p.y + 2)
                    c1 = Point(p.x - 1, p.y)
                    c2 = Point(p.x - 2, p.y)
                    d1 = Point(p.x, p.y - 1)
                    d2 = Point(p.x, p.y - 2)

                    if any([(a1 and a2 in self.enemy_board.fine_shot),
                            (b1 and b2 in self.enemy_board.fine_shot),
                            (c1 and c2 in self.enemy_board.fine_shot),
                            (d1 and d2 in self.enemy_board.fine_shot)]):
                        ts = p
                        break
                    else:
                        ts = target_kit[0]
            else:
                ts = Point(randint(0, 5), randint(0, 5))
            return ts

        while True:
            p = target_selection()
            try:
                if self.enemy_board.busy_check(p):
                    raise BoardWrongShipException()
                break
            except BoardWrongShipException:
                pass

        sleep(3)
        print(f'Ход компьютера: {p.x + 1} {p.y + 1}')

        return p


class User(Player):
    def ask(self):
        while True:
            coordinates = input('Ваш ход: ').split()

            if len(coordinates) != 2:
                print(' Введите 2 координаты! ')
                continue

            x, y = coordinates

            if not (x.isdigit()) or not (y.isdigit()):
                print(' Введите числа! ')
                continue

            x, y = int(x), int(y)
            return Point(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        self.ship_lens = [3, 2, 2, 1, 1, 1]
        human_board = self.random_board()
        comp_board = self.random_board()
        comp_board.hid = True

        self.ai = AI(comp_board, human_board)
        self.us = User(human_board, comp_board)

    def random_place(self):
        board = Board(size=self.size)
        creations = 0
        for sL in self.ship_lens:
            while True:
                creations += 1
                if creations > 2000:
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), sL, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    @staticmethod
    def poster():
        print(f'\n'
              f'                        и г р а        \n'
              f'                      МОРСКОЙ  БОЙ        \n'
              f'\n'
              f' формат ввода: x y  (x - № строки, y - № столбца)\n')

    def game_step(self):
        num = 0

        def print_boards():
            print('̅' * 60)
            print('      Ваша доска' + ' ' * 22 + 'Доска компьютера')
            us_board = str(self.us.player_board).split('\n')
            ai_board = str(self.ai.player_board).split('\n')
            us_ai = ''
            for i in range(len(us_board)):
                us_ai += ''.join(us_board[i]) + ' ' * 5 + ''.join(ai_board[i]) + '\n'
            print(us_ai)
            return

        while True:
            print_boards()

            if num % 2 == 0:
                print('̅' * 60)
                print('Вы ходите...')
                repeat = self.us.move()
            else:
                print('̅' * 60)
                print('Компьютер ходит...')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.player_board.count == len(self.ship_lens):
                print('̅' * 60)
                print_boards()
                print('Вы выиграли!')
                break

            if self.us.player_board.count == len(self.ship_lens):
                print('̅' * 25)
                print_boards()
                print('Компьютер выиграл!')
                break

            num += 1


if __name__ == '__main__':
    g = Game()
    g.poster()
    g.game_step()
