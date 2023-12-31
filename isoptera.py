from time import time

import cv2
import numpy as np
import tqdm

DIRECTIONS = {
    0:  # north
        np.array((0, -1), dtype=np.int16),
    1:  # east
        np.array((1, 0), dtype=np.int16),
    2:  # south
        np.array((0, 1), dtype=np.int16),
    3:  # west
        np.array((-1, 0), dtype=np.int16),
}

TURN = {
    1:  # no turn
        np.array((0, 0), dtype=np.int16),
    2:  # turn right
        np.array((1, 0), dtype=np.int16),
    4:  # turn around
        np.array((2, 0), dtype=np.int16),
    8:  # turn left
        np.array((3, 0), dtype=np.int16),
}

ORIENTATION_TO_STR = {
    0: "north",
    1: "east",
    2: "south",
    3: "west",
}

EXPANDING_FRAME = [[[1, 8, 0], [1, 2, 1]], [[0, 2, 0], [0, 8, 1]]]
CHAOS = [[[1, 2, 0], [1, 2, 1]], [[0, 1, 0], [0, 1, 1]]]
FIB_SPIRAL = [[[1, 8, 1], [1, 8, 1]], [[1, 2, 1], [0, 1, 0]]]
TEXTURED = [[[1, 2, 1], [1, 8, 1]], [[1, 2, 1], [0, 2, 0]]]
DIAMOND = [[[0, 1, 1], [0, 2, 1]], [[1, 8, 0], [0, 1, 1]]]
SPIRAL = [[[1, 1, 1], [1, 8, 0]], [[1, 2, 1], [0, 1, 0]]]
BINARY_COUNTER = [[[1, 2, 0], [0, 1, 0]]]
# noinspection SpellCheckingInspection
LANGTONS_ANT = [[[1, 2, 0], [0, 8, 0]]]
SNOWFLAKE = [[[1, 8, 1], [1, 2, 0]], [[1, 4, 1], [1, 4, 2]], [[0, 0, 0], [0, 4, 0]]]

# https://en.wikipedia.org/wiki/Turmite
ISOPTERA = {
    "expanding frame": (EXPANDING_FRAME, 223577),
    "chaotic": (CHAOS, 8342),
    "fibonacci spiral": (FIB_SPIRAL, 10211),
    "textured": (TEXTURED, 65932),
    "diamond": (DIAMOND, 31380),
    "spiral": (SPIRAL, 12536),
    # "binary": BINARY_COUNTER,
    "langton's ant": (LANGTONS_ANT, 27731),
    "snowflake": (SNOWFLAKE, 306000),
}


class Isoptera:
    def __init__(self, width: int, height: int, states: list[list[list[int]]],
                 start: int, blank: int = 0):
        super().__init__()
        # initialize 2D tape
        self.tape = np.zeros((width, height), dtype=np.int16)

        # make the center of the tape the current position
        self.pos = np.array((width // 2, height // 2), dtype=np.int16)
        # 0: north, 1: east, 2: south, 3: west
        self.orientation = 0

        # initialize the state
        self.q0 = start
        # self.F = {final}
        self.b = blank
        self.Sigma = {0, 1}
        self.Gamma = {0, 1}
        self.Q = range(len(states))
        self.q = self.Q[self.q0]
        self.F = {}

        # initialize the transition function as an ndarray
        self.delta: np.ndarray = np.array(states, dtype=np.int16)

    def print_delta(self):
        print("     0       1")
        for i in range(self.delta.shape[0]):
            print(f"{i} ", end="")
            for j in range(self.delta.shape[1]):
                print(f"{self.delta[i, j]} ", end="")
            print()

    def step(self):
        if self.q in self.F:
            # halt
            raise StopIteration

        # get current symbol
        cur_symbol = self.tape[*self.pos]
        old_q = self.q

        # get transition
        t = self.delta[old_q, cur_symbol]
        symbol: int = t[0]
        turn: int = t[1]
        self.q = t[2]

        # turn
        match turn:
            case 1:
                pass
            case 2:
                self.orientation = (self.orientation + 1) % 4
            case 4:
                self.orientation = (self.orientation + 2) % 4
            case 8:
                self.orientation = (self.orientation + 3) % 4

        # write
        self.tape[*self.pos] = symbol

        # move
        match self.orientation:
            case 0:
                self.pos[0] -= 1
            case 1:
                self.pos[1] += 1
            case 2:
                self.pos[0] += 1
            case 3:
                self.pos[1] -= 1

        # wrap around
        self.pos %= self.tape.shape
        # print(f"delta[{old_q}, {cur_symbol}] = {t}\n{self.pos} {ORIENTATION_TO_STR[self.orientation]}\n")

    def __iter__(self):
        return self

    def __next__(self):
        self.step()
        return self.tape, self.pos, self.q

    def __str__(self):
        s = f"{self.q} {self.pos} {self.orientation}\n"
        for y in range(self.tape.shape[1]):
            for x in range(self.tape.shape[0]):
                if (x, y) == tuple(self.pos):
                    s += "X"
                else:
                    s += '#' if self.tape[x, y] else ' '
            s += "\n"
        return s

    def __repr__(self):
        return f"Isoptera({self.tape.shape[0]}, {self.tape.shape[1]}, {self.Q}, {self.q0}, {self.F}, {self.b})"

    # noinspection PyUnboundLocalVariable
    def run(self, iterations: int, duration: int, video: bool = False):
        fps = 30
        ipf = iterations // (duration * fps)

        if video:
            out = cv2.VideoWriter("isoptera.mp4", cv2.VideoWriter_fourcc(*"MP4V"), fps, (800, 800))
        print(f"running {iterations} iterations ({duration} seconds) at {fps} fps ({ipf} iterations per frame)")
        print("press q to stop")

        img = np.ones((self.tape.shape[0], self.tape.shape[1], 3), dtype=np.uint8) * 255
        _ipf = 0
        loop_duration = 1 / fps
        for i in tqdm.tqdm(range(iterations)):
            next_t = time() + loop_duration
            self.step()

            if _ipf < ipf:
                _ipf += 1
                continue
            _ipf = 0
            # print(f"\r{i}/{iterations} ({i / iterations * 100:.2f}%)", end="")
            img[:, :] = (255, 255, 255)
            img[self.tape == 1] = (0, 0, 0)
            img[self.pos[0], self.pos[1]] = (0, 0, 255)
            final = cv2.resize(img, (500, 500), interpolation=cv2.INTER_NEAREST)
            if video:
                out.write(final)
            cv2.imshow("isoptera", final)
            if cv2.waitKey(1) == ord('q'):
                break
            while time() < next_t:
                pass

        if video:
            out.release()
        img = np.zeros((self.tape.shape[0], self.tape.shape[1], 3), dtype=np.uint8)
        img[self.tape == 1] = (255, 255, 255)
        img[self.pos[0], self.pos[1]] = (0, 0, 255)
        img = cv2.resize(img, (500, 500), interpolation=cv2.INTER_NEAREST)
        cv2.imshow("isoptera", img)
        cv2.waitKey(0)
