import curses

from isoptera import Isoptera


def main(screen: curses.window):
    screen.clear()

    width, height = screen.getmaxyx()
    isoptera = Isoptera(width, height, )
