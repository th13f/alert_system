from solver import Star
from random import randint

class Department(object):
    def __init__(self, pos, fire, chem, layer, barriers, symbol):
        self.x = pos[0]
        self.y = pos[1]
        self.fire = fire
        self.chem = chem
        self.layer = layer
        self.width = len(self.layer[0])
        self.height = len(self.layer)
        self.barriers = barriers
        self.symbol = symbol
        self.layer[self.y][self.x] = self.symbol
        self.path = None
        self.home = (self.y,self.x)
        self.fire_timer = 0
        self.chem_timer = 0

    def next_target(self):
        for i in xrange(0, self.height):
            for j in xrange(0, self.width):
                if self.chem_timer > 0:
                    if self.layer[i][j] == self.chem:
                        return i, j
                if self.fire_timer > 0:
                    if self.layer[i][j] == self.fire:
                        return i, j
        return -1, -1

    def find_path(self, target):
        solver = Star((self.y, self.x), target, 'queen', self.barriers)
        while not solver.solution:
            solver.evaluate()
        return solver.solution

    def go_home(self):
        if (self.y,self.x) != self.home:
            path = self.find_path(self.home)
        else:
            path = None
        return path

    def aim(self):
        next = self.next_target()
        if (next == (-1, -1)) or (self.fire_timer == 0 and self.chem_timer == 0):
            path = self.go_home()
        else:
            path = self.find_path(next)
        self.path = path

    def next(self):
        if self.path:
            return self.path.pop()
        else:
            self.aim()
            return None
        if self.chem_timer > 0:
            self.chem_timer -= 1
        if self.fire_timer > 0:
            self.fire_timer -= 1

class Plague(object):
    def __init__(self, layers, layer, barriers_ids, symbol, wait_for):
        self.barriers_ids = barriers_ids
        self.symbol = symbol
        self.layers = layers
        self.layer = layer
        self.height = len(layers[0])
        self.width = len(layers[0][0])
        self.wait_for = wait_for
        self.i = 0

    def new(self, pos):
        self.layer[pos[1]][pos[0]] = self.symbol

    def tick(self):
        if self.i == 0:
            self.i = self.wait_for
            for y in xrange(0,self.height):
                for x in xrange(0,self.width):
                    if self.layer[y][x] == self.symbol:
                        dir = randint(0,8+1)
                        if dir == 0:
                            x_dir, y_dir = -1, -1
                        elif dir == 1:
                            x_dir, y_dir = 0, -1
                        elif dir == 2:
                            x_dir, y_dir = 1, -1
                        elif dir == 3:
                            x_dir, y_dir = 1, 0
                        elif dir == 4:
                            x_dir, y_dir = 1, 1
                        elif dir == 5:
                            x_dir, y_dir = 0, 1
                        elif dir == 6:
                            x_dir, y_dir = -1, 1
                        elif dir == 7:
                            x_dir, y_dir = -1, 0
                        else:
                            x_dir, y_dir = 0, 0

                        can_go = True
                        for layer in self.layers:
                            if layer[y+y_dir][x+x_dir] in self.barriers_ids:
                                can_go = False
                        if can_go:
                            self.layer[y+y_dir][x+x_dir] = self.symbol
        else:
            self.i -= 1


class Sensor(object):
    def __init__(self, layer, to_find, symbol, sensors_array):
        self.symbol = symbol
        self.layer = layer
        self.height = len(layer)
        self.width = len(layer[0])
        self.to_find = to_find
        self.sensors = sensors_array
        self.area = 6

    def new(self, pos):
        self.layer[pos[1]][pos[0]] = self.symbol

    def tick(self):
        for sensor in self.sensors:
            for y in xrange(max(0, sensor[0]-self.area), min(self.height, sensor[0]+self.area)):
                for x in xrange(max(0, sensor[1]-self.area), min(self.width, sensor[1]+self.area)):
                    if self.layer[y][x] == self.to_find:
                        return True
        return False