from classes import Screen, Player, KeyboardThread, Game
from classes import is_linux

import os
import sys
import time

FPS = 1 / 15
INPUT_DELAY = FPS
SPACE_CHR = ' '

input_thread = None
game = None
player = None
screen = None


def change_terminal_size(columns, lines):
    if is_linux:
        pass
    else:
        os.system('mode con: cols=' + str(columns) + ' lines=' + str(lines))


def get_terminal_size():
    return os.get_terminal_size().lines, os.get_terminal_size().columns


def start_keyboard_thread():
    global input_thread
    input_thread = KeyboardThread(INPUT_DELAY)
    input_thread.start()


def keyboard_handler():
    if input_thread.keysPressed["up"]:
        player.veloc.y = -1 * abs(player.veloc.y)
    if input_thread.keysPressed["down"]:
        player.veloc.y = abs(player.veloc.y)
    if input_thread.keysPressed["left"]:
        player.veloc.x = -1 * abs(player.veloc.x)
    if input_thread.keysPressed["right"]:
        player.veloc.x = abs(player.veloc.x)
    if input_thread.keysPressed["exit"]:
        finish()
    if input_thread.keysPressed["restart"]:
        restart()


def restart():
    game.GAMEOVER = False
    game.save_highscore()
    init()


def finish():
    clear_screen()
    input_thread.stop()
    game.save_highscore()
    sys.exit()


def clear_screen():
    if is_linux:
        os.system("clear")
    else:
        os.system("cls")


def update():
    # milestone check:
    game.milestone_checker(game.score)
    # update positions:
    player.x += player.veloc.x
    player.y += player.veloc.y
    for enemy in game.enemies_list:
        enemy.x += enemy.veloc.x
        enemy.y += enemy.veloc.y
    # wall collision:
    hit_wall = False
    if player.x + player.width - 1 >= screen.columns:
        player.x = screen.columns - player.width
        player.change_dir_x()
        hit_wall = True
    elif player.x < 0:
        player.x = 0
        player.change_dir_x()
        hit_wall = True
    if player.y + player.height - 1 >= screen.lines:
        player.y = screen.lines - player.height
        player.change_dir_y()
        hit_wall = True
    elif player.y < 0:
        player.y = 0
        player.change_dir_y()
        hit_wall = True
    if hit_wall:
        player.speed_up()
        game.score += 1
    for enemy in game.enemies_list:
        hit_wall = False
        if enemy.x + enemy.width - 1 >= screen.columns:
            hit_wall = True
            enemy.x = screen.columns - enemy.width
            enemy.change_dir_x()
        elif enemy.x < 0:
            hit_wall = True
            enemy.x = 0
            enemy.change_dir_x()
        if enemy.y + enemy.height >= screen.lines:
            hit_wall = True
            enemy.y = screen.lines - enemy.height
            enemy.change_dir_y()
        elif enemy.y < 0:
            hit_wall = True
            enemy.y = 0
            enemy.change_dir_y()
        if hit_wall:
            enemy.speed_up()
            game.score += 1
    # player-enemy collision:
    for enemy in game.enemies_list:
        for i in range(enemy.width):
            for j in range(enemy.height):
                for w in range(player.width):
                    for h in range(player.height):
                        if int(player.x + w) == int(enemy.x + i) and int(player.y + h) == int(enemy.y + j):
                            game.GAMEOVER = True
                            break


def render():
    # fill the space:
    screen.matrix = [[SPACE_CHR for i in range(screen.columns)] for j in range(screen.lines)]
    # render stuff on screen:
    for enemy in game.enemies_list:
        for i in range(enemy.height):
            for j in range(enemy.width):
                screen.matrix[int(enemy.y) + i][int(enemy.x) + j] = enemy.shape[i][j]
    for i in range(player.height):
        for j in range(player.width):
            screen.matrix[int(player.y) + i][int(player.x) + j] = player.shape[i][j]
    # show everything:
    for i in screen.matrix:
        for j in i:
            sys.stdout.write(str(j))
    for i in range(screen.columns):
        sys.stdout.write("-")
    sys.stdout.write(" " + game.milestone_message + "\n\r")
    for i in range(screen.columns):
        sys.stdout.write("-")
    if game.score > game.highscore:
        game.highscore = game.score
    sys.stdout.write(" Survivalist Rect! | High Score: " + str(game.highscore) + " | Score: " +
                     str(game.score) + " | " + ("Game Over! \n\r " if game.is_gameover() else ""))
    sys.stdout.flush()
    # first show the collision on the screen, then the game is over if it's over :)
    if game.is_gameover():
        time.sleep(1.2)
        restart()


def init():
    global game, player, screen
    # init screen:
    lines, columns = get_terminal_size()
    lines -= 1 + 4  # to fit in cmd properly + score line
    matrix = [[SPACE_CHR * columns] for j in range(lines)]
    screen = Screen(lines, columns, matrix)
    # init game, enemies and player:
    game = Game(1, screen.columns, screen.lines)
    game.generate_enemies()
    player = Player.generate(screen)


def main():
    init()
    start_keyboard_thread()
    running = True
    while running:
        start = time.time()
        # input:
        keyboard_handler()
        # update:
        update()
        # show on screen:
        clear_screen()
        render()
        # delay:
        delay = FPS - (time.time() - start)
        if delay > 0:
            time.sleep(delay)


try:
    main()
except Exception:
    raise
