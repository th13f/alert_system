import pygame
from pygame.surface import Surface
from pytmx import load_pygame
from objects import Department, Plague, Sensor, Veil


class Interface(object):
    GROUND_INDEX = 0
    EFFECTS_INDEX = 1
    OBJECTS_INDEX = 2

    FIRE_MODE = 2
    CHEM_MODE = 1
    INACTIVE_MODE = 0

    def __init__(self, bg_color, display):
        self.animate = False
        self.cell_size = (10, 10)

        self.image = Surface(display)
        self.image.fill(pygame.Color(bg_color))

        self.fon = Surface(self.cell_size)
        self.fon.fill(pygame.Color(bg_color))
        self.bg_color = bg_color

        self.font = pygame.font.SysFont("calibri", 18)
        self.rendered = {}
        self.map = load_pygame("maps/map.tmx")

        Interface.SENSOR_CHEM_ID = self.map.gidmap[1][0][0]
        Interface.CHEM_ID = self.map.gidmap[2][0][0]
        Interface.DEPARTMENT_ID = self.map.gidmap[3][0][0]
        Interface.FIRE_ID = self.map.gidmap[4][0][0]
        Interface.SENSOR_MANUAL_ID = self.map.gidmap[5][0][0]
        Interface.SENSOR_FIRE_ID = self.map.gidmap[6][0][0]
        Interface.REPOSITORY_ID = self.map.gidmap[7][0][0]
        Interface.WATER_ID = self.map.gidmap[8][0][0]
        Interface.VEIL_ID = self.map.gidmap[9][0][0]
        Interface.WALL_ID = self.map.gidmap[10][0][0]
        Interface.FON_ID = 0

        Interface.FIRE_MSG = "FIRE_ALERT"
        Interface.CHEM_MSG = "CHEM_ALERT"
        Interface.NEW_FIRE_MSG = "NEW_FIRE"
        Interface.NEW_CHEM_MSG = "NEW_CHEM"
        Interface.NEW_INACTIVE_MSG = "NEW_INACTIVE"

        self.ground_layer = self.map.get_layer_by_name("Ground").data
        self.effects_layer = self.map.get_layer_by_name("Effects").data
        self.objects_layer = self.map.get_layer_by_name("Objects_tiles").data
        self.height = self.map.height
        self.width = self.map.width
        barriers_ids = [Interface.WALL_ID, Interface.VEIL_ID, Interface.SENSOR_CHEM_ID,
                        Interface.SENSOR_FIRE_ID, Interface.SENSOR_MANUAL_ID]
        plague_barriers_ids = barriers_ids + [Interface.WATER_ID, Interface.DEPARTMENT_ID,
                                              Interface.FIRE_ID, Interface.CHEM_ID]
        self.barriers = self.setup_barriers([self.ground_layer, self.objects_layer],
                                            barriers_ids)
        fire_sensors = self.setup_barriers([self.objects_layer, ], [Interface.SENSOR_FIRE_ID, ])
        chem_sensors = self.setup_barriers([self.objects_layer, ], [Interface.SENSOR_CHEM_ID, ])
        veils = self.setup_barriers([self.objects_layer, ], [Interface.VEIL_ID, ])
        self.department = Department((32, 42), Interface.FIRE_ID, Interface.CHEM_ID,
                                     self.objects_layer, self.barriers, Interface.DEPARTMENT_ID)
        self.fire = Plague([self.objects_layer, self.effects_layer, self.ground_layer], self.objects_layer,
                           plague_barriers_ids, Interface.FIRE_ID, 20)
        self.chem = Plague([self.objects_layer, self.effects_layer, self.ground_layer], self.objects_layer,
                           plague_barriers_ids, Interface.CHEM_ID, 35)
        self.veil = Veil(self.effects_layer, self.objects_layer, self.VEIL_ID, self.WATER_ID, self.FIRE_ID,
                         veils, self.department)
        self.fire_sensor = Sensor(self.objects_layer, Interface.FIRE_ID, Interface.SENSOR_FIRE_ID, fire_sensors)
        self.chem_sensor = Sensor(self.objects_layer, Interface.CHEM_ID, Interface.SENSOR_CHEM_ID, chem_sensors)
        self.text_dict = {
            self.FIRE_MSG: ["FIRE ALERT!", (1005, 20)],
            self.CHEM_MSG: ["CHEM ALERT!", (1005, 35)],
        }
        self.messages = ['', '']
        self.mode = self.INACTIVE_MODE


    def move_object(self, obj, end):
        symbol = obj.symbol
        start_i = obj.y
        start_j = obj.x
        self.objects_layer[end[0]][end[1]] = symbol
        self.objects_layer[start_i][start_j] = 0
        obj.x = end[1]
        obj.y = end[0]

    def update(self):
        for y in xrange(0, self.height):
            for x in xrange(0, self.width):
                image = self.map.get_tile_image(x, y, Interface.OBJECTS_INDEX)
                if not image:
                    image = self.map.get_tile_image(x, y, Interface.EFFECTS_INDEX)
                    if not image:
                        image = self.map.get_tile_image(x, y, Interface.GROUND_INDEX)
                        if not image:
                            image = self.fon
                self.image.blit(image, (x * 10, y * 10))
        self.fire.tick()
        self.chem.tick()
        fire = self.fire_sensor.tick()
        chem = self.chem_sensor.tick()
        self.veil.tick()
        if fire:
            self.department.fire_timer = 30
            self.messages[0] = Interface.FIRE_MSG
        else:
            if Interface.FIRE_MSG in self.rendered:
                self.rendered.pop(Interface.FIRE_MSG)
                self.messages[0] = ''
        if chem:
            self.department.chem_timer = 30
            self.messages[1] = Interface.CHEM_MSG
        else:
            if Interface.CHEM_MSG in self.rendered:
                self.rendered.pop(Interface.CHEM_MSG)
                self.messages[1] = ''

        next = self.department.next()
        if next:
            self.move_object(self.department, next)

        if self.mode == self.INACTIVE_MODE:
            self.image.blit(self.fon, (1005, 100))
        elif self.mode == self.FIRE_MODE:
            self.image.blit(self.map.images[self.FIRE_ID], (1005, 100))
        elif self.mode == self.CHEM_MODE:
            self.image.blit(self.map.images[self.CHEM_ID], (1005, 100))

        self.render_text()
        for text in self.text_dict:
            if text in self.rendered:
                self.image.blit(self.rendered[text][0], self.rendered[text][1])


    def setup_barriers(self, layers, bad_indexes):
        barriers = set()
        for layer in layers:
            for y in xrange(0, self.height):
                for x in xrange(0, self.width):
                    if layer[y][x] in bad_indexes:
                        barriers.add((y, x))
        return barriers


    def render_each(self, specific, text_dict):
        msg, loc = text_dict[specific]
        rend = self.font.render(msg, 1, (0, 0, 0))
        rect = pygame.Rect(rend.get_rect(topleft=loc))
        self.rendered[specific] = [rend, rect]

    def render_text(self):
        self.image.fill(pygame.Color(self.bg_color), (1000, 0, 100, 100))
        for msg in self.messages:
            if msg != '':
                self.render_each(msg, self.text_dict)

    def make_fire(self, pos):
        self.fire.new(pos)

    def make_chem(self, pos):
        self.chem.new(pos)

    def new_object(self, (x, y)):
        if self.mode == self.FIRE_MODE:
            self.make_fire((x / 10, y / 10))
        elif self.mode == self.CHEM_MODE:
            self.make_chem((x / 10, y / 10))