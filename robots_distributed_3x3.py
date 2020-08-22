__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

from robots_local_view_3x3 import *
from robots_local_move_3x3 import *
import numpy as np
import random
from robots_mode import *
import robots_plot
from robots_obj_value_calculator import *

class RobotsDistributed3X3Base(object):
    def __init__(self, SIZE_COL, SIZE_ROW, POS_INPUT):
        self.MODE                 = None
        self.obj_value_calculator = None
        self.SIZE_COL      = SIZE_COL
        self.SIZE_ROW      = SIZE_ROW
        self.POS_INPUT     = POS_INPUT
        self.MAT_BIGGER, self.POS_BIGGER = self.get_mat_and_pos_bigger(POS_INPUT)
        self.MAT_REAL      = None
        self.hist_enabled  = True
        self.load0_enabled = True
        self.pull_enabled  = True
        self.push_enabled  = True
        self.carry_enabled = True
        self.must_be_connected    = False
        self.occupy_empty_5x5_enabled = True
        self.move_3x3_enabled         = True
        self.move_5x5_enabled         = True
        self.dict_robot_move          = {}
        self.cmap = robots_plot.get_cmap(len(POS_INPUT))

        self.list_robot_move_to_elect = []
        self.robot_move_elected       = None
        self.obj_func_value_elected   = float('-inf')
        self.grid_board               = None

    def get_mat_and_pos_bigger(self, POS_INPUT):
        mat_bigger = np.zeros((self.SIZE_COL + 4, self.SIZE_ROW + 4))
        pos_bigger = {}
        for i in [0, 1, self.SIZE_COL + 2, self.SIZE_COL + 3]:
            for j in range(0, self.SIZE_ROW + 4):
                mat_bigger[(i, j)] = -1
        for i in range(0, self.SIZE_COL + 4):
            for j in [0, 1, self.SIZE_ROW + 2, self.SIZE_ROW + 3]:
                mat_bigger[(i, j)] = -1
        for i, p in POS_INPUT.iteritems():
            mat_bigger[(p[0] + 2, p[1] + 2)] = i + 1
            pos_bigger[i] = (p[0] + 2, p[1] + 2)
        return mat_bigger, pos_bigger

    def update_mat_bigger(self):
        self.MAT_BIGGER = np.zeros((self.SIZE_COL + 4, self.SIZE_ROW + 4))
        for i in [0, 1, self.SIZE_COL + 2, self.SIZE_COL + 3]:
            for j in range(0, self.SIZE_ROW + 4):
                self.MAT_BIGGER[(i, j)] = -1
        for i in range(0, self.SIZE_COL + 4):
            for j in [0, 1, self.SIZE_ROW + 2, self.SIZE_ROW + 3]:
                self.MAT_BIGGER[(i, j)] = -1
        for i, p in self.POS_BIGGER.iteritems():
            self.MAT_BIGGER[(p[0], p[1])] = i + 1

    def update_mat_real(self):
        self.MAT_REAL = np.zeros((self.SIZE_COL, self.SIZE_ROW))
        for i, p in self.POS_BIGGER.iteritems():
            self.MAT_REAL[(p[0] - 2, p[1] - 2)] = i + 1

    def create_dict_robot_move(self):
        self.dict_robot_move = {}
        for i, p in self.POS_BIGGER.iteritems():
            robot_view_3x3 = None
            if self.move_3x3_enabled:
                robot_view_3x3 = RobotLocalView(self.MAT_BIGGER, self.POS_BIGGER, i,
                            self.SIZE_COL, self.SIZE_ROW, False, False)
            robot_view_5x5 = None
            if self.move_5x5_enabled:
                robot_view_5x5 = RobotLocalView(self.MAT_BIGGER, self.POS_BIGGER, i,
                        self.SIZE_COL, self.SIZE_ROW, True, True)
            robot_move = RobotsLocalMove(robot_view_3x3, robot_view_5x5, self.obj_value_calculator, self.hist_enabled, self.load0_enabled,
                        self.pull_enabled, self.push_enabled, self.carry_enabled, self.must_be_connected)
            robot_move.hist_enabled  = self.hist_enabled
            robot_move.load0_enabled = self.load0_enabled
            robot_move.pull_enabled = self.pull_enabled
            robot_move.push_enabled = self.push_enabled
            robot_move.carry_enabled = self.carry_enabled
            robot_move.must_be_connected = self.must_be_connected
            self.dict_robot_move[i] = robot_move

    def conduct_election_distributed(self):
        self.list_robot_move_to_elect = []
        self.obj_func_value_elected = float('-inf')
        for i, p in self.POS_BIGGER.iteritems():
            robot_move_result = self.dict_robot_move[i].get_max_gain()
            if robot_move_result.obj_func_value > self.obj_func_value_elected:
                self.obj_func_value_elected = robot_move_result.obj_func_value
                self.list_robot_move_to_elect = [self.dict_robot_move[i]]
            elif robot_move_result.obj_func_value == self.obj_func_value_elected:
                self.list_robot_move_to_elect.append(self.dict_robot_move[i])

        self.robot_move_elected = random.choice(self.list_robot_move_to_elect)
        for i, p in self.robot_move_elected.robot_move_result.pos.iteritems():
            self.POS_BIGGER[i] = p
        self.update_mat_bigger()
        self.update_mat_real()
        obj_func_value_real = self.obj_value_calculator.get_real_value(self.MAT_REAL, None)
        print "obj_func_value = ", obj_func_value_real

    def main_distributed(self):
        for i in range(200):
            print ""
            print ""
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            print self.MAT_REAL

    def pygame_draw(self):
        which = self.robot_move_elected.robot_view.which
        x = self.robot_move_elected.robot_view.X - 2
        y = self.robot_move_elected.robot_view.Y - 2
        self.grid_board.unset_local_3x3()
        self.grid_board.set_local_3x3(which, x, y)
        hist = self.robot_move_elected.robot_move_result.hist
        self.grid_board.show_move_without_refresh(hist)

    def pygame_wait_for_exit(self):
        self.grid_board.wait_for_exit()

    def pygame_detect_stop_and_reset(self):
        return self.grid_board.detect_stop_and_reset()

    def get_line(self, A, B):
        if A[0] == B[0]:
            a = min(A[1], B[1])
            b = max(A[1], B[1])
            return [(A[0], y) for y in range(a, b + 1)]
        if A[1] == B[1]:
            a = min(A[0], B[0])
            b = max(A[0], B[0])
            return [(x, A[1]) for x in range(a, b + 1)]

