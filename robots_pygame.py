__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

import pygame, sys, time
from pygame.locals import *
from enum import Enum
from itertools import chain
from robots_direction import D
from robots_mode import *
import copy
from robots_distributed_3x3 import RobotsDistributed3X3IOuputTwoLines, RobotsDistributed3X3IOuputFourLines

class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (120, 186, 0)
    BLUE = (0, 106, 193)
    YELLOW = (244, 179, 0)
    GRAY = (100, 100, 100)
    DARKGREY = (50, 50, 50)
    NAVYBLUE = (60, 60, 100)

rob_size_col = 14
rob_size_row = 20
WINDOWWIDTH = 1090
WINDOWHEIGHT = 685
MARGIN = 10
BGCOLOR = Colors.BLUE

class GameRect(object):
    def __init__(self, surface, display, posx, posy, width, height, forecolor=Colors.GRAY, bgcolor=Colors.BLUE,
                 legend=None, fontcolor=Colors.BLACK, font='freesansbold.ttf', fontsize=32, rectwidth=0):
        self._x = posx
        self._y = posy
        self._width = width
        self._height = height
        self._display = display
        self._surface = surface
        self._forecolor = forecolor
        self._bgcolor = bgcolor
        self._rectwidth = rectwidth
        self.legend = legend
        self.fontcolor = fontcolor
        self._font = font
        self.fontObj = pygame.font.Font(font, fontsize)

    def __contains__(self, otherobj):
        if (self._x <= otherobj._x) and ((self._x + self._width) >= (otherobj._x + otherobj._width)) and (
                    self._y <= otherobj._y) and ((self._y + self._height) >= (otherobj._y + otherobj._height)):
            return True
        else:
            return False

    def erase(self):
        pygame.draw.rect(self._surface, self._bgcolor, (self._x, self._y, self._width, self._height))
        self._display.update()

    def _drawtext(self):
        if self.legend:
            textSurfaceObj = self.fontObj.render(self.legend, True, self.fontcolor)
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (self._x + self._width / 2, self._y + self._height / 2)
            self._surface.blit(textSurfaceObj, textRectObj)

    def _drawtext_legend(self, legend):
        textSurfaceObj = self.fontObj.render(legend, True, self.fontcolor)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (self._x + self._width / 2, self._y + self._height / 2)
        self._surface.blit(textSurfaceObj, textRectObj)

    def draw(self):
        pygame.draw.rect(self._surface, self._forecolor, (self._x, self._y, self._width, self._height), self._rectwidth)
        self._drawtext()
        self._display.update()

    def redraw(self):
        self.erase()
        self.draw()

    def mouseinside(self, mousex, mousey):
        if GameRect(None, None, mousex, mousey, 1, 1) in self:
            return True
        else:
            return False

class Text(GameRect):
    def __init__(self, surface, display, posx, posy, width, height, forecolor=Colors.BLUE,
                 bgcolor=Colors.BLUE, legend='Text', fontcolor=Colors.WHITE,
                 font='freesansbold.ttf', fontsize=14):
        GameRect.__init__(self, surface, display, posx, posy, width, height, forecolor, bgcolor, legend, fontcolor,
                          font, fontsize)
        self.fontObj = pygame.font.SysFont('comicsansms', fontsize + 2)
        # self.fontObj = pygame.font.SysFont('arialblack', fontsize)
        # self.fontObj = pygame.font.SysFont('arial', fontsize)

    def draw(self):
        self._drawtext()
        self._display.update()

    def animatepress(self, wait=0.1, classaction=None):
        pass

    def update_text_number(self, number):
        legend = str(number)
        pygame.draw.rect(self._surface, self._forecolor, (self._x, self._y, self._width, self._height), self._rectwidth)
        textSurfaceObj = self.fontObj.render(legend, True, self.fontcolor)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (self._x + self._width / 2, self._y + self._height / 2)
        self._surface.blit(textSurfaceObj, textRectObj)
        self._display.update()


