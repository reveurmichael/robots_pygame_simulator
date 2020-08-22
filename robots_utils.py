__author__ = "lunde chen"
__email__  = "lundechen@shu.edu.cn"

import numpy as np
import math

def is_same_pos_and_same_direction(pos1, pos2):
    return True

def is_same_pos(pos1, pos2):
    mat1, _min1, _max1 = pos_to_mat_1001(pos1)
    mat2, _min2, _max2 = pos_to_mat_1001(pos2)
    if _min1 != _min2 or _max1 != _max2:
        return False
    if np.array_equal(mat1, mat2) or np.array_equal(mat1, mat2.T):
        return True
    if np.array_equal(mat1, np.flipud(mat2)) or np.array_equal(mat1, np.fliplr(mat2)):
        return True
    if np.array_equal(mat1, np.flipud(mat2.T)) or np.array_equal(mat1, np.fliplr(mat2.T)):
        return True
    if np.array_equal(mat1, np.flipud(np.fliplr(mat2.T))) or np.array_equal(mat1.T, np.flipud(np.fliplr(mat2.T))):
        return True
    if np.array_equal(mat1.T, np.flipud(mat2)) or np.array_equal(mat1.T, np.fliplr(mat2)):
        return True
    if np.array_equal(mat1.T, np.flipud(mat2.T)) or np.array_equal(mat1.T, np.fliplr(mat2.T)):
        return True
    return False


def has_at_least_one_neighbor(mat, pos_relative):
    for p in pos_relative:
        (x, y) = p
        if mat[(x + 1, y)] + mat[(x - 1, y)] + mat[(x, y + 1)] + mat[(x, y - 1)] == 0:
            return False
    return True

def get_diameter(pos):  # Max length of line
    diameter = [0]

    def traverse(m):
        for i in range(len(m)):
            line = m[i]
            d = 0
            for j in range(len(line)):
                if line[j] != 0:
                    d += 1
                else:
                    diameter[0] = max(diameter[0], d)
                    d = 0

    mat, pos_relative = pos_to_mat_0110(pos)
    traverse(mat)
    #traverse(mat.T)  ### NORMALLY SHOULD NOT BE COMMENTED
    return diameter[0]

def pos_to_mat_0110(pos):
    NUM_ROBOTS = len(pos)
    min_x = 10000000
    max_x = -1
    min_y = 10000000
    max_y = -1
    for p in pos:
        min_x = min(p[0], min_x)
        max_x = max(p[0], max_x)
        min_y = min(p[1], min_y)
        max_y = max(p[1], max_y)
    NUM_GRID = max(max_x - min_x, max_y - min_y) + 3
    mat = np.zeros((NUM_GRID, NUM_GRID))
    pos_relative = []
    for i in range(NUM_ROBOTS):
        (x, y) = pos[i]
        mat[(x - min_x + 1, y - min_y + 1)] = 1
        pos_relative.append((x - min_x + 1, y - min_y + 1))
    return mat, pos_relative

def pos_to_mat_0230(pos):
    NUM_ROBOTS = len(pos)
    min_x = 10000000
    max_x = -1
    min_y = 10000000
    max_y = -1
    for p in pos:
        min_x = min(p[0], min_x)
        max_x = max(p[0], max_x)
        min_y = min(p[1], min_y)
        max_y = max(p[1], max_y)
    NUM_GRID = max(max_x - min_x, max_y - min_y) + 3
    mat = np.zeros((NUM_GRID, NUM_GRID))
    pos_relative = []
    for i in range(NUM_ROBOTS):
        (x, y) = pos[i]
        mat[(x - min_x + 1, y - min_y + 1)] = (i + 1)
        pos_relative.append((x - min_x + 1, y - min_y + 1))
    return mat, pos_relative

def pos_to_mat_1001(pos):
    NUM_ROBOTS = len(pos)
    min_x = 10000000
    max_x = -1
    min_y = 10000000
    max_y = -1
    for p in pos:
        min_x = min(p[0], min_x)
        max_x = max(p[0], max_x)
        min_y = min(p[1], min_y)
        max_y = max(p[1], max_y)
    NUM_X = max_x - min_x + 1
    NUM_Y = max_y - min_y + 1
    mat = np.zeros((NUM_X, NUM_Y))
    for i in range(NUM_ROBOTS):
        (x, y) = pos[i]
        mat[(x - min_x, y - min_y)] = 1
    return mat, min(NUM_X, NUM_Y), max(NUM_X, NUM_Y)

def list_to_tuple(list_a):
    return tuple(list_a)

def tuple_to_list(tuple_a):
    return list(tuple_a)

def dict_to_tuple_no_key(dict_a):
    list_a = [v for k, v in dict_a.iteritems()]
    return tuple(sorted(list_a))

def dict_to_list(dict_a):
    list_a = [None for _ in range(len(dict_a))]
    for k, v in dict_a.iteritems():
        list_a[int(k)] = v
    return sorted(list_a)

def tuple_to_dict(tuple_a):
    pass