class RobotsDistributed3X3Linear(RobotsDistributed3X3Base):
    def __init__(self, SIZE_COL, SIZE_ROW, POS_INPUT):
        RobotsDistributed3X3Base.__init__(self, SIZE_COL, SIZE_ROW, POS_INPUT)
        self.MODE                 = Mode.LINEAR
        self.obj_value_calculator = ObjectiveValueCalculatorLinear()

class RobotsDistributed3X3IOuputOneLine(RobotsDistributed3X3Base):
    def __init__(self, SIZE_COL, SIZE_ROW, POS_INPUT, WHERE_INPUT, WHERE_OUTPUT):
        RobotsDistributed3X3Base.__init__(self, SIZE_COL, SIZE_ROW, POS_INPUT)
        self.MODE              = Mode.INPUT_OUTPUT
        self.WHERE_INPUT       = (WHERE_INPUT[0]  + 2, WHERE_INPUT[1]  + 2)
        self.WHERE_OUTPUT      = (WHERE_OUTPUT[0] + 2, WHERE_OUTPUT[1] + 2)
        self.obj_value_calculator = ObjectiveValueCalculatorIOuput(self.WHERE_INPUT, self.WHERE_OUTPUT)

    def main_distributed(self):
        while not self.obj_value_calculator.is_finished(self.POS_BIGGER):
            print ""
            print ""
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            print self.MAT_REAL

    def update_mat_real(self):
        self.MAT_REAL = np.zeros((self.SIZE_COL, self.SIZE_ROW))
        value = -1
        for p in [self.WHERE_INPUT, self.WHERE_OUTPUT]:
            self.MAT_REAL[(p[0] - 2, p[1] - 2)] = value
            value -= 1
        for i, p in self.POS_BIGGER.iteritems():
            self.MAT_REAL[(p[0] - 2, p[1] - 2)] = i + 1

class RobotsDistributed3X3IOuputTwoLines(RobotsDistributed3X3IOuputOneLine):
    def __init__(self, SIZE_COL, SIZE_ROW, POS_INPUT, WHERE_INPUT, WHERE_OUTPUT):
        RobotsDistributed3X3IOuputOneLine.__init__(self, SIZE_COL,
                        SIZE_ROW, POS_INPUT, WHERE_INPUT, WHERE_OUTPUT)
        self.MODE = Mode.INPUT_OUTPUT_TWO_LINES
        dummy_calculator = ObjectiveValueCalculator()
        center = dummy_calculator.get_center(self.POS_BIGGER)
        p1 = self.WHERE_INPUT
        p2 = self.WHERE_OUTPUT
        self.orthogonalAnglePoint   = (p1[0], p2[1])
        if (p1[0] - center[0]) ** 2 + (p2[1] - center[1]) ** 2 > \
                                (p2[0] - center[0]) ** 2 + (p1[1] - center[1]) ** 2:
            self.orthogonalAnglePoint = (p2[0], p1[1])

        self.calculator_1 = ObjectiveValueCalculatorIOuput(
            self.WHERE_INPUT, self.orthogonalAnglePoint)

        self.precious = set(self.get_line(self.WHERE_INPUT, self.orthogonalAnglePoint))

        self.calculator_2 = ObjectiveValueCalculatorIOuputSecondLine(
            self.orthogonalAnglePoint, self.WHERE_OUTPUT, precious=self.precious)

    def main_distributed(self):
        self.obj_value_calculator = self.calculator_1
        while not self.obj_value_calculator.is_finished(self.POS_BIGGER):
            _stop, _reset = self.pygame_detect_stop_and_reset()
            if _stop:
                continue
            if _reset:
                return
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            self.pygame_draw()
        print "First line finished, now the second line"
        self.obj_value_calculator = self.calculator_2
        while not self.obj_value_calculator.is_finished(self.POS_BIGGER):
            _stop, _reset = self.pygame_detect_stop_and_reset()
            if _stop:
                continue
            if _reset:
                return
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            self.pygame_draw()
        self.grid_board.unset_local_3x3()

    def update_mat_real(self):
        self.MAT_REAL = np.zeros((self.SIZE_COL, self.SIZE_ROW))
        value = -1
        for p in [self.WHERE_INPUT, self.WHERE_OUTPUT, self.orthogonalAnglePoint]:
            self.MAT_REAL[(p[0] - 2, p[1] - 2)] = value
            value -= 1
        for i, p in self.POS_BIGGER.iteritems():
            self.MAT_REAL[(p[0] - 2, p[1] - 2)] = i + 1