class Button(GameRect):
    def __init__(self, surface, display, posx, posy, width, height, buttonaction=None, forecolor=Colors.GRAY,
                 bgcolor=Colors.GRAY, pressedcolor=Colors.GRAY, legend='Button', fontcolor=Colors.WHITE,
                 font='freesansbold.ttf', fontsize=32):
        GameRect.__init__(self, surface, display, posx, posy, width, height, forecolor, bgcolor, legend, fontcolor,
                          font, fontsize)
        self.__pressedcolor = pressedcolor
        self.__pressed = False
        self.__buttonaction = buttonaction
        self.fontObj = pygame.font.Font(font, fontsize)

    def animatepress(self, wait=0.1, classaction=None):
        if self.__pressed:
            self.unpress()
        self.press(classaction)
        time.sleep(wait)
        self.unpress()

    def press(self, classaction=None):
        pygame.draw.rect(self._surface, self.__pressedcolor, (self._x, self._y, self._width, self._height))
        self._drawtext()
        self._display.update()
        self.__pressed = True
        if self.__buttonaction and classaction:
            method = getattr(classaction, self.__buttonaction)
            method()

    def unpress(self):
        pygame.draw.rect(self._surface, self._forecolor, (self._x, self._y, self._width, self._height))
        self._drawtext()
        self._display.update()
        self.__pressed = False

    def update_text_pause_resume(self, flag):
        if flag:
            legend = "Resume"
        else:
            legend = "Pause"
        pygame.draw.rect(self._surface, self._forecolor, (self._x, self._y, self._width, self._height), self._rectwidth)
        textSurfaceObj = self.fontObj.render(legend, True, self.fontcolor)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (self._x + self._width / 2, self._y + self._height / 2)
        self._surface.blit(textSurfaceObj, textRectObj)
        self._display.update()

    def update_text_number(self, number):
        legend = str(number)
        pygame.draw.rect(self._surface, self._forecolor, (self._x, self._y, self._width, self._height), self._rectwidth)
        textSurfaceObj = self.fontObj.render(legend, True, self.fontcolor)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (self._x + self._width / 2, self._y + self._height / 2)
        self._surface.blit(textSurfaceObj, textRectObj)
        self._display.update()

class Checkbox(Button):
    def __init__(self, surface, display, posx, posy, width=15, height=15, buttonaction=None, forecolor=Colors.GREEN,
                 bgcolor=Colors.GRAY, pressedcolor=Colors.GREEN, legend='', fontcolor=Colors.WHITE,
                 font='freesansbold.ttf', fontsize=0):
        Button.__init__(self, surface, display, posx, posy, width, height, buttonaction=buttonaction, forecolor=forecolor,
                 bgcolor=bgcolor, pressedcolor=pressedcolor, legend=legend, fontcolor=fontcolor,
                 font=font, fontsize=fontsize)
        self.checked = True

    def draw(self):
        w = 2
        w2 = 2 * 2
        if self.checked:
            pygame.draw.rect(self._surface, (230, 230, 230), (self._x, self._y, self._width, self._height), self._rectwidth)
            pygame.draw.rect(self._surface, (98, 146, 0), (self._x+w, self._y+w, self._width - w2, self._height - w2), self._rectwidth)
            self._display.update()
        else:
            pygame.draw.rect(self._surface, (230, 230, 230), (self._x, self._y, self._width, self._height), self._rectwidth)
            self._display.update()

    def clicked(self):
        self.checked = not self.checked
        self.draw()

    def unpress(self):
        pass

class Slab(GameRect):
    def __init__(self, surface, display, posx, posy, length, legend, margin=5, bgcolor=Colors.GRAY, fontsize=20,
                 color=Colors.YELLOW):
        GameRect.__init__(self, surface, display, posx, posy, length, length, color, bgcolor, legend, fontsize=fontsize)
        self.__length = length
        self.__margin = margin
        self.fontObj = pygame.font.Font(self._font, fontsize)

