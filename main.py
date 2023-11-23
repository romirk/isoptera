#!/usr/bin/env python3
from simple_term_menu import TerminalMenu

from isoptera import ISOPTERA, Isoptera


def main():
    isoptera_options = list(ISOPTERA.keys())
    isoptera_menu = TerminalMenu(isoptera_options, title="isoptera")
    isoptera_index: int = isoptera_menu.show()
    length_menu = TerminalMenu(["short", "medium", "long"], title="length")
    duration = [5, 15, 30][length_menu.show()]
    video_menu = TerminalMenu(["no", "yes"], title="export video?")
    export_video = bool(video_menu.show())

    isoptera, iterations = ISOPTERA[isoptera_options[isoptera_index]]
    iso = Isoptera(200, 200, isoptera, 0)
    iso.run(iterations, duration, export_video)


if __name__ == '__main__':
    main()
