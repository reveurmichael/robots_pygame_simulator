__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

import math

class ObjectiveValueCalculator(object):
    def __init__(self):
        self.result_value         = None

    def get_value(self, mat, list_pos):
        return 0

    def get_real_value(self, mat, list_pos):
        return 0

    def get_width(self, m):
        total = 0.0001
        for i in range(len(m)):
            line = m[i]
            x_min = 1000000
            x_max = -1000000
            for j in range(len(line)):
                if line[j] >= 1:
                    x_min = min(x_min, j)
                    x_max = max(x_max, j)
            w = max(0, x_max - x_min)
            total += w ** 2
        return math.sqrt(total) / len(m)

    def get_height_vertical(self, m):
        def traverse(m):
            x_min = 1000000
            x_max = -1000000
            for i in range(len(m)):
                line = m[i]
                for j in range(len(line)):
                    if line[j] >= 1:
                        x_min = min(x_min, j)
                        x_max = max(x_max, j)
            return max(0, x_max - x_min + 1)

        return traverse(m.T)

    def get_diameter_minus_width_3x3(self, mat):  # Max length of line
        a = self.get_diameter_3x3(mat)
        b = self.get_width(mat.T)
        return 1 * a - 1 * b

    def get_diameter_3x3(self, mat):  # Max length of line
        diameter = [0]

        def traverse(m):
            for i in range(len(m)):
                line = m[i]
                d = 0
                for j in range(len(line)):
                    if line[j] >= 1:
                        d += 1
                    else:
                        diameter[0] = max(diameter[0], d)
                        d = 0

        traverse(mat)
        # traverse(mat.T)  ### NORMALLY SHOULD NOT BE COMMENTED
        return diameter[0]

    def get_total_x_y_diff(self, where_input, where_output, where_mid, pos, power):
        total = 0
        for i, p in pos.iteritems():
            for q in [where_input, where_output, where_mid]:
                total += (abs(p[0] - q[0])) ** power
                total += (abs(p[1] - q[1])) ** power
        return total

    def get_total_distance_y(self, pos, input_output_x, power):
        total = 0
        for i, p in pos.iteritems():
            total += (abs(p[0] - input_output_x)) ** power
        return total

    def get_empty_number_rectangle(self, mat, pos):
        rectangle = self.get_height_vertical(mat) * self.get_height_vertical(mat.T)
        return abs(rectangle - len(pos))

    def get_empty_ratio_rectangle(self, mat, pos):
        rectangle = self.get_height_vertical(mat) * self.get_height_vertical(mat.T)
        return abs(len(pos) / (rectangle + 0.00001))

    def get_dist_from_mid(self, mid, pos):
        total_d = 0
        for i, p in pos.iteritems():
            dx = abs(p[0] - mid[0])
            dy = abs(p[1] - mid[1])
            total_d += dx ** 2 - dy ** 2
        return abs(total_d)

    def get_center(self, pos):
        center_x = 0
        center_y = 0
        for i, p in pos.iteritems():
            center_x += p[0]
            center_y += p[1]
        return (int(center_x / len(pos)), int(center_y / len(pos)))

    def calculate_precious(self, pos, precious, price=10000):
        total = 0
        for i, p in pos.iteritems():
            if p in precious:
                total += price
        return total

class ObjectiveValueCalculatorLinear(ObjectiveValueCalculator):
    def __init__(self):
        ObjectiveValueCalculator.__init__(self)

    def get_value(self, mat, pos):
        return self.get_diameter_minus_width_3x3(mat)

    def get_real_value(self, mat, pos):
        return self.get_diameter_3x3(mat)