class Container(GameRect):
    def __init__(self, surface, display, posx, posy, width, height, color=Colors.BLACK, bgcolor=Colors.BLUE,
                 rectwidth=5):
        GameRect.__init__(self, surface, display, posx, posy, width, height, color, bgcolor, rectwidth=rectwidth)
        self._objects = list()

    def redrawall(self):
        for obj in self._objects:
            assert isinstance(obj, GameRect)
            obj.redraw()

    def _addobject(self, obj):
        assert obj in self
        self._objects.append(obj)

    def handleclick(self, x, y, classaction=None):
        for obj in self._objects:
            if obj.mouseinside(x, y):
                obj.animatepress(classaction=classaction)

    def addButton(self, relx, rely, width, height, buttonaction=None, forecolor=Colors.GRAY, pressedcolor=Colors.GRAY,
                  legend='Button', fontcolor=Colors.BLACK, font='freesansbold.ttf', fontsize=32):
        self._addobject(Button(self._surface, self._display, self._x + relx, self._y + rely, width, height,
                               buttonaction=buttonaction, bgcolor=self._bgcolor, forecolor=forecolor, fontcolor=fontcolor,
                               pressedcolor=pressedcolor, legend=legend, fontsize=fontsize))
    def add_text(self, relx, rely, width, height, forecolor=Colors.BLUE,
                  legend='Text', fontcolor=Colors.BLACK, fontsize=14):
        self._addobject(Text(self._surface, self._display, self._x + relx, self._y + rely, width, height,
                             forecolor=forecolor, legend=legend, fontcolor=fontcolor, fontsize=fontsize))