class RobotsDistributed3X3IOuputFourLines(RobotsDistributed3X3IOuputOneLine):
    def __init__(self, SIZE_COL, SIZE_ROW, POS_INPUT, WHERE_INPUT, WHERE_OUTPUT):
        RobotsDistributed3X3IOuputOneLine.__init__(self, SIZE_COL,
                        SIZE_ROW, POS_INPUT, WHERE_INPUT, WHERE_OUTPUT)
        self.MODE = Mode.INPUT_OUTPUT_FOUR_LINES
        dummy_calculator = ObjectiveValueCalculator()
        center = dummy_calculator.get_center(self.POS_BIGGER)
        p1 = self.WHERE_INPUT
        p2 = self.WHERE_OUTPUT
        self.orthogonalAnglePoint_1 = (p1[0], p2[1])
        self.orthogonalAnglePoint_2 = (p2[0], p1[1])

        if (p1[0] - center[0]) ** 2 + (p2[1] - center[1]) ** 2 > \
                                (p2[0] - center[0]) ** 2 + (p1[1] - center[1]) ** 2:
            self.orthogonalAnglePoint_1 = (p2[0], p1[1])
            self.orthogonalAnglePoint_2 = (p1[0], p2[1])

        self.calculator_1 = ObjectiveValueCalculatorIOuput(
            self.WHERE_INPUT, self.orthogonalAnglePoint_1)

        self.precious = set(self.get_line(self.WHERE_INPUT, self.orthogonalAnglePoint_1))

        self.calculator_2 = ObjectiveValueCalculatorIOuputSecondLine(
            self.orthogonalAnglePoint_1, self.WHERE_OUTPUT, precious=self.precious)

        self.precious = set(list(self.precious) + self.get_line(self.orthogonalAnglePoint_1, self.WHERE_OUTPUT))

        self.calculator_3 = ObjectiveValueCalculatorIOuputSecondLine(
            self.WHERE_OUTPUT, self.orthogonalAnglePoint_2, precious=self.precious)

        self.precious = set(list(self.precious) + self.get_line(self.WHERE_OUTPUT, self.orthogonalAnglePoint_2))

        self.calculator_4 = ObjectiveValueCalculatorIOuputSecondLine(
            self.orthogonalAnglePoint_2, self.WHERE_INPUT, precious=self.precious)

    def main_distributed(self):
        self.obj_value_calculator = self.calculator_1
        while not self.obj_value_calculator.is_finished(self.POS_BIGGER):
            _stop, _reset = self.pygame_detect_stop_and_reset()
            if _stop:
                continue
            if _reset:
                return
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            self.pygame_draw()
        print "First line finished, now the second line"
        self.obj_value_calculator = self.calculator_2
        while not self.obj_value_calculator.is_finished(self.POS_BIGGER):
            _stop, _reset = self.pygame_detect_stop_and_reset()
            if _stop:
                continue
            if _reset:
                return
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            self.pygame_draw()
        print "Second line finished, now the third line"
        self.obj_value_calculator = self.calculator_3
        while not self.obj_value_calculator.is_finished(self.POS_BIGGER):
            _stop, _reset = self.pygame_detect_stop_and_reset()
            if _stop:
                continue
            if _reset:
                return
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            self.pygame_draw()
        print "Third line finished, now the forth line"
        self.obj_value_calculator = self.calculator_4
        while not self.obj_value_calculator.is_finished(self.POS_BIGGER):
            _stop, _reset = self.pygame_detect_stop_and_reset()
            if _stop:
                continue
            if _reset:
                return
            self.create_dict_robot_move()
            self.conduct_election_distributed()
            self.pygame_draw()
        self.grid_board.unset_local_3x3()
