import sys
import os
from random import randint, uniform, choice
from time import sleep
from threading import Thread

if os.name == 'nt':
    is_linux = False
    import msvcrt
    from msvcrt import getch
elif os.name == 'posix':
    is_linux = True
    import termios
    import tty


class Screen:

    def __init__(self, lines, columns, matrix):
        self.lines = lines
        self.columns = columns
        self.matrix = matrix


class MovingObject:
    FILL_CHARS = ":./\\-|"
    MAX_VELOC = 0.85
    SPEED_UP_VAR = MAX_VELOC / 50

    def __init__(self, x, y, width, height, shape, veloc):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shape = [row[:] for row in shape]
        self.veloc = veloc

    def speed_up(self):
        if abs(self.veloc.x) < MovingObject.MAX_VELOC:
            if self.veloc.x < 0:
                self.veloc.x -= MovingObject.SPEED_UP_VAR
            else:
                self.veloc.x += MovingObject.SPEED_UP_VAR
            if self.veloc.y < 0:
                self.veloc.y -= MovingObject.SPEED_UP_VAR
            else:
                self.veloc.y += MovingObject.SPEED_UP_VAR

    def change_dir_x(self):
        self.veloc.x = -1 * self.veloc.x

    def change_dir_y(self):
        self.veloc.y = -1 * self.veloc.y

    @staticmethod
    def generate_random(min_size, max_size, min_veloc, max_veloc, screen_height):
        width = randint(min_size, max_size)
        height = randint(min_size, max_size)
        fill_char = MovingObject.FILL_CHARS[randint(0, len(MovingObject.FILL_CHARS) - 1)]
        shape = [[fill_char for i in range(width)] for j in range(height)]
        random_num = uniform(min_veloc, max_veloc)
        veloc = Vector2(random_num * 1 if choice([True, False]) else -1,
                        random_num * 1 if choice([True, False]) else -1)
        return MovingObject(randint(0, 5), randint(0, screen_height - 1), width, height, shape, veloc)