class Board(Container):
    def __init__(self, surface, display, posx, posy, width, height, color=Colors.BLACK, bgcolor=Colors.BLUE,
                 rectwidth=5, slabsize=32, margin=5):
        Container.__init__(self, surface, display, posx, posy, width, height, color=color, bgcolor=bgcolor,
                           rectwidth=rectwidth)
        self.__slabsize = slabsize
        self.__margin = margin

        self.MODE = Mode.INPUT_OUTPUT_TWO_LINES

        self.button_stop = None
        self.button_number_elections = None
        self.button_number_steps     = None

        self.mat = None
        self.pos_real_dict = {}
        self.matrix_slab = [[None for y in range(rob_size_row)] for x in range(rob_size_col)]
        self.prev_3x3 = []
        self.click_count = -2
        self.click_input = None
        self.click_output = None
        self.click_pos    = []
        self.minimum_number_of_robots = 0
        self.menu = None
        self.running   = False
        self.start_game = False
        self.flag_stop = False
        self.reset_1   = 1
        self.reset_2   = 0
        self.number_election = 0
        self.number_steps = 0

        self.checkbox_1 = None
        self.checkbox_2 = None
        self.checkbox_3 = None
        self.checkbox_4 = None
        self.checkbox_5 = None
        self.checkbox_6 = None
        self.checkbox_7 = None

        self.move_3x3_enabled = True
        self.move_5x5_enabled = False

        self.push_enabled = True
        self.pull_enabled = True
        self.carry_enabled = True
        self.must_be_connected = False
        self.two_paths = False

    def checkboxaction_1(self):
        self.checkbox_1.draw()
        if self.running:
            return
        if self.start_game:
            return
        self.move_3x3_enabled = not self.move_3x3_enabled
        self.checkbox_1.clicked()

    def checkboxaction_2(self):
        self.checkbox_2.draw()
        if self.running:
            return
        if self.start_game:
            return
        self.move_5x5_enabled = not self.move_5x5_enabled
        self.checkbox_2.clicked()

    def checkboxaction_3(self):
        self.checkbox_3.draw()
        if self.running:
            return
        if self.start_game:
            return
        self.push_enabled = not self.push_enabled
        self.checkbox_3.clicked()

    def checkboxaction_4(self):
        self.checkbox_4.draw()
        if self.running:
            return
        if self.start_game:
            return
        self.pull_enabled = not self.pull_enabled
        self.checkbox_4.clicked()

    def checkboxaction_5(self):
        self.checkbox_5.draw()
        if self.running:
            return
        if self.start_game:
            return
        self.carry_enabled = not self.carry_enabled
        self.checkbox_5.clicked()

    def checkboxaction_6(self):
        self.checkbox_6.draw()
        if self.running:
            return
        if self.start_game:
            return
        self.must_be_connected = not self.must_be_connected
        self.checkbox_6.clicked()

    def checkboxaction_7(self):
        self.checkbox_7.draw()
        if self.running:
            return
        if self.start_game:
            return
        self.two_paths = not self.two_paths
        if self.two_paths:
            self.MODE = Mode.INPUT_OUTPUT_FOUR_LINES
        else:
            self.MODE = Mode.INPUT_OUTPUT_TWO_LINES
        self.checkbox_7.clicked()

    def add_button_stop(self, relx, rely, width, height, buttonaction=None, forecolor=Colors.GRAY, pressedcolor=Colors.GRAY,
                  legend='Button', fontcolor=Colors.BLACK, font='freesansbold.ttf', fontsize=32):
        self.button_stop = Button(self._surface, self._display, self._x + relx, self._y + rely, width, height,
                               buttonaction=buttonaction, bgcolor=self._bgcolor, forecolor=forecolor, fontcolor=Colors.WHITE,
                               pressedcolor=pressedcolor, legend=legend, fontsize=fontsize)
        self._addobject(self.button_stop)

    def new_slab(self, i, j, color, legend):
        return Slab(self._surface, self._display,
                    self._y + self.__margin * (j + 1) + self.__slabsize * j,
                    self._x + self.__margin * (i + 1) + self.__slabsize * i,
                    self.__slabsize, legend,
                    fontsize=15, color=color)

    def set_local_3x3(self, which, x, y):
        if not self.running:
            return
        time.sleep(0.3)
        pos_list = []
        self.prev_3x3 = []
        d = 1
        if self.move_5x5_enabled:
            d = 2
        for _i, _p in self.pos_real_dict.iteritems():
            if abs(_p[0] - x) <= d and abs(_p[1] - y) <= d:
                pos_list.append(_p)
                self.prev_3x3.append(_i)
        for p in pos_list:
            i = int(p[0])
            j = int(p[1])
            slab = self.new_slab(i, j, Colors.GREEN, str(int(self.mat[(i, j)])))
            self.matrix_slab[i][j] = slab
            slab.draw()
        self.assure_input_output_color()

    def unset_local_3x3(self):
        if not self.running:
            return
        time.sleep(0.3)
        for _i in self.prev_3x3:
            p = self.pos_real_dict[_i]
            i = int(p[0])
            j = int(p[1])
            slab = self.new_slab(i, j, Colors.YELLOW, str(int(self.mat[(i, j)])))
            self.matrix_slab[i][j] = slab
            slab.draw()
        self.assure_input_output_color()

    def show_move_without_refresh(self, hist):
        if not self.running:
            return
        self.number_election += 1
        self.button_number_elections.update_text_number(self.number_election)
        for h in hist:
            to_be_erased = {}
            to_be_added  = {}
            time.sleep(0.3)
            self.number_steps += 1
            for i in range(len(h) / 2):
                w = h[2 * i] + 1
                direction = h[2 * i + 1]
                (x, y) = self.pos_real_dict[w]
                to_be_erased[w] = (x, y)
                if direction == D.LEFT:
                    x -= 1
                elif direction == D.RIGHT:
                    x += 1
                elif direction == D.UP:
                    y += 1
                elif direction == D.DOWN:
                    y -= 1
                to_be_added[w] = (x, y)

            for _i, _p in to_be_erased.iteritems():
                x, y = _p[0], _p[1]
                self.mat[(x, y)] = 0
                self.matrix_slab[x][y].erase()
                self.matrix_slab[x][y] = None

            for _i, _p in to_be_added.iteritems():
                x, y = _p[0], _p[1]
                self.mat[(x, y)] = _i
                self.pos_real_dict[_i] = (x, y)

            for _i, _p in to_be_added.iteritems():
                x, y = _p[0], _p[1]
                slab = self.new_slab(x, y, Colors.GREEN, str(int(self.mat[(x, y)])))
                self.matrix_slab[x][y] = slab
                slab.draw()
            self.button_number_steps.update_text_number(self.number_steps)
        self.assure_input_output_color()

    def start(self):
        if self.minimum_number_of_robots != self.click_count - 1:
            return
        if self.running:
            return
        if not self.click_input:
            return
        if not self.click_output:
            return
        if (not self.move_3x3_enabled) and (not self.move_5x5_enabled):
            return
        self.reset_2 = self.reset_1
        self.running = True
        POS = {}
        for i in range(len(self.click_pos)):
            POS[i] = self.click_pos[i]
            self.pos_real_dict[i+1] = self.click_pos[i]
        if self.MODE == Mode.INPUT_OUTPUT_TWO_LINES:
            robot_distributed_3x3 = RobotsDistributed3X3IOuputTwoLines(rob_size_col, rob_size_row, POS,
                                    self.click_input, self.click_output)
        elif self.MODE == Mode.INPUT_OUTPUT_FOUR_LINES:
            robot_distributed_3x3 = RobotsDistributed3X3IOuputFourLines(rob_size_col, rob_size_row, POS,
                                    self.click_input, self.click_output)
        robot_distributed_3x3.grid_board = self
        robot_distributed_3x3.pull_enabled = self.pull_enabled
        robot_distributed_3x3.push_enabled = self.push_enabled
        robot_distributed_3x3.carry_enabled = self.carry_enabled
        robot_distributed_3x3.must_be_connected = self.must_be_connected
        robot_distributed_3x3.move_3x3_enabled = self.move_3x3_enabled
        robot_distributed_3x3.move_5x5_enabled = self.move_5x5_enabled
        robot_distributed_3x3.update_mat_real()
        self.mat = copy.deepcopy(robot_distributed_3x3.MAT_REAL)
        robot_distributed_3x3.main_distributed()

    def detect_stop_and_reset(self):
        for i in range(1):
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if self.mouseinside(x, y):
                        self.handleclick(x, y, self)
        _stop = self.flag_stop
        _reset = (self.reset_2 > self.reset_1)
        self.reset_2 = self.reset_1
        return _stop, _reset

    def stop(self):
        if not self.running:
            self.flag_stop = False
        else:
            self.flag_stop = not self.flag_stop

    def assure_input_output_color(self):
        if not self.running:
            return
        if (not self.click_input) or (not self.click_output):
            return
        i, j = self.click_input[0], self.click_input[1]
        if self.mat[(i, j)] <= 0:
            slab = self.new_slab(i, j, Colors.RED, "IN")
            slab.draw()
            self.matrix_slab[i][j] = slab
        else:
            slab = self.new_slab(i, j, Colors.RED, str(int(self.mat[(i, j)])))
            slab.draw()
            self.matrix_slab[i][j] = slab

        i, j = self.click_output[0], self.click_output[1]
        if self.mat[(i, j)] <= 0:
            slab = self.new_slab(i, j, Colors.RED, "OUT")
            slab.draw()
            self.matrix_slab[i][j] = slab
        else:
            slab = self.new_slab(i, j, Colors.RED, str(int(self.mat[(i, j)])))
            slab.draw()
            self.matrix_slab[i][j] = slab

    def draw_for_select(self):
        self.mat = None
        self.pos_real_dict = {}
        self.matrix_slab = [[None for y in range(rob_size_row)] for x in range(rob_size_col)]
        self.prev_3x3 = []
        self.click_count = -2
        self.click_input = None
        self.click_output = None
        self.click_pos = []
        self.minimum_number_of_robots = 0
        self.running = False
        self.start_game = False
        self.flag_stop = False
        self.reset_2 += 1
        self.number_election = 0
        self.number_steps = 0
        if self.button_number_elections:
            self.button_number_elections.update_text_number(self.number_election)
        if self.button_number_steps:
            self.button_number_steps.update_text_number(self.number_steps)
        for i in range(rob_size_col):
            for j in range(rob_size_row):
                self.add_and_draw_slab(i, j, Colors.GRAY, "")
        self.redrawall()

    def redrawall(self):
        self.draw()
        for obj in self._objects:
            assert isinstance(obj, GameRect)
            obj.redraw()
        for slab in chain.from_iterable(zip(*self.matrix_slab)):
            if slab:
                slab.redraw()

    def eraseall(self):
        for slab in chain.from_iterable(zip(*self.matrix_slab)):
            if slab:
                slab.erase()

    def add_and_draw_slab(self, i, j, color, legend):
        self.matrix_slab[i][j] = self.new_slab(i, j, color, legend)

    def wait_for_exit(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    print "quit"
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if self.mouseinside(x, y):
                        self.handleclick(x, y, self)

    def click_input_action(self, i, j):
        self.start_game = True
        self.click_count += 1
        self.click_input = (i, j)
        slab = self.new_slab(i, j, Colors.RED, "IN")
        slab.draw()
        self.matrix_slab[i][j] = slab

    def click_output_action(self, i, j):
        if (i, j) != self.click_input:
            self.click_count += 1
            self.click_output = (i, j)
            slab = self.new_slab(i, j, Colors.RED, "OUT")
            slab.draw()
            self.matrix_slab[i][j] = slab
            p_in = self.click_input
            p_out = self.click_output
            self.minimum_number_of_robots = abs(p_in[0] - p_out[0]) + abs(p_in[1] - p_out[1]) + 1
            if self.MODE == Mode.INPUT_OUTPUT_FOUR_LINES:
                self.minimum_number_of_robots = 2 * (abs(p_in[0] - p_out[0]) + abs(p_in[1] - p_out[1]))

    def click_pos_action(self, i, j):
        if (i, j) not in self.click_pos and self.minimum_number_of_robots >= self.click_count:
            self.click_count += 1
            self.click_pos.append((i, j))
            slab = self.new_slab(i, j, Colors.YELLOW, str(self.click_count))
            slab.draw()
            self.matrix_slab[i][j] = slab

    def handleclick(self, x, y, classaction=None):
        find = False
        for obj in self._objects:
            if obj.mouseinside(x, y):
                find = True
                obj.animatepress(classaction=classaction)
                self.button_stop.update_text_pause_resume(self.flag_stop)
        if find:
            return
        if self.running:
            return
        for i in range(rob_size_col):
            for j in range(rob_size_row):
                if not self.matrix_slab[i][j]:
                    continue
                if self.matrix_slab[i][j].mouseinside(x, y):
                    if self.running:
                        return
                    elif self.click_count == -2:
                        self.click_input_action(i, j)
                    elif self.click_count == -1:
                        self.click_output_action(i, j)
                    else:
                        self.click_pos_action(i, j)

class RobotsGridSelectAndDraw(object):
    def __init__(self):
        pygame.init()
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('')
        DISPLAYSURF.fill(BGCOLOR)
        pygame.display.update()
        SLABSIZE = 40
        MARGIN = 5
        self.grid_board = Board(DISPLAYSURF, pygame.display, 20, 20,
                    rob_size_row * SLABSIZE + (rob_size_row) * MARGIN + 155,
                    rob_size_col * SLABSIZE + (rob_size_col + 1) * MARGIN,
                    slabsize=SLABSIZE, margin=MARGIN, color=Colors.GRAY, bgcolor=BGCOLOR)

        self.grid_board.draw_for_select()

        dy = -40
        self.grid_board.addButton(930, 70 + dy, 100, 50, buttonaction='start', forecolor=Colors.GREEN, fontcolor=Colors.WHITE,
                       pressedcolor=Colors.GREEN, legend='Start', fontsize=16)
        self.grid_board.add_button_stop(930, 135 + dy, 100, 50, buttonaction='stop', forecolor=Colors.GREEN,
                    pressedcolor=Colors.GREEN, legend='Pause', fontsize=16)
        self.grid_board.addButton(930, 195 + dy, 100, 50, buttonaction='draw_for_select',
                       forecolor=Colors.GREEN, pressedcolor=Colors.GREEN, fontcolor=Colors.WHITE,
                       legend='Reset', fontsize=16)

        self.grid_board.add_text(918, 275 + dy, 120, 20,  forecolor=Colors.BLUE,  fontcolor=Colors.WHITE,
                                  legend='Num of elections', fontsize=14)
        self.grid_board.button_number_elections = Text(DISPLAYSURF, pygame.display, 935, 320 + dy, 120, 20,
                                  forecolor=Colors.BLUE,  fontcolor=Colors.WHITE, legend='0', fontsize=20)
        self.grid_board._addobject(self.grid_board.button_number_elections)

        self.grid_board.add_text(920, 330 + dy, 120, 20,
                                  forecolor=Colors.BLUE,  fontcolor=Colors.WHITE,
                                  legend='Num of steps', fontsize=14)
        self.grid_board.button_number_steps = Text(DISPLAYSURF, pygame.display, 935, 375 + dy, 120, 20,
                                  forecolor=Colors.BLUE, fontcolor=Colors.WHITE, legend='0', fontsize=20)
        self.grid_board._addobject(self.grid_board.button_number_steps)


        checkbox_x = 938
        cy = 15
        checkbox_y = 23 + cy
        self.grid_board.checkbox_1 = Checkbox(DISPLAYSURF, pygame.display, checkbox_x - 3, 440 + dy - cy, buttonaction='checkboxaction_1')
        self.grid_board._addobject(self.grid_board.checkbox_1)
        self.grid_board.add_text(checkbox_x, 440 + dy - checkbox_y, 100, 20,  forecolor=Colors.BLUE,
                                   fontcolor=Colors.WHITE,
                                  legend='3x3 view', fontsize=14)


        self.grid_board.checkbox_2 = Checkbox(DISPLAYSURF, pygame.display, checkbox_x - 3, 480 + dy - cy, buttonaction='checkboxaction_2')
        self.grid_board._addobject(self.grid_board.checkbox_2)
        self.grid_board.add_text(checkbox_x, 480 + dy - checkbox_y, 100, 20, forecolor=Colors.BLUE,
                                  fontcolor=Colors.WHITE,
                                  legend='5x5 view', fontsize=14)
        self.grid_board.checkbox_2.clicked()

        self.grid_board.checkbox_3 = Checkbox(DISPLAYSURF, pygame.display, checkbox_x - 3, 520 + dy - cy, buttonaction='checkboxaction_3')
        self.grid_board._addobject(self.grid_board.checkbox_3)
        self.grid_board.add_text(checkbox_x, 520 + dy - checkbox_y, 100, 20, forecolor=Colors.BLUE,
                                  fontcolor=Colors.WHITE,
                                  legend='push enabled', fontsize=14)

        self.grid_board.checkbox_4 = Checkbox(DISPLAYSURF, pygame.display, checkbox_x - 3, 560 + dy - cy, buttonaction='checkboxaction_4')
        self.grid_board._addobject(self.grid_board.checkbox_4)
        self.grid_board.add_text(checkbox_x, 560 + dy - checkbox_y, 100, 20, forecolor=Colors.BLUE,
                                  fontcolor=Colors.WHITE,
                                  legend='pull enabled', fontsize=14)

        self.grid_board.checkbox_5 = Checkbox(DISPLAYSURF, pygame.display, checkbox_x - 3, 600 + dy - cy, buttonaction='checkboxaction_5')
        self.grid_board._addobject(self.grid_board.checkbox_5)
        self.grid_board.add_text(checkbox_x, 600 + dy - checkbox_y, 100, 20, forecolor=Colors.BLUE,
                                  fontcolor=Colors.WHITE,
                                  legend='carry enabled', fontsize=14)

        self.grid_board.checkbox_6 = Checkbox(DISPLAYSURF, pygame.display, checkbox_x - 3, 640 + dy - cy, buttonaction='checkboxaction_6')
        self.grid_board._addobject(self.grid_board.checkbox_6)
        self.grid_board.add_text(checkbox_x, 634 + dy - checkbox_y, 100, 20, forecolor=Colors.BLUE,
                                  fontcolor=Colors.WHITE,
                                  legend='always', fontsize=14)
        self.grid_board.add_text(checkbox_x, 653 + dy - checkbox_y, 100, 20, forecolor=Colors.BLUE,
                                 fontcolor=Colors.WHITE,
                                 legend='connected', fontsize=14)
        self.grid_board.checkbox_6.clicked()

        self.grid_board.checkbox_7 = Checkbox(DISPLAYSURF, pygame.display, checkbox_x - 3, 680 + dy - cy, buttonaction='checkboxaction_7')
        self.grid_board._addobject(self.grid_board.checkbox_7)
        self.grid_board.add_text(checkbox_x, 680 + dy - checkbox_y, 100, 20, forecolor=Colors.BLUE,
                                  fontcolor=Colors.WHITE,
                                  legend='two paths', fontsize=14)
        self.grid_board.checkbox_7.clicked()

        self.grid_board.draw_for_select()
        self.grid_board.wait_for_exit()