class ObjectiveValueCalculatorIOuput(ObjectiveValueCalculator):
    def __init__(self, WHERE_INPUT, WHERE_OUTPUT):
        ObjectiveValueCalculator.__init__(self)
        self.WHERE_INPUT  = WHERE_INPUT
        self.WHERE_OUTPUT = WHERE_OUTPUT
        self.obj_line_set = set()
        p1 = self.WHERE_INPUT
        p2 = self.WHERE_OUTPUT
        self.MID = (int((p1[0] + p2[0]) / 2),
                     int((p1[1] + p2[1]) / 2))
        self.MID_occupied = False
        if p1[0] == p2[0]:
            self.obj_line_horizontal = True
            self.obj_line_set = set([(p1[0], py) for py in
                                     range(min(p1[1], p2[1]), max(p1[1], p2[1]) + 1)])
        elif p1[1] == p2[1]:
            self.obj_line_horizontal = False
            self.obj_line_set = set([(px, p1[1]) for px in
                                     range(min(p1[0], p2[0]), max(p1[0], p2[0]) + 1)])
        self.INPUT_occupied = False
        self.OUTPUT_occupied = False
        self.obj_value_calculator_vertical = None

    def get_value(self, mat, pos):
        if not self.obj_line_horizontal:
            return self.get_value_vertical(mat, pos)
        else:
            return self.get_value_horizontal(mat, pos)

    def get_value_vertical(self, mat, pos):
        where_input_T = (self.WHERE_INPUT[1], self.WHERE_INPUT[0])
        where_output_T = (self.WHERE_OUTPUT[1], self.WHERE_OUTPUT[0])
        pos_T = {}
        for i, p in pos.iteritems():
            pos_T[i] = (p[1], p[0])
        self.obj_value_calculator_vertical = ObjectiveValueCalculatorIOuput(
            where_input_T, where_output_T)
        self.result_value = \
            self.obj_value_calculator_vertical.get_value_horizontal(mat.T, pos_T)
        return self.result_value


    def get_x_y_diff(self, point, power_x, power_y, alpha, betta, gamma, pos):
        total = 0
        q = point
        for i, p in pos.iteritems():
            total += alpha * (abs(p[0] - q[0]) ** power_x)
            total += betta * (abs(p[1] - q[1]) ** power_y)
        return gamma * total

    def get_dist_from_point(self, point, power, gamma, pos):
        total = 0
        q = point
        for i, p in pos.iteritems():
            total += (abs(p[0] - q[0]) + abs(p[1] - q[1])) ** power
        return gamma * total

    def get_value_horizontal(self, mat, pos):
        return self.get_value_horizontal_helper(mat, pos)

    def get_value_horizontal_helper(self, mat, pos):
        self.result_value = 0
        [a, b] = sorted([self.WHERE_INPUT[1], self.WHERE_OUTPUT[1]])
        for i, p in pos.iteritems():
            if p[0] == self.WHERE_INPUT[0]:
                if self.WHERE_INPUT[1] <= p[1] <= self.WHERE_OUTPUT[1] \
                        or self.WHERE_OUTPUT[1] <= p[1] <= self.WHERE_INPUT[1]:
                    self.result_value += 10000000000
                if self.WHERE_INPUT[1] == p[1] or p[1] == self.WHERE_OUTPUT[1]:
                    self.result_value += 30000000000

        for i, p in pos.iteritems():
            self.result_value -=  abs(p[0] - self.WHERE_OUTPUT[0]) ** 3
            self.result_value -=  abs(abs(p[1] - self.WHERE_OUTPUT[1]) - 1) ** 2

        return self.result_value

    def get_value_horizontal_backup(self, mat, pos):
        self.MID_occupied = False
        self.INPUT_occupied = False
        self.OUTPUT_occupied = False
        for i, p in pos.iteritems():
            if (int(p[0]), int(p[1])) == self.MID:
                self.MID_occupied = True
            if (int(p[0]), int(p[1])) == self.WHERE_INPUT:
                self.INPUT_occupied = True
            if (int(p[0]), int(p[1])) == self.WHERE_OUTPUT:
                self.OUTPUT_occupied = True
        if not self.MID_occupied:
            self.result_value = self.approach_line_mid_point(mat, pos)
        else:
            self.result_value = self.get_overlap_with_obj_line(mat, pos)
        return self.result_value

    def get_real_value(self, mat, pos):
        return self.result_value

    def approach_line_mid_point(self, mat, pos):
        heigh_width_ratio = self.get_height_vertical(mat) / (self.get_height_vertical(mat.T) + 0.0001)
        flag = False
        if 0.6 <= self.get_empty_ratio_rectangle(mat, pos) and 0.5 <= heigh_width_ratio <= 2:
            flag = True
        if not flag:
            self.result_value = -1000000
            center = self.get_center(pos)
            self.result_value -= self.get_total_x_y_diff(center, center, center, pos, 2)
            self.result_value -= math.sqrt(self.get_total_distance_y(pos, self.WHERE_INPUT[0], 2))
        if flag:
            self.result_value = -100000
            self.result_value -= math.sqrt(self.get_total_x_y_diff(  
                self.WHERE_INPUT, self.WHERE_OUTPUT, self.MID, pos, 3))
            self.result_value += self.get_diameter_minus_width_3x3(mat)
            self.result_value -= self.get_height_vertical(mat)
            self.result_value -= math.sqrt(self.get_total_distance_y(pos, self.WHERE_INPUT[0], 2))
            self.result_value -= math.sqrt(self.get_empty_number_rectangle(mat, pos))
        return self.result_value

    def get_overlap_with_obj_line(self, mat, pos):
        alpha, betta = 0.5, 0.5
        overlap = 0
        for i, p in pos.iteritems():
            if p in self.obj_line_set:
                overlap += 1 + alpha * (abs(p[0] - self.MID[0]) + abs(p[1] - self.MID[1]))
        width = self.get_width(mat)
        height = math.sqrt(math.sqrt(self.get_height_vertical(mat)))
        dist_from_mid = 0
        x_y_diff = math.sqrt(abs(betta * self.get_total_x_y_diff(
                    self.WHERE_INPUT, self.WHERE_OUTPUT, self.MID, pos, 1)))
        if self.get_height_vertical(mat) <= 3:
            x_y_diff = -10000
            if self.INPUT_occupied:
                dist_from_mid = math.sqrt(math.sqrt(self.get_dist_from_mid(
                    self.WHERE_INPUT, pos)))
            elif self.OUTPUT_occupied:
                dist_from_mid = math.sqrt(math.sqrt(self.get_dist_from_mid(
                    self.WHERE_OUTPUT, pos)))
            else:
                dist_from_mid = math.sqrt(math.sqrt(self.get_dist_from_mid(
                    self.MID, pos)))

        return overlap + dist_from_mid - width - height - x_y_diff  ## MAXIMIZE

    def is_finished(self, pos):
        size = len(self.obj_line_set)
        for i, p in pos.iteritems():
            if p in self.obj_line_set:
                size -= 1
        return size == 0