class Player(MovingObject):
    MAX_VELOC = 1.3
    SPEED_UP_VAR = MAX_VELOC / 50
    FILL_CHAR = "X"

    def __init__(self, x, y, width, height, shape, veloc):
        super().__init__(x, y, width, height, shape, veloc)

    def speed_up(self):
        if abs(self.veloc.x) < Player.MAX_VELOC:
            if self.veloc.x < 0:
                self.veloc.x -= Player.SPEED_UP_VAR
            else:
                self.veloc.x += Player.SPEED_UP_VAR
            if self.veloc.y < 0:
                self.veloc.y -= Player.SPEED_UP_VAR
            else:
                self.veloc.y += Player.SPEED_UP_VAR

    def change_dir_x(self):
        self.veloc.x = -1 * self.veloc.x

    def change_dir_y(self):
        self.veloc.y = -1 * self.veloc.y

    @staticmethod
    def generate(screen):
        width = randint(2, 3)
        height = randint(2, 3)
        shape = [[Player.FILL_CHAR for i in range(width)] for j in range(height)]
        veloc = Vector2(0.7 * 1 if choice([True, False]) else -1, 0.7 * 1 if choice([True, False]) else -1)
        return Player(screen.columns // 2, screen.lines // 2, width, height, shape, veloc)


class KeyboardThread:

    def __init__(self, delay_time):
        self.delay_time = delay_time
        self.keysPressed = {"exit": False, "restart": False, "up": False, "down": False, "right": False, "left": False}
        self.started = False

    def win32_get_input(self, delay_time):
        while self.started:
            if msvcrt.kbhit():
                key = ord(getch())
                if key == 112:  # p
                    self.keysPressed["exit"] = True
                if key == 114:  # r
                    self.keysPressed["restart"] = True
                if key == 119:  # w
                    self.keysPressed["up"] = True
                if key == 97:  # a
                    self.keysPressed["left"] = True
                if key == 115:  # s
                    self.keysPressed["down"] = True
                if key == 100:  # d
                    self.keysPressed["right"] = True
            sleep(delay_time)
            # set all to False:
            for key in self.keysPressed.keys():
                self.keysPressed[key] = False

    @staticmethod
    def linux_getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def linux_get_input(self, delay_time):
        while self.started:
            key = KeyboardThread.linux_getch()
            if key == "p":
                self.keysPressed["exit"] = True
            if key == "r":
                self.keysPressed["restart"] = True
            if key == "w":
                self.keysPressed["up"] = True
            if key == "a":
                self.keysPressed["left"] = True
            if key == "s":
                self.keysPressed["down"] = True
            if key == "d":
                self.keysPressed["right"] = True
            sleep(delay_time)
            # set all to False:
            for key in self.keysPressed.keys():
                self.keysPressed[key] = False

    def start(self):
        global is_linux
        self.started = True
        if is_linux:
            thread = Thread(target=KeyboardThread.linux_get_input, args=[self, self.delay_time])
            thread.start()
        else:
            thread = Thread(target=KeyboardThread.win32_get_input, args=[self, self.delay_time])
            thread.start()

    def stop(self):
        self.started = False


class Vector2:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Game:
    GAMEOVER = False
    DATA_FILE = "data.game"
    MILESTONE_LIST = [
        5, 15, 30, 50, 100, 150, 250, 500, 750, 1000, 1500, 2500, 5000, 7500, 10_000,
        15_000, 25_000, 50_000, 75_000, 100_000, 250_000, 500_000, 1_000_000, 1_000_000_000
    ]
    MILESTONE_MSGS = [
        "One more enemy at each milestone.",
        "Each time they hit the wall, they become faster! (up to a max).",
        "They enter from the left side.",
        "Yes, you can hold the keys. But more score -> more enemies!",
        "Bigger screen -> better survival chance!",
        "Do you know about the first version of Tetris?",
        "Can you make it a 4-digit? But first half of it.",
        "The thing is starting to happen!",
        "Almost impossible!",
        "Nice, you did it! How far can you get?",
        "I'm running out of sentences at this point.",
        "Just kidding! Keep going, dude!",
        "Alright, wana lose now?",
        "Nice dodges, little shape!",
        "It's getting interesting, isn't it?",
        "Keep avoiding them, little one!",
        "A determined one. I like it.",
        "You're almost getting there.",
        "Wow, look how far you've come!",
        "This is getting out of control.",
        "Are you sure you're not cheating?",
        "It's absolutely ridiculous. Anyway,",
        "Are you f***ing kidding me? Stop it.",
        "Sh*t. Just stop it. seriously. Have mercy on your computer."
    ]

    def __init__(self, enemy_num, screen_width, screen_height):
        self.score = 0
        self.enemy_num = enemy_num
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies_list = []
        self.milestone_check = {}
        self.milestone_message = "Hit the wall, avoid the object(s)! (keys: w s a d / r / p) Milestone at 5"
        for milestone in Game.MILESTONE_LIST:
            self.milestone_check[milestone] = False
        try:
            with open(Game.DATA_FILE, 'r') as f:
                content = f.readlines()
                content = [x.strip() for x in content]
                self.highscore = int(content[0])
        except IOError:
            with open(Game.DATA_FILE, 'w') as f:
                f.write('0\n')
            self.highscore = 0

    def generate_enemies(self):
        for i in range(self.enemy_num):
            self.enemies_list.append(
                MovingObject.generate_random(1, 7, 0.2, 0.5, self.screen_height))

    def add_enemy(self, num):
        self.enemy_num += num
        for i in range(num):
            self.enemies_list.append(
                MovingObject.generate_random(1, 7, 0.5, 0.7, self.screen_height))

    def save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
        try:
            with open(Game.DATA_FILE, 'w') as f:
                f.write(str(self.highscore) + '\n')
        except IOError:
            raise

    def milestone_checker(self, score):
        for i in range(1, len(Game.MILESTONE_LIST)):
            if Game.MILESTONE_LIST[i] > score >= Game.MILESTONE_LIST[i - 1]:
                self.milestone_message = Game.MILESTONE_MSGS[i - 1] + " Next at " + str(Game.MILESTONE_LIST[i])
                if not self.milestone_check[Game.MILESTONE_LIST[i - 1]]:
                    self.add_enemy(1)
                    self.milestone_check[Game.MILESTONE_LIST[i - 1]] = True
                break

    def is_gameover(self):
        return self.GAMEOVER
