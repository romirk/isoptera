import cv2
import numpy as np

from tm import TuringMachine

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
    0:  # no turn
        np.array((0, 0), dtype=np.int16),
    1:  # turn right
        np.array((1, 0), dtype=np.int16),
    2:  # turn around
        np.array((2, 0), dtype=np.int16),
    8:  # turn left
        np.array((3, 0), dtype=np.int16),
}

EXPANDING_FRAME = [[[1, 8, 0], [1, 2, 1]], [[0, 2, 0], [0, 8, 1]]]
CHAOS = [[[1, 1, 0], [1, 1, 1]], [[0, 0, 0], [0, 0, 1]]]


class Isoptera(TuringMachine):
    def __init__(self, width: int, height: int, states: list[list[list[int]]],
                 start: int, final: int, blank: int = 0):
        super().__init__()
        # initialize 2D tape
        self.tape = np.zeros((width, height), dtype=np.int16)

        # make the center of the tape the current position
        self.pos = np.array((width // 2, height // 2), dtype=np.int16)
        self.orientation = 0

        # initialize the state
        self.q0 = start
        self.F = {final}
        self.b = blank
        self.Sigma = {0, 1}
        self.Gamma = {0, 1}
        self.Q = range(len(states))
        self.q = self.Q[self.q0]

        # initialize the transition function as an ndarray
        self.delta: np.ndarray = np.array(states, dtype=np.int16)

    def step(self):
        if self.q in self.F:
            # halt
            raise StopIteration

        # get current symbol
        symbol = self.tape[*self.pos]

        # get transition
        t = self.delta[self.q, symbol]
        symbol: int = t[0]
        turn: int = t[1]
        self.q = t[2]

        # turn
        match turn:
            case 0:
                pass
            case 1:
                self.orientation = (self.orientation + 1) % 4
            case 2:
                self.orientation = (self.orientation + 2) % 4
            case 8:
                self.orientation = (self.orientation + 3) % 4

        # write
        self.tape[*self.pos] = symbol

        # move
        match self.orientation:
            case 0:
                self.pos[1] -= 1
            case 1:
                self.pos[0] += 1
            case 2:
                self.pos[1] += 1
            case 3:
                self.pos[0] -= 1

        # wrap around
        self.pos %= self.tape.shape

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


if __name__ == '__main__':
    iso = Isoptera(200, 200, CHAOS, 0, 2)
    for i in range(10000):
        # print(iso)
        iso.step()
        # if i % 1000:
        #     continue
        img = np.zeros((iso.tape.shape[0], iso.tape.shape[1], 3), dtype=np.uint8)
        img[iso.tape == 1] = (255, 255, 255)
        img[iso.pos[0], iso.pos[1]] = (0, 0, 255)
        img = cv2.resize(img, (800, 800))
        cv2.imshow("isoptera", img)
        cv2.waitKey(1)

    img = np.zeros((iso.tape.shape[0], iso.tape.shape[1], 3), dtype=np.uint8)
    img[iso.tape == 1] = (255, 255, 255)
    img[iso.pos[0], iso.pos[1]] = (0, 0, 255)
    img = cv2.resize(img, (800, 800))
    cv2.imshow("isoptera", img)
    cv2.waitKey(0)
