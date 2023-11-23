class TuringMachine:
    def __init__(self):
        self.Q = set()
        "The set of states"
        self.Gamma = set()
        "The tape alphabet"
        self.b = None
        "The blank symbol"
        self.Sigma = set()
        "The input alphabet"
        self.delta = dict()
        "The transition function"
        self.q0 = None
        "The start state"
        self.F = set()
        "The set of final states"
        self.tape = None
        "The tape"
        self.pos = None
        "The current position on the tape"