class ObjectiveValueCalculatorIOuputSecondLine(ObjectiveValueCalculatorIOuput):
    def __init__(self, WHERE_INPUT, WHERE_OUTPUT, precious=set()):
        ObjectiveValueCalculatorIOuput.__init__(self, WHERE_INPUT, WHERE_OUTPUT)
        self.precious = precious

    def exclude_precious_mat(self, m):
        for p in self.precious:
            m[p] = 0

    def exclude_precious_pos(self, pos):
        for p in self.precious:
            if p in pos:
                del pos[p]

    def get_value_vertical(self, mat, pos):
        where_input_T = (self.WHERE_INPUT[1], self.WHERE_INPUT[0])
        where_output_T = (self.WHERE_OUTPUT[1], self.WHERE_OUTPUT[0])
        precious_T = set()
        pos_T = {}
        for i, p in pos.iteritems():
            pos_T[i] = (p[1], p[0])
        for p in self.precious:
            precious_T.add((p[1], p[0]))
        self.obj_value_calculator_vertical = ObjectiveValueCalculatorIOuputSecondLine(
            where_input_T, where_output_T, precious=precious_T)
        self.result_value = \
            self.obj_value_calculator_vertical.get_value_horizontal(mat.T, pos_T)
        return self.result_value

    def get_value_horizontal(self, mat, pos):
        total_precious_price = self.calculate_precious(pos, self.precious, price=50000000000)
        self.exclude_precious_mat(mat)
        self.exclude_precious_pos(pos)
        self.result_value = self.get_value_horizontal_helper(mat, pos)
        self.result_value += total_precious_price
        return self.result_value

