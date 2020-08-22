__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

import heapq
import time
import os
import robots_utils as utils
from robots_direction import D
import robots_is_connected
import robots_local_view_3x3
from robots_heapdict import *
import copy
from robots_mode import *


class RobotsMoveResult(object):
    def __init__(self, res_obj_func_value, res_step, res_pos, res_hist):
        self.obj_func_value    = res_obj_func_value
        self.step        = res_step
        self.pos         = res_pos
        self.hist        = res_hist

class RobotsLocalMove(object):
    def __init__(self, robot_view_3x3, robot_view_5x5, obj_value_calculator, hist_enabled, load0_enabled, pull_enabled,
                                       push_enabled, carry_enabled, must_be_connected):
        '''
        1. pos is now a dict, not a list anymore.
        2. It's possible to limit the search space (or len of set_of_traversed) to a certain threshold, e.g. 50, at each iteration. This can be quite good for 5 * 5.
        '''
        self.obj_value_calculator = obj_value_calculator

        self.robot_view     = None
        self.robot_view_3x3 = robot_view_3x3
        self.robot_view_5x5 = robot_view_5x5

        self.distant_dict   = {}
        self.hq             = []
        self.hist_enabled   = hist_enabled
        self.load0_enabled  = load0_enabled
        self.pull_enabled   = pull_enabled
        self.push_enabled   = push_enabled
        self.carry_enabled  = carry_enabled
        self.must_be_connected  = must_be_connected
        self.robot_move_result  = None
        self.result_mat_local   = None
        self.result_mat_global  = None
        self.already_traversed  = None
        self.count_already_popped     = 0

    def get_max_gain(self):
        res_obj_func_value = float('-inf')
        res_step     = 10000000
        res_pos      = {}
        res_hist     = []

        if self.robot_view_3x3:
            self.robot_view = self.robot_view_3x3
            self.already_traversed = set([utils.dict_to_tuple_no_key(self.robot_view.POS_LOCAL)])
            self.search_movable_load_0_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            self.search_movable_load_1_pull_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            self.search_movable_load_1_push_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            self.search_movable_load_1_carry_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            while self.hq:
                pop = heapq.heappop(self.hq)
                self.count_already_popped += 1
                if -1 * pop[0] > res_obj_func_value:
                    pos_global = copy.deepcopy(self.robot_view.POS_GLOBAL_BIGGER)
                    for i, p in pop[3].iteritems():
                        pos_global[i] = p
                    list_pos_global = utils.dict_to_list(pos_global)
                    if robots_is_connected.is_connected(list_pos_global):
                        res_obj_func_value = -1 * pop[0]
                        res_step     = pop[2]
                        res_pos      = pop[3]
                        res_hist     = pop[4]
                self.search_movable_load_0_3x3(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_pull_3x3(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_push_3x3(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_carry_3x3(pop[3], pop[1], pop[2], pop[4])

        if self.robot_view_5x5:
            self.count_already_popped = 0
            self.robot_view = self.robot_view_5x5
            self.already_traversed = set([utils.dict_to_tuple_no_key(self.robot_view.POS_LOCAL)])

            self.search_movable_load_0_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            self.search_movable_load_1_pull_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            self.search_movable_load_1_push_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            self.search_movable_load_1_carry_3x3(self.robot_view.POS_LOCAL, 0, 0, [])
            while self.hq:
                pop = heapq.heappop(self.hq)
                self.count_already_popped += 1
                if self.count_already_popped >= 20:
                    break
                if -1 * pop[0] > res_obj_func_value:
                    pos_global = copy.deepcopy(self.robot_view.POS_GLOBAL_BIGGER)
                    for i, p in pop[3].iteritems():
                        pos_global[i] = p
                    list_pos_global = utils.dict_to_list(pos_global)
                    if robots_is_connected.is_connected(list_pos_global):
                        res_obj_func_value = -1 * pop[0]
                        res_step = pop[2]
                        res_pos = pop[3]
                        res_hist = pop[4]
                self.search_movable_load_0_3x3(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_pull_3x3(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_push_3x3(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_carry_3x3(pop[3], pop[1], pop[2], pop[4])
        self.result_mat_local  = self.robot_view.get_robot_view_mat_from_new_pos(res_pos)
        self.result_mat_global = copy.deepcopy(self.robot_view.MAT_000_GLOBAL)
        POS_GLOBAL_BIGGER      = copy.deepcopy(self.robot_view.POS_GLOBAL_BIGGER)
        for i, p in res_pos.iteritems():
            POS_GLOBAL_BIGGER[i] = p
        for i, p in POS_GLOBAL_BIGGER.iteritems():
            self.result_mat_global[p] = i + 1
        self.robot_move_result = RobotsMoveResult(res_obj_func_value, res_step, res_pos, res_hist)
        return self.robot_move_result

    def judge_already_traversed(self, pos, step):
        pos_tuple = utils.dict_to_tuple_no_key(pos)
        if pos_tuple in self.already_traversed:
            return True
        else:
            self.already_traversed.add(pos_tuple)
            return False

    def judge_and_heappush_3x3(self, pos_next, energy, step, hist):
        if self.judge_already_traversed(pos_next, step):
            return
        pos_global = copy.deepcopy(self.robot_view.POS_GLOBAL_BIGGER)
        for i, p in pos_next.iteritems():
            pos_global[i] = p
        mat_000_global = copy.deepcopy(self.robot_view.MAT_000_GLOBAL)
        for i, p in pos_global.iteritems():
            mat_000_global[p] = i + 1

        list_pos_global = utils.dict_to_list(pos_global)
        obj_func_value  = self.obj_value_calculator.get_value(mat_000_global, pos_global)
        if self.must_be_connected:
            if not robots_is_connected.is_connected(list_pos_global):
                return
        heapq.heappush(self.hq, (-1 * obj_func_value, energy, step, pos_next, hist))

    def search_movable_load_0_3x3(self, pos, energy, step, hist):
        if not self.load0_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat = self.robot_view.get_robot_view_mat_from_new_pos(pos)
        for w, p in pos.iteritems():
            if not self.robot_view.is_within_moore_neighbour(p):
                continue
            (x, y) = p
            if mat[(x - 1, y)] == 0:
                if (mat[(x - 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x - 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[w] = (pos[w][0] - 1, pos[w][1])
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.LEFT)])

            if mat[(x + 1, y)] == 0:
                if (mat[(x + 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x + 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[w] = (pos[w][0] + 1, pos[w][1])
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.RIGHT)])

            if mat[(x, y + 1)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y + 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[w] = (pos[w][0], pos[w][1] + 1)
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.UP)])

            if mat[(x, y - 1)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y - 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y - 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[w] = (pos[w][0], pos[w][1] - 1)
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.DOWN)])

    def search_movable_load_1_pull_3x3(self, pos, energy, step, hist):
        if not self.pull_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat = self.robot_view.get_robot_view_mat_from_new_pos(pos)
        for w, p in pos.iteritems():
            if not self.robot_view.is_within_moore_neighbour(p):
                continue
            (x, y) = p
            if mat[(x - 1, y)] == 0:
                if (mat[(x - 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x - 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    if mat[(x + 1, y)] >= 1:
                        pos_next = copy.deepcopy(pos)
                        pos_next[w] = (pos[w][0] - 1, pos[w][1])
                        k    = int(mat[(x + 1, y)]) - 1
                        pos_next[k] = (pos[k][0] - 1, pos[k][1])
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.LEFT, k, D.LEFT)])

            if mat[(x + 1, y)] == 0:
                if (mat[(x + 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x + 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    if mat[(x - 1, y)] >= 1:
                        pos_next = copy.deepcopy(pos)
                        pos_next[w] = (pos[w][0] + 1, pos[w][1])
                        k    = int(mat[(x - 1, y)]) - 1
                        pos_next[k] = (pos[k][0] + 1, pos[k][1])
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.RIGHT, k, D.RIGHT)])

            if mat[(x, y + 1)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y + 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y + 1)] >= 1):
                    if mat[(x, y - 1)] >= 1:
                        pos_next = copy.deepcopy(pos)
                        pos_next[w] = (pos[w][0], pos[w][1] + 1)
                        k    = int(mat[(x, y - 1)]) - 1
                        pos_next[k] = (pos[k][0], pos[k][1] + 1)
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.UP, k, D.UP)])

            if mat[(x, y - 1)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y - 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y - 1)] >= 1):
                    if mat[(x, y + 1)] >= 1:
                        pos_next = copy.deepcopy(pos)
                        pos_next[w] = (pos[w][0], pos[w][1] - 1)
                        k    = int(mat[(x, y + 1)]) - 1
                        pos_next[k] = (pos[k][0], pos[k][1] - 1)
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.DOWN, k, D.DOWN)])

    def search_movable_load_1_push_3x3(self, pos, energy, step, hist):
        if not self.push_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat = self.robot_view.get_robot_view_mat_from_new_pos(pos)
        for w, p in pos.iteritems():
            if not self.robot_view.is_within_moore_neighbour(p):
                continue
            (x, y) = p
            if mat[(x - 1, y)] >= 1 and mat[(x - 2, y)] == 0:
                if (mat[(x - 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x - 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    k = int(mat[(x - 1, y)]) - 1
                    pos_next[k] = (pos[k][0] - 1, pos[k][1])
                    pos_next[w] = (pos[w][0] - 1, pos[w][1])
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.LEFT, k, D.LEFT)])

            if mat[(x + 1, y)] >= 1 and mat[(x + 2, y)] == 0:
                if (mat[(x + 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x + 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    k = int(mat[(x + 1, y)]) - 1
                    pos_next[k] = (pos[k][0] + 1, pos[k][1])
                    pos_next[w] = (pos[w][0] + 1, pos[w][1])
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.RIGHT, k, D.RIGHT)])

            if mat[(x, y + 1)] >= 1 and mat[(x, y + 2)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y + 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    k = int(mat[(x, y + 1)]) - 1
                    pos_next[k] = (pos[k][0], pos[k][1] + 1)
                    pos_next[w] = (pos[w][0], pos[w][1] + 1)
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.UP, k, D.UP)])

            if mat[(x, y - 1)] >= 1 and mat[(x, y - 2)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y - 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y - 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    k = int(mat[(x, y - 1)]) - 1
                    pos_next[k] = (pos[k][0], pos[k][1] - 1)
                    pos_next[w] = (pos[w][0], pos[w][1] - 1)
                    self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(w, D.DOWN, k, D.DOWN)])

    def search_movable_load_1_carry_3x3(self, pos, energy, step, hist):
        if not self.carry_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat = self.robot_view.get_robot_view_mat_from_new_pos(pos)
        for i, p in pos.iteritems():
            if not self.robot_view.is_within_moore_neighbour(p):
                continue
            (x, y) = p
            if mat[(x - 1, y)] == 0:
                if (mat[(x - 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x - 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[i] = (pos[i][0] - 1, pos[i][1])
                    if mat[(x, y + 1)] >= 1 and mat[(x - 1, y + 1)] == 0:
                        k = int(mat[(x, y + 1)]) - 1
                        pos_next[k] = (pos[k][0] - 1, pos[k][1])
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.LEFT, k, D.LEFT)])
                    elif mat[(x, y - 1)] >= 1 and mat[(x - 1, y - 1)] == 0:
                        k = int(mat[(x, y - 1)]) - 1
                        pos_next[k] = (pos[k][0] - 1, pos[k][1])
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.LEFT, k, D.LEFT)])

            if mat[(x + 1, y)] == 0:
                if (mat[(x + 1, y - 1)] >= 1 and mat[(x, y - 1)] >= 1) or (mat[(x + 1, y + 1)] >= 1 and mat[(x, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[i] = (pos[i][0] + 1, pos[i][1])
                    if mat[(x, y + 1)] >= 1 and mat[(x + 1, y + 1)] == 0:
                        k = int(mat[(x, y + 1)]) - 1
                        pos_next[k] = (pos[k][0] + 1, pos[k][1])
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.RIGHT, k, D.RIGHT)])
                    elif mat[(x, y - 1)] >= 1 and mat[(x + 1, y - 1)] == 0:
                        k = int(mat[(x, y - 1)]) - 1
                        pos_next[k] = (pos[k][0] + 1, pos[k][1])
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.RIGHT, k, D.RIGHT)])

            if mat[(x, y + 1)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y + 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y + 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[i] = (pos[i][0], pos[i][1] + 1)
                    if mat[(x - 1, y)] >= 1 and mat[(x - 1, y + 1)] == 0:
                        k = int(mat[(x - 1, y)]) - 1
                        pos_next[k] = (pos[k][0], pos[k][1] + 1)
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.UP, k, D.UP)])
                    elif mat[(x + 1, y)] >= 1 and mat[(x + 1, y + 1)] == 0:
                        k = int(mat[(x + 1, y)]) - 1
                        pos_next[k] = (pos[k][0], pos[k][1] + 1)
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.UP, k, D.UP)])

            if mat[(x, y - 1)] == 0:
                if (mat[(x - 1, y)] >= 1 and mat[(x - 1, y - 1)] >= 1) or (mat[(x + 1, y)] >= 1 and mat[(x + 1, y - 1)] >= 1):
                    pos_next = copy.deepcopy(pos)
                    pos_next[i] = (pos[i][0], pos[i][1] - 1)
                    if mat[(x - 1, y)] >= 1 and mat[(x - 1, y - 1)] == 0:
                        k = int(mat[(x - 1, y)]) - 1
                        pos_next[k] = (pos[k][0], pos[k][1] - 1)
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.DOWN, k, D.DOWN)])
                    elif mat[(x + 1, y)] >= 1 and mat[(x + 1, y - 1)] == 0:
                        k = int(mat[(x + 1, y)]) - 1
                        pos_next[k] = (pos[k][0], pos[k][1] - 1)
                        self.judge_and_heappush_3x3(pos_next, energy + 1, step + 1, hist + [(i, D.DOWN, k, D.DOWN)])
