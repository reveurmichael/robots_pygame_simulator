__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

import heapq
import robots_plot
import time
import os
import robots_utils as utils
from robots_direction import D
import robots_is_connected


class ModularRobots(object):
    def __init__(self, POS):
        self.POS           = POS
        self.hq            = []
        self.energy        = 0
        self.dict_diameter = {utils.get_diameter(self.POS): [self.POS]}
        self.result_dir    = "result_dir"
        self.hist_enabled  = True
        self.load0_enabled = True
        self.pull_enabled  = True
        self.push_enabled  = True
        self.carry_enabled = True
        self.must_be_connected    = False
        self.cmap                 = robots_plot.get_cmap(len(self.POS))

    def main_load_0(self):
        OBJECTIVE = len(self.POS) - 1
        flag_success = 0
        robots_plot.plot_matrix(self.POS, self.cmap)
        self.search_movable_load_0(self.POS, 0, 0, [])
        while self.hq:
            pop = heapq.heappop(self.hq)
            robots_plot.plot_matrix(pop[3], self.cmap)
            if -1 * pop[0] == OBJECTIVE:
                flag_success = 1
                break
            else:
                self.search_movable_load_0(pop[3], pop[1], pop[2], pop[4])
        if flag_success:
            robots_plot.plot_matrix(pop[3], self.cmap)

    def search_movable_load_0(self, pos, energy, step, hist):
        if not self.load0_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat, pos_relative = utils.pos_to_mat_0110(pos)
        for i in range(len(pos_relative)):
            (x, y) = pos_relative[i]
            if mat[(x - 1, y)] == 0:
                if (mat[(x - 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x - 1, y + 1)] and mat[(x, y + 1)]):
                    pos_next = pos[:i] + [(pos[i][0] - 1, pos[i][1])] + pos[i + 1:]
                    self.judge_and_heappush(pos_next, energy + 1, step + 1, hist + [(i, D.LEFT)])

            if mat[(x + 1, y)] == 0:
                if (mat[(x + 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x + 1, y + 1)] and mat[(x, y + 1)]):
                    pos_next = pos[:i] + [(pos[i][0] + 1, pos[i][1])] + pos[i + 1:]
                    self.judge_and_heappush(pos_next, energy + 1, step + 1, hist + [(i, D.RIGHT)])

            if mat[(x, y + 1)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y + 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y + 1)]):
                    pos_next = pos[:i] + [(pos[i][0], pos[i][1] + 1)] + pos[i + 1:]
                    self.judge_and_heappush(pos_next, energy + 1, step + 1, hist + [(i, D.UP)])

            if mat[(x, y - 1)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y - 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y - 1)]):
                    pos_next = pos[:i] + [(pos[i][0], pos[i][1] - 1)] + pos[i + 1:]
                    self.judge_and_heappush(pos_next, energy + 1, step + 1, hist + [(i, D.DOWN)])


    def judge_and_heappush(self, pos_next, energy, step, hist, plot=False):
        diameter = utils.get_diameter(pos_next)
        if self.must_be_connected:
            if not robots_is_connected.is_connected(pos_next):
                return
        hmap_diameter = self.dict_diameter.setdefault(diameter, [])
        flag = 0
        for elem in hmap_diameter:
            if utils.is_same_pos(elem, pos_next):
                flag = 1
                break
        if flag:
            return
        else:
            hmap_diameter.append(pos_next)
        heapq.heappush(self.hq, (-1 * diameter, energy, step, pos_next, hist))
        if plot:
            robots_plot.plot_matrix(pos_next, self.cmap)

    def main_load_1_pull_push_carry(self):
        self.result_dir = time.strftime("%Y%m%d_%H_%M_%S")
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        OBJECTIVE = len(self.POS) - 1
        flag_success = 0
        robots_plot.plot_matrix(self.POS, self.cmap)
        self.search_movable_load_0(self.POS, 0, 0, [])
        self.search_movable_load_1_pull(self.POS, 0, 0, [])
        self.search_movable_load_1_push(self.POS, 0, 0, [])
        self.search_movable_load_1_carry(self.POS, 0, 0, [])
        while self.hq:
            pop = heapq.heappop(self.hq)
            robots_plot.plot_matrix(pop[3], self.cmap)
            if -1 * pop[0] == OBJECTIVE:
                flag_success = 1
                break
            else:
                self.search_movable_load_0(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_pull(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_push(pop[3], pop[1], pop[2], pop[4])
                self.search_movable_load_1_carry(pop[3], pop[1], pop[2], pop[4])
        if flag_success:
            print "SUCESS. WAIT A MOMENT FOR PLOTTING"
            if self.hist_enabled:
                robots_plot.draw_and_save_hist_relative(self.POS, pop[4],
                   self.result_dir, self.cmap, file_extension=".png")
                robots_plot.draw_and_save_hist_fixed(self.POS, pop[4],
                    self.result_dir, self.cmap, file_extension=".png")
                print "PLOT FINISHED. CHECK THE DIRECTORY ", self.result_dir
            robots_plot.plot_matrix(pop[3], self.cmap)

    def search_movable_load_1_pull(self, pos, energy, step, hist):
        if not self.pull_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat, pos_relative = utils.pos_to_mat_0230(pos)
        for i in range(len(pos_relative)):
            (x, y) = pos_relative[i]
            if mat[(x - 1, y)] == 0:
                if (mat[(x - 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x - 1, y + 1)] and mat[(x, y + 1)]):
                    if mat[(x + 1, y)]:
                        pos_pull_0 = pos[:i] + [(pos[i][0] - 1, pos[i][1])] + pos[i + 1:]
                        k    = int(mat[(x + 1, y)]) - 1
                        pos_pull_1 = pos_pull_0[:k] + [(pos_pull_0[k][0] - 1, pos_pull_0[k][1])] + pos_pull_0[k + 1:]
                        self.judge_and_heappush(pos_pull_1, energy + 1, step + 1, hist + [(i, D.LEFT, k, D.LEFT)])

            if mat[(x + 1, y)] == 0:
                if (mat[(x + 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x + 1, y + 1)] and mat[(x, y + 1)]):
                    if mat[(x - 1, y)]:
                        pos_pull_0 = pos[:i] + [(pos[i][0] + 1, pos[i][1])] + pos[i + 1:]
                        k    = int(mat[(x - 1, y)]) - 1
                        pos_pull_1 = pos_pull_0[:k] + [(pos_pull_0[k][0] + 1, pos_pull_0[k][1])] + pos_pull_0[k + 1:]
                        self.judge_and_heappush(pos_pull_1, energy + 1, step + 1, hist + [(i, D.RIGHT, k, D.RIGHT)])

            if mat[(x, y + 1)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y + 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y + 1)]):
                    if mat[(x, y - 1)]:
                        pos_pull_0 = pos[:i] + [(pos[i][0], pos[i][1] + 1)] + pos[i + 1:]
                        k    = int(mat[(x, y - 1)]) - 1
                        pos_pull_1 = pos_pull_0[:k] + [(pos_pull_0[k][0], pos_pull_0[k][1] + 1)] + pos_pull_0[k + 1:]
                        self.judge_and_heappush(pos_pull_1, energy + 1, step + 1, hist + [(i, D.UP, k, D.UP)])

            if mat[(x, y - 1)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y - 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y - 1)]):
                    if mat[(x, y + 1)]:
                        pos_pull_0 = pos[:i] + [(pos[i][0], pos[i][1] - 1)] + pos[i + 1:]
                        k    = int(mat[(x, y + 1)]) - 1
                        pos_pull_1 = pos_pull_0[:k] + [(pos_pull_0[k][0], pos_pull_0[k][1] - 1)] + pos_pull_0[k + 1:]
                        self.judge_and_heappush(pos_pull_1, energy + 1, step + 1, hist + [(i, D.DOWN, k, D.DOWN)])

    def search_movable_load_1_push(self, pos, energy, step, hist):
        if not self.push_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat, pos_relative = utils.pos_to_mat_0230(pos)
        for i in range(len(pos_relative)):
            (x, y) = pos_relative[i]
            if mat[(x - 1, y)] and mat[(x - 2, y)] == 0:
                if (mat[(x - 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x - 1, y + 1)] and mat[(x, y + 1)]):
                    k = int(mat[(x - 1, y)]) - 1
                    pos_push_1 = pos[:k] + [(pos[k][0] - 1, pos[k][1])] + pos[k + 1:]
                    pos_push_0 = pos_push_1[:i] + [(pos_push_1[i][0] - 1, pos_push_1[i][1])] + pos_push_1[i + 1:]
                    self.judge_and_heappush(pos_push_0, energy + 1, step + 1, hist + [(i, D.LEFT, k, D.LEFT)])

            if mat[(x + 1, y)] and mat[(x + 2, y)] == 0:
                if (mat[(x + 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x + 1, y + 1)] and mat[(x, y + 1)]):
                    k = int(mat[(x + 1, y)]) - 1
                    pos_push_1 = pos[:k] + [(pos[k][0] + 1, pos[k][1])] + pos[k + 1:]
                    pos_push_0 = pos_push_1[:i] + [(pos_push_1[i][0] + 1, pos_push_1[i][1])] + pos_push_1[i + 1:]
                    self.judge_and_heappush(pos_push_0, energy + 1, step + 1, hist + [(i, D.RIGHT, k, D.RIGHT)])

            if mat[(x, y + 1)] and mat[(x, y + 2)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y + 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y + 1)]):
                    k = int(mat[(x, y + 1)]) - 1
                    pos_push_1 = pos[:k] + [(pos[k][0], pos[k][1] + 1)] + pos[k + 1:]
                    pos_push_0 = pos_push_1[:i] + [(pos_push_1[i][0], pos_push_1[i][1] + 1)] + pos_push_1[i + 1:]
                    self.judge_and_heappush(pos_push_0, energy + 1, step + 1, hist + [(i, D.UP, k, D.UP)])

            if mat[(x, y - 1)] and mat[(x, y - 2)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y - 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y - 1)]):
                    k = int(mat[(x, y - 1)]) - 1
                    pos_push_1 = pos[:k] + [(pos[k][0], pos[k][1] - 1)] + pos[k + 1:]
                    pos_push_0 = pos_push_1[:i] + [(pos_push_1[i][0], pos_push_1[i][1] - 1)] + pos_push_1[i + 1:]
                    self.judge_and_heappush(pos_push_0, energy + 1, step + 1, hist + [(i, D.DOWN, k, D.DOWN)])

    def search_movable_load_1_carry(self, pos, energy, step, hist):
        if not self.carry_enabled:
            return
        if not self.hist_enabled:
            hist = []
        mat, pos_relative = utils.pos_to_mat_0230(pos)
        for i in range(len(pos_relative)):
            (x, y) = pos_relative[i]
            if mat[(x - 1, y)] == 0:
                if (mat[(x - 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x - 1, y + 1)] and mat[(x, y + 1)]):
                    pos_carry_0 = pos[:i] + [(pos[i][0] - 1, pos[i][1])] + pos[i + 1:]
                    if mat[(x, y + 1)] != 0 and mat[(x - 1, y + 1)] == 0:
                        k = int(mat[(x, y + 1)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0] - 1, pos_carry_0[k][1])] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.LEFT, k, D.LEFT)])
                    elif mat[(x, y - 1)] != 0 and mat[(x - 1, y - 1)] == 0:
                        k = int(mat[(x, y - 1)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0] - 1, pos_carry_0[k][1])] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.LEFT, k, D.LEFT)])

            if mat[(x + 1, y)] == 0:
                if (mat[(x + 1, y - 1)] and mat[(x, y - 1)]) or (mat[(x + 1, y + 1)] and mat[(x, y + 1)]):
                    pos_carry_0 = pos[:i] + [(pos[i][0] + 1, pos[i][1])] + pos[i + 1:]
                    if mat[(x, y + 1)] != 0 and mat[(x + 1, y + 1)] == 0:
                        k = int(mat[(x, y + 1)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0] + 1, pos_carry_0[k][1])] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.RIGHT, k, D.RIGHT)])
                    elif mat[(x, y - 1)] != 0 and mat[(x + 1, y - 1)] == 0:
                        k = int(mat[(x, y - 1)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0] + 1, pos_carry_0[k][1])] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.RIGHT, k, D.RIGHT)])

            if mat[(x, y + 1)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y + 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y + 1)]):
                    pos_carry_0 = pos[:i] + [(pos[i][0], pos[i][1] + 1)] + pos[i + 1:]
                    if mat[(x - 1, y)] != 0 and mat[(x - 1, y + 1)] == 0:
                        k = int(mat[(x - 1, y)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0], pos_carry_0[k][1] + 1)] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.UP, k, D.UP)])
                    elif mat[(x + 1, y)] != 0 and mat[(x + 1, y + 1)] == 0:
                        k = int(mat[(x + 1, y)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0], pos_carry_0[k][1] + 1)] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.UP, k, D.UP)])

            if mat[(x, y - 1)] == 0:
                if (mat[(x - 1, y)] and mat[(x - 1, y - 1)]) or (mat[(x + 1, y)] and mat[(x + 1, y - 1)]):
                    pos_carry_0 = pos[:i] + [(pos[i][0], pos[i][1] - 1)] + pos[i + 1:]
                    if mat[(x - 1, y)] != 0 and mat[(x - 1, y - 1)] == 0:
                        k = int(mat[(x - 1, y)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0], pos_carry_0[k][1] - 1)] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.DOWN, k, D.DOWN)])
                    elif mat[(x + 1, y)] != 0 and mat[(x + 1, y - 1)] == 0:
                        k = int(mat[(x + 1, y)]) - 1
                        pos_carry_1 = pos_carry_0[:k] + \
                            [(pos_carry_0[k][0], pos_carry_0[k][1] - 1)] + pos_carry_0[k + 1:]
                        self.judge_and_heappush(pos_carry_1, energy + 1, step + 1, hist + [(i, D.DOWN, k, D.DOWN)])
