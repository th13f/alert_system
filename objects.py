from solver import Star


class Department(object):
    def __init__(self, pos, to_kill, layer, barriers, symbol):
        self.x = pos[0]
        self.y = pos[1]
        self.to_kill = to_kill
        self.layer = layer
        self.width = len(self.layer[0])
        self.height = len(self.layer)
        self.barriers = barriers
        self.symbol = symbol
        self.layer[self.y][self.x] = self.symbol
        self.path = None
        self.home = (self.y,self.x)

    def next_target(self):
        for i in xrange(0, self.height):
            for j in xrange(0, self.width):
                if self.layer[i][j] in self.to_kill:
                    return i, j
        return -1, -1

    def find_path(self, target):
        solver = Star((self.y, self.x), target, 'queen', self.barriers)
        while not solver.solution:
            solver.evaluate()
        return solver.solution

    def aim(self):
        next = self.next_target()
        if next == (-1, -1):
            if (self.y,self.x) != self.home:
                path = self.find_path(self.home)
            else:
                path = None
        else:
            path = self.find_path(next)
        self.path = path

    def next(self):
        if self.path:
            return self.path.pop()
        else:
            self.aim()
            return None