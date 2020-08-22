__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

import numpy as np
import copy

class RobotLocalView(object):
    def __init__(self, MAT_GLOBAL_BIGGER, POS_GLOBAL_BIGGER, which, SIZE_COL, SIZE_ROW, occupy_empty_5x5_enabled, move_5x5_allowed):
        self.move_5x5_allowed = move_5x5_allowed
        self.occupy_empty_5x5_enabled = occupy_empty_5x5_enabled or self.move_5x5_allowed
        (self.X, self.Y) = POS_GLOBAL_BIGGER[which]
        self.which = which
        self.VALUE    = MAT_GLOBAL_BIGGER[(self.X, self.Y)]
        self.POS_GLOBAL_BIGGER = POS_GLOBAL_BIGGER
        self.MAT_GLOBAL_BIGGER = MAT_GLOBAL_BIGGER
        self.MAT_LOCAL, self.MAT_000_LOCAL, self.MAT_000_GLOBAL, self.POS_LOCAL = self.get_robot_local_view(MAT_GLOBAL_BIGGER, SIZE_COL, SIZE_ROW)

    def get_robot_local_view(self, MAT_GLOBAL_BIGGER, SIZE_COL, SIZE_ROW):
        mat_local = np.zeros((SIZE_COL + 4, SIZE_ROW + 4))
        mat_000_local   = np.zeros((SIZE_COL + 4, SIZE_ROW + 4))
        mat_000_global  = np.zeros((SIZE_COL + 4, SIZE_ROW + 4))
        pos_local  = {}
        mat_local.fill(-1)
        mat_000_local.fill(-1)
        a = self.X - 2
        b = self.X + 2
        c = self.Y - 2
        d = self.Y + 2
        for i in range(a + 1, b):
            for j in range(c + 1, d):
                mat_local[i][j] = MAT_GLOBAL_BIGGER[i][j]
                if MAT_GLOBAL_BIGGER[i][j] >= 0:
                    mat_000_local[i][j] = 0
                if mat_local[i][j] >= 1:
                    pos_local[mat_local[i][j] - 1] = (i, j)
        if self.occupy_empty_5x5_enabled:
            for i in [a, b]:
                for j in range(c, d + 1):
                    if MAT_GLOBAL_BIGGER[i][j] == 0:
                        mat_local[i][j] = 0
                        mat_000_local[i][j] = 0
            for j in [c, d]:
                for i in range(a, b + 1):
                    if MAT_GLOBAL_BIGGER[i][j] == 0:
                        mat_local[i][j] = 0
                        mat_000_local[i][j] = 0
        if self.move_5x5_allowed:
            for i in [a, b]:
                for j in range(c, d + 1):
                    if MAT_GLOBAL_BIGGER[i][j] >= 1:
                        mat_000_local[i][j] = 0
                        mat_local[i][j] = MAT_GLOBAL_BIGGER[i][j]
                        pos_local[mat_local[i][j] - 1] = (i, j)
            for j in [c, d]:
                for i in range(a, b + 1):
                    if MAT_GLOBAL_BIGGER[i][j] >= 1:
                        mat_000_local[i][j] = 0
                        mat_local[i][j] = MAT_GLOBAL_BIGGER[i][j]
                        pos_local[mat_local[i][j] - 1] = (i, j)
        return mat_local, mat_000_local, mat_000_global, pos_local

    def get_robot_view_mat_from_new_pos(self, new_pos):
        mat = copy.deepcopy(self.MAT_000_LOCAL)
        for key, value in new_pos.iteritems():
            mat[value] = key + 1
        return mat

    def is_within_moore_neighbour(self, another_p):
        moore_dist = 1
        if self.move_5x5_allowed:
            moore_dist = 2
        if -1 * moore_dist <= another_p[0] - self.X <= moore_dist \
                and -1 * moore_dist <= another_p[1] - self.Y <= moore_dist:
            return True
        return False
