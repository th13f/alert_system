"""Module: interface.py
Overview: The core of the GUI for the A* demo.
Classes:
    Interface(object):
        Methods:
            __init__(self)
            make_background(self)
            reset(self,full=True)
            setup_barriers(self)
            render_text(self,specific=None)
            get_target(self)
            get_event(self,event)
            left_button_clicked(self)
            right_button_clicked(self)
            hotkeys(self,event)
            toggle_animate(self)
            toggle_piece(self,ind=None)
            add_barriers(self)
            update(self,Surf)
            found_solution(self)
            fill_cell(self,cell,color,Surf)
            center_number(self,cent,string,color,Surf)
            draw(self,Surf)
            draw_solve(self,Surf)
            draw_start_end_walls(self,Surf)
            draw_messages(self,Surf)"""
import pygame
from pygame.surface import Surface
from pytmx import load_pygame
from objects import Department
import solver


class Interface(object):
    GROUND_INDEX = 0
    EFFECTS_INDEX = 1
    OBJECTS_INDEX = 2

    def __init__(self, bg_color, display):
        self.animate = False
        self.cell_size = (10, 10)

        self.image = Surface(display)
        self.image.fill(pygame.Color(bg_color))

        self.fon = Surface(self.cell_size)
        self.fon.fill(pygame.Color(bg_color))

        self.font = pygame.font.SysFont("arial", 13)
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

        self.ground_layer = self.map.get_layer_by_name("Ground").data
        self.effects_layer = self.map.get_layer_by_name("Effects").data
        self.objects_layer = self.map.get_layer_by_name("Objects_tiles").data
        self.height = self.map.height
        self.width = self.map.width
        barriers_ids = [Interface.WALL_ID, Interface.VEIL_ID, Interface.SENSOR_CHEM_ID,
                        Interface.SENSOR_FIRE_ID, Interface.SENSOR_MANUAL_ID]
        fire_barriers_ids = barriers_ids + [Interface.WATER_ID, Interface.DEPARTMENT_ID,
                                            Interface.FIRE_ID, Interface.CHEM_ID]
        self.barriers = self.setup_barriers([self.ground_layer, self.objects_layer],
                                            barriers_ids)
        self.fire_barriers = self.setup_barriers([self.ground_layer, self.objects_layer, self.effects_layer],
                                                 fire_barriers_ids)
        self.department = Department((32, 42), [Interface.FIRE_ID, Interface.CHEM_ID],
                                     self.objects_layer, self.barriers, Interface.DEPARTMENT_ID)

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
        next = self.department.next()
        if next:
            self.move_object(self.department, next)


    def setup_barriers(self, layers, bad_indexes):
        barriers = set()
        for layer in layers:
            for y in xrange(0, self.height):
                for x in xrange(0, self.width):
                    if layer[y][x] in bad_indexes:
                        barriers.add((y, x))
        return barriers

    def render_text(self, specific=None):
        """Prerender text messages. By default all are rendered. Single messages
        can be rerendered by passing a key corresponding to the below dictionary."""

        def render_each(specific, text_dict):
            msg, loc = text_dict[specific]
            rend = self.font.render(msg, 1, (255, 255, 255))
            rect = pygame.Rect(rend.get_rect(topleft=loc))
            self.rendered[specific] = [rend, rect]

        text = {"START": ["Place your start point:", (10, 1)],
                "GOAL": ["Place your goal:", (10, 1)],
                "BARRIER": ["Draw your walls or press spacebar to solve:", (10, 1)],
                "ENTER": ["Press 'Enter' to restart.", (10, 1)],
                "RESET": ["Press 'i' to reset.", (150, 1)],
                "ANIM": ["Animation: {}".format(["Off", "On"][self.animate]), (340, 1)],
                "MOVE": ["Move type: {}".format(self.piece_type.capitalize()), (320, 263)],
                "TIME": ["Time (ms): {}".format(self.time_end - self.time_start), (100, 263)],
                "FAILED": ["No solution.", (20, 263)],
                "SOLVED": ["Steps: {}".format(len(self.solution)), (20, 263)]}
        if specific:
            render_each(specific, text)
        else:
            for specific in text:
                render_each(specific, text)

    """def update(self, Surf):
        #Primary update logic control flow for the GUI.
        self.add_barriers()
        if self.mode == "RUN":
            if not self.Solver:
                self.time_start = pg.time.get_ticks()
                self.Solver = solver.Star(self.start_cell, self.goal_cell, self.piece_type, self.barriers)
            if self.animate:
                self.Solver.evaluate()
            else:
                while not self.Solver.solution:
                    self.Solver.evaluate()
            if self.Solver.solution:
                self.found_solution()
        if self.mode != "RUN" or self.animate:
            self.draw(Surf)
"""
    def found_solution(self):
        """Sets appropriate mode when solution is found (or failed)."""
        self.time_end = pygame.time.get_ticks()
        if self.Solver.solution == "NO SOLUTION":
            self.mode = "FAILED"
        else:
            self.solution = self.Solver.solution
            self.mode = "SOLVED"
            self.render_text("SOLVED")
        self.render_text("TIME")

    def fill_cell(self, cell, color, Surf):
        """Fills a single cell given coordinates, color, and a target Surface."""
        loc = cell[0] * self.cell_size[0], cell[1] * self.cell_size[1]
        Surf.fill(color, (loc, self.cell_size))
        return pygame.Rect(loc, self.cell_size)

    def center_number(self, cent, string, color, Surf):
        """Used for centering numbers on cells."""
        rend = self.font.render(string, 1, color)
        rect = pygame.Rect(rend.get_rect(center=cent))
        rect.move_ip(1, 1)
        Surf.blit(rend, rect)

    def draw(self, Surf):
        """Calls draw functions in the appropraite order."""
        Surf.fill(0)
        self.draw_solve(Surf)
        self.draw_start_end_walls(Surf)
        Surf.blit(self.image, (0, 0))
        self.draw_messages(Surf)

    def draw_solve(self, Surf):
        """Draws while solving (if animate is on) and once solved."""
        if self.mode in ("RUN", "SOLVED", "FAILED"):
            for cell in self.Solver.closed_set:
                self.fill_cell(cell, (255, 0, 255), Surf)
            if self.mode == "SOLVED":
                for i, cell in enumerate(self.solution):
                    cent = self.fill_cell(cell, (0, 255, 0), Surf).center
                    self.center_number(cent, str(len(self.solution) - i), (0, 0, 0), Surf)

    def draw_start_end_walls(self, Surf):
        """Draw endpoints and barriers."""
        if self.start_cell:
            self.fill_cell(self.start_cell, (255, 255, 0), Surf)
        if self.goal_cell:
            cent = self.fill_cell(self.goal_cell, (0, 0, 255), Surf).center
            if self.mode == "SOLVED":
                self.center_number(cent, str(len(self.solution)), (255, 255, 255), Surf)
        for cell in self.barriers:
            self.fill_cell(cell, (255, 255, 255), Surf)

    def draw_messages(self, Surf):
        """Draws the text (not including cell numbers)."""
        for key in [self.mode, "MOVE", "ANIM"]:
            try:
                Surf.blit(*self.rendered[key])
            except KeyError:
                pass
        if self.mode in ("SOLVED", "FAILED"):
            for rend in ("TIME", "RESET", "ENTER"):
                Surf.blit(*self.rendered[rend])